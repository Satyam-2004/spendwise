from sqlalchemy.orm import Session
from app.models.transaction import Category, TransactionType

DEFAULT_CATEGORIES = [
    # Income
    {"name": "Salary", "type": TransactionType.INCOME, "icon": "💼"},
    {"name": "Freelance", "type": TransactionType.INCOME, "icon": "💻"},
    {"name": "Investment", "type": TransactionType.INCOME, "icon": "📈"},
    {"name": "Other Income", "type": TransactionType.INCOME, "icon": "💰"},
    # Expense
    {"name": "Food & Dining", "type": TransactionType.EXPENSE, "icon": "🍔"},
    {"name": "Transportation", "type": TransactionType.EXPENSE, "icon": "🚗"},
    {"name": "Shopping", "type": TransactionType.EXPENSE, "icon": "🛍️"},
    {"name": "Bills & Utilities", "type": TransactionType.EXPENSE, "icon": "🧾"},
    {"name": "Rent", "type": TransactionType.EXPENSE, "icon": "🏠"},
    {"name": "Entertainment", "type": TransactionType.EXPENSE, "icon": "🎬"},
    {"name": "Healthcare", "type": TransactionType.EXPENSE, "icon": "🏥"},
    {"name": "Education", "type": TransactionType.EXPENSE, "icon": "📚"},
    {"name": "Travel", "type": TransactionType.EXPENSE, "icon": "✈️"},
    {"name": "Personal Care", "type": TransactionType.EXPENSE, "icon": "💅"},
    {"name": "Other Expense", "type": TransactionType.EXPENSE, "icon": "📦"},
]


def create_default_categories(db: Session, user_id: int) -> None:
    """Create a standard set of categories for a new user."""
    for cat in DEFAULT_CATEGORIES:
        db.add(
            Category(
                name=cat["name"],
                type=cat["type"],
                icon=cat["icon"],
                user_id=user_id,
            )
        )
    db.commit()
