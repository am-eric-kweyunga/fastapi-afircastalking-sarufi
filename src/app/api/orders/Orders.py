from datetime import datetime
from sqlmodel import Session, select
from typing import Dict, Any
from uuid import UUID
from src.utils.utililities import Utilities
from src.config.settings import settings
from src.schemas.users import Order, Payment, User
from src.schemas.orders import OrderBase


class OrderService:
    def __init__(self, session: Session):
        self.session = session
        self.gas_price_per_liter = settings.PRICE_PER_LITER
        self.utilities = Utilities()

    def calculate_total_amount(self, volume: float) -> float:
        """Calculate total amount based on volume"""
        return volume * self.gas_price_per_liter

    def create_order(self, user_id: str, order_data: dict) -> Dict[str, Any]:
        """Create a new order and initialize payment"""

        valid_phone_number = self.utilities.validate_phone_number(user_id)
        
        # Check if user exists
        user = self.session.exec(select(User).where(User.phone_number == valid_phone_number)).first()

        if not user:
            return {"message": "User not found"}

        try:
            # Create order
            total_amount = self.calculate_total_amount(order_data.get("volume"))

            order = Order(
                user_id=user_id,
                volume=order_data.get("volume"),
                notes=order_data.get("notes"),
                total_amount=total_amount,
            )

            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)

            # Initialize payment
            payment = Payment(
                order_id=order.id,
                amount=total_amount,
                payment_method="mobile",
            )

            self.session.add(payment)
            self.session.commit()

            return {
                "message": "Order created successfully",
                "order_id": str(order.id),
                "payment_id": str(payment.id),
                "total_amount": total_amount,
            }

        except Exception as e:
            self.session.rollback()
            return {"message": f"Failed to create order: {str(e)}"}

    def get_order(self, order_id: UUID) -> Dict[str, Any]:
        """Get order details"""
        order = self.session.exec(select(Order).where(Order.id == order_id)).first()

        if not order:
            return {"message": "Order not found"}

        return {
            "order_id": str(order.id),
            "user_id": str(order.user_id),
            "volume": order.volume,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at,
            "payment_status": order.payment.status if order.payment else "No payment",
        }
