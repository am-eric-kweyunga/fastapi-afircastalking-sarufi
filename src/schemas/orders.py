from typing import Optional
from sqlmodel import Field, SQLModel
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class OrderBase(SQLModel):
    volume: float = Field(gt=0)  # Volume in liters


class PaymentBase(SQLModel):
    amount: float = Field(gt=0)
    payment_method: str = Field(max_length=50)  # e.g., "mpesa", "card", etc.
    transaction_ref: Optional[str] = Field(default=None)  # External payment reference
