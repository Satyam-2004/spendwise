from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.database import get_db
from app.models.user import User
from app.models.transaction import Transaction, Category, TransactionType
from app.core.deps import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/analytics", tags=["Analytics"])


class SummaryResponse(BaseModel):
    total_income: float
    total_expense: float
    net_savings: float
    savings_rate: float
    transaction_count: int


class CategoryBreakdown(BaseModel):
    category_id: Optional[int]
    category_name: str
    total_amount: float
    percentage: float
    transaction_count: int


class MonthlyTrend(BaseModel):
    year: int
    month: int
    income: float
    expense: float
    net: float


@router.get("/summary", response_model=SummaryResponse)
def get_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    income = (
        query.filter(Transaction.type == TransactionType.INCOME)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0.0))
        .scalar()
    )
    expense = (
        query.filter(Transaction.type == TransactionType.EXPENSE)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0.0))
        .scalar()
    )
    count = query.count()

    net = income - expense
    savings_rate = (net / income * 100) if income > 0 else 0.0

    return SummaryResponse(
        total_income=round(income, 2),
        total_expense=round(expense, 2),
        net_savings=round(net, 2),
        savings_rate=round(savings_rate, 2),
        transaction_count=count,
    )


@router.get("/by-category", response_model=List[CategoryBreakdown])
def get_category_breakdown(
    type: TransactionType = TransactionType.EXPENSE,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(
            Category.id,
            Category.name,
            func.sum(Transaction.amount).label("total"),
            func.count(Transaction.id).label("count"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == type,
        )
        .group_by(Category.id, Category.name)
    )

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    results = query.all()
    grand_total = sum(r.total for r in results) or 1.0

    return [
        CategoryBreakdown(
            category_id=r.id,
            category_name=r.name,
            total_amount=round(r.total, 2),
            percentage=round((r.total / grand_total) * 100, 2),
            transaction_count=r.count,
        )
        for r in results
    ]


@router.get("/monthly-trend", response_model=List[MonthlyTrend])
def get_monthly_trend(
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start = datetime.utcnow() - timedelta(days=months * 31)

    rows = (
        db.query(
            extract("year", Transaction.transaction_date).label("year"),
            extract("month", Transaction.transaction_date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start,
        )
        .group_by("year", "month", Transaction.type)
        .all()
    )

    # Aggregate into dict
    data = {}
    for r in rows:
        key = (int(r.year), int(r.month))
        if key not in data:
            data[key] = {"income": 0.0, "expense": 0.0}
        if r.type == TransactionType.INCOME:
            data[key]["income"] = r.total
        else:
            data[key]["expense"] = r.total

    result = []
    for (year, month), vals in sorted(data.items()):
        result.append(
            MonthlyTrend(
                year=year,
                month=month,
                income=round(vals["income"], 2),
                expense=round(vals["expense"], 2),
                net=round(vals["income"] - vals["expense"], 2),
            )
        )
    return result
