import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.transaction import Transaction, Category, TransactionType
from app.models.user import User

# Simple keyword → category mapping for auto-categorization
CATEGORY_KEYWORDS = {
    "Food & Dining": ["swiggy", "zomato", "restaurant", "cafe", "food", "dining", "mcdonald", "kfc", "dominos", "pizza"],
    "Transportation": ["uber", "ola", "rapido", "metro", "petrol", "fuel", "parking", "taxi", "bus", "train"],
    "Shopping": ["amazon", "flipkart", "myntra", "ajio", "shopping", "mall", "store"],
    "Bills & Utilities": ["electricity", "water", "gas", "internet", "broadband", "mobile", "recharge", "airtel", "jio", "vi"],
    "Rent": ["rent", "landlord", "housing"],
    "Entertainment": ["netflix", "spotify", "prime", "hotstar", "movie", "cinema", "game"],
    "Healthcare": ["hospital", "pharmacy", "medicine", "doctor", "clinic", "apollo"],
    "Education": ["course", "udemy", "coursera", "school", "college", "tuition", "book"],
    "Travel": ["flight", "hotel", "makemytrip", "goibibo", "irctc", "booking"],
    "Salary": ["salary", "payroll", "wage"],
    "Freelance": ["freelance", "upwork", "fiverr", "client"],
}


def detect_category(description: str, categories: List[Category]):
    """Try to match transaction description to a category using keywords."""
    if not description:
        return None
    desc_lower = description.lower()

    name_to_id = {c.name: c.id for c in categories}

    for cat_name, keywords in CATEGORY_KEYWORDS.items():
        if cat_name in name_to_id:
            for kw in keywords:
                if kw in desc_lower:
                    return name_to_id[cat_name]
    return None


def parse_csv_content(content: str) -> List[Dict[str, Any]]:
    """
    Parse CSV with flexible column names.
    Expected columns (case-insensitive): date, amount, description/narration, type (optional)
    """
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        raise ValueError("CSV has no headers")

    # Normalize headers
    header_map = {}
    for h in reader.fieldnames:
        h_lower = h.strip().lower()
        if h_lower in ("date", "transaction_date", "txn_date", "value_date"):
            header_map["date"] = h
        elif h_lower in ("amount", "txn_amount", "value"):
            header_map["amount"] = h
        elif h_lower in ("description", "narration", "remarks", "particulars", "details"):
            header_map["description"] = h
        elif h_lower in ("type", "txn_type", "credit_debit", "dr_cr"):
            header_map["type"] = h

    if "amount" not in header_map:
        raise ValueError("CSV must contain an 'amount' column")

    rows = []
    for i, row in enumerate(reader, start=2):
        try:
            amount_str = row[header_map["amount"]].strip().replace(",", "")
            amount = abs(float(amount_str))

            # Determine type
            tx_type = TransactionType.EXPENSE
            if "type" in header_map:
                t = row[header_map["type"]].strip().lower()
                if t in ("income", "credit", "cr", "c"):
                    tx_type = TransactionType.INCOME
                elif t in ("expense", "debit", "dr", "d"):
                    tx_type = TransactionType.EXPENSE
            else:
                # Heuristic: negative amount → expense (already abs'd)
                raw = row[header_map["amount"]].strip().replace(",", "")
                if raw.startswith("-"):
                    tx_type = TransactionType.EXPENSE
                else:
                    # Default to expense for bank exports unless clearly income keywords
                    desc = row.get(header_map.get("description", ""), "").lower()
                    if any(k in desc for k in ["salary", "credit", "refund", "interest"]):
                        tx_type = TransactionType.INCOME

            # Date
            tx_date = datetime.utcnow()
            if "date" in header_map:
                date_str = row[header_map["date"]].strip()
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%d %b %Y", "%d-%b-%Y"):
                    try:
                        tx_date = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue

            description = ""
            if "description" in header_map:
                description = row[header_map["description"]].strip()[:255]

            rows.append({
                "amount": amount,
                "type": tx_type,
                "description": description,
                "transaction_date": tx_date,
            })
        except Exception as e:
            raise ValueError(f"Error parsing row {i}: {e}")

    return rows


def import_transactions_from_csv(
    db: Session,
    user: User,
    csv_content: str,
) -> Dict[str, Any]:
    """Parse CSV and create transactions with auto-categorization."""
    parsed = parse_csv_content(csv_content)
    categories = db.query(Category).filter(Category.user_id == user.id).all()

    created = 0
    for row in parsed:
        cat_id = detect_category(row["description"], categories)
        tx = Transaction(
            amount=row["amount"],
            type=row["type"],
            description=row["description"],
            transaction_date=row["transaction_date"],
            user_id=user.id,
            category_id=cat_id,
        )
        db.add(tx)
        created += 1

    db.commit()
    return {"imported": created, "message": f"Successfully imported {created} transactions"}
