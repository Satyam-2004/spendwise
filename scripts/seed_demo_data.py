"""
Seed demo data for screenshots and testing.
Usage (with API running):
    python scripts/seed_demo_data.py
"""

import requests
from datetime import datetime, timedelta
import random

API = "http://localhost:8000"

EMAIL = "demo@spendwise.app"
PASSWORD = "demo1234"
NAME = "Demo User"


def main():
    # Register
    r = requests.post(f"{API}/api/auth/register", json={
        "email": EMAIL,
        "full_name": NAME,
        "password": PASSWORD,
    })
    if r.status_code not in (201, 400):
        print("Register failed:", r.text)
        return

    # Login
    r = requests.post(f"{API}/api/auth/login", data={
        "username": EMAIL,
        "password": PASSWORD,
    })
    if r.status_code != 200:
        print("Login failed:", r.text)
        return

    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in as", EMAIL)

    # Get categories
    cats = requests.get(f"{API}/api/transactions/categories", headers=headers).json()
    cat_map = {c["name"]: c["id"] for c in cats}
    print(f"✅ Found {len(cats)} categories")

    # Sample transactions
    samples = [
        ("Salary", "income", 55000, "Monthly salary"),
        ("Freelance", "income", 12000, "Upwork project payment"),
        ("Food & Dining", "expense", 450, "Swiggy - Dinner"),
        ("Food & Dining", "expense", 280, "Zomato - Lunch"),
        ("Transportation", "expense", 180, "Uber to office"),
        ("Transportation", "expense", 95, "Metro card recharge"),
        ("Shopping", "expense", 2499, "Amazon - Headphones"),
        ("Bills & Utilities", "expense", 899, "Jio Fiber bill"),
        ("Bills & Utilities", "expense", 350, "Electricity bill"),
        ("Rent", "expense", 18000, "Monthly house rent"),
        ("Entertainment", "expense", 649, "Netflix + Spotify"),
        ("Healthcare", "expense", 1200, "Apollo Pharmacy"),
        ("Education", "expense", 3999, "Udemy course"),
        ("Travel", "expense", 4500, "Flight tickets"),
        ("Personal Care", "expense", 799, "Haircut + grooming"),
        ("Food & Dining", "expense", 620, "Weekend dinner"),
        ("Shopping", "expense", 1899, "Myntra - Shoes"),
        ("Transportation", "expense", 220, "Ola airport drop"),
        ("Food & Dining", "expense", 150, "Coffee and snacks"),
        ("Other Expense", "expense", 500, "Miscellaneous"),
    ]

    base = datetime.utcnow()
    created = 0
    for i, (cat_name, tx_type, amount, desc) in enumerate(samples):
        tx_date = base - timedelta(days=random.randint(0, 60))
        payload = {
            "amount": amount,
            "type": tx_type,
            "description": desc,
            "transaction_date": tx_date.isoformat(),
            "category_id": cat_map.get(cat_name),
        }
        r = requests.post(f"{API}/api/transactions/", headers=headers, json=payload)
        if r.status_code == 201:
            created += 1

    print(f"✅ Created {created} demo transactions")
    print("\nDemo credentials:")
    print(f"  Email   : {EMAIL}")
    print(f"  Password: {PASSWORD}")
    print("\nOpen http://localhost:8000/docs or run: streamlit run dashboard.py")


if __name__ == "__main__":
    main()
