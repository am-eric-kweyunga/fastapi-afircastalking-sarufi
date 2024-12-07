from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Dict, Any
from pydantic import BaseModel

from src.app.api.registration.Registration import Registration
from src.database.db_config import get_db
from src.schemas.users import User, UserBase
from src.utils.utililities import Utilities


# Request models
class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str


class ResendOTPRequest(BaseModel):
    phone_number: str


# Initialize router
router = APIRouter(
    prefix="/registration",
    tags=["registration"],
)

registration = Registration()
utils = Utilities()


@router.post("/check_user", status_code=status.HTTP_200_OK)
async def check_user(data: dict, session: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Check if a user with the given phone number exists
    """
    print(data)

    phone_number = data.get("chat_id")

    try:
        user = session.exec(
            select(User).where(User.phone_number == phone_number)
        ).first()
        if user:
            return {"text": "continue"}
        else:
            return utils.response_buttons(
                text=f"Seems like your not registered, please register",
                buttons=[
                    {"id": "register", "title": "Register"},
                    {"id": "cancel", "title": "Cancel"},
                ],
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check user",
        )


@router.post("/r", status_code=status.HTTP_201_CREATED)
async def register_user(
    data: dict, session: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register a new user and send initial OTP
    """
    print(data)

    phone_number = data.get("phone_number")
    plate_number = data.get("plate_number")

    try:
        response = registration.register_user(
            data={"phone_number": phone_number, "plate_number": plate_number},
            session=session,
        )
        if response.get("message") == "User already exists":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone number already exists",
            )
        return
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_otp(data: dict, session: Session = Depends(get_db)):
    """
    Verify OTP for user registration
    """
    print(data)

    try:
        response = registration.verify_otp(
            phone_number=data.get("phone_number"),
            otp=data.get("verify_otp"),
            session=session,
        )

        if response.get("message") == "No verification found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active verification found for this phone number",
            )
        elif response.get("message") == "OTP has expired":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP has expired. Please request a new one",
            )
        elif response.get("message") == "Invalid OTP":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP provided"
            )

        return utils.response_buttons(
            text=f"Your account is verified!",
            buttons=[
                {"id": "filling_station", "title": "Continue"},
                {"id": "cancel", "title": "Cancel"},
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify OTP",
        )


@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(
    resend_data: ResendOTPRequest, session: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Resend OTP to user's phone number
    """
    try:
        response = registration.resend_otp(
            phone_number=resend_data.phone_number, session=session
        )

        if response.get("message") == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user found with this phone number",
            )

        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend OTP",
        )


@router.get("/status/{phone_number}", status_code=status.HTTP_200_OK)
async def check_registration_status(
    phone_number: str, session: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Check registration status for a phone number
    """
    try:
        user = session.exec(
            select(User).where(User.phone_number == phone_number)
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "is_registered": True,
            "is_verified": user.is_verified,
            "user_id": str(user.id),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check registration status",
        )
