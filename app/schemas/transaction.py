from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionType


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: TransactionType
    icon: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: TransactionType
    icon: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: TransactionType
    description: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None
    category_id: Optional[int] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[TransactionType] = None
    description: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    transaction_date: Optional[datetime] = None
    category_id: Optional[int] = None


class TransactionResponse(BaseModel):
    id: int
    amount: float
    type: TransactionType
    description: Optional[str]
    notes: Optional[str]
    transaction_date: datetime
    category_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionWithCategory(TransactionResponse):
    category: Optional[CategoryResponse] = None
