from fastapi import APIRouter, Depends
from fastapi import status, HTTPException
from sqlmodel import Session

from src.app.api.orders.Orders import OrderService
from src.database.db_config import get_db
from src.schemas.orders import OrderBase

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(
    data: dict,
    session: Session = Depends(get_db),
):

    user_id = data.get("user_id")
    volume = data.get("volume")
    notes = data.get("notes")

    order_service = OrderService(session=session)
    # Process the order data and create the order
    order = order_service.create_order(
        user_id=user_id,
        order_data={
            "volume": volume,
            "notes": notes,
        },
    )

    # You can use the OrderService to handle the order creation
    # and payment processing
    return {"message": "Order created successfully"}
