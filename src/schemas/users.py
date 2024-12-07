from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

from src.schemas.orders import (
    OrderBase,
    OrderStatus,
    PaymentBase,
    PaymentStatus,
)


class UserBase(SQLModel):
    phone_number: Optional[str] = Field(max_length=13)
    plate_number: Optional[str] = Field(max_length=10)


class UserVerify(UserBase):
    otp: str


class VerificationsBase(SQLModel):
    otp: Optional[str] = None
    phone_number: Optional[str] = Field(max_length=13)
    is_verified: bool = False
    is_active: bool = True
    created_at: Optional[str] = Field(default=datetime.now().isoformat())
    updated_at: Optional[str] = Field(default=datetime.now().isoformat())


class Order(OrderBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: float = Field(default=0.0)  # Total amount in KES

    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Relationships
    user: "User" = Relationship(back_populates="orders")
    payment: Optional["Payment"] = Relationship(back_populates="order")

    class Config:
        from_attributes = True
        orm_mode = True


class Payment(PaymentBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    order_id: UUID = Field(foreign_key="order.id")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    payment_date: Optional[str] = Field(
        default=None
    )  # Will be set when payment is completed
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Relationships
    order: Order = Relationship(back_populates="payment")

    class Config:
        from_attributes = True
        orm_mode = True


class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    otp: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[str] = Field(default=datetime.now().isoformat())
    updated_at: Optional[str] = Field(default=datetime.now().isoformat())

    # Relationship to Verifications
    verifications: List["Verifications"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    orders: list[Order] = Relationship(back_populates="user")

    class Config:
        from_attributes = True
        orm_mode = True


class Verifications(VerificationsBase, table=True):
    user_id: UUID = Field(foreign_key="user.id")
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    # Relationship to User
    user: User = Relationship(back_populates="verifications")

    class Config:
        from_attributes = True
        orm_mode = True
