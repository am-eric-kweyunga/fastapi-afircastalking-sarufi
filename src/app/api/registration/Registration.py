import logging
import pyotp
from datetime import datetime, timedelta
from sqlmodel import Session, select
from typing import Dict, Any
from uuid import UUID

from src.schemas.users import User, UserBase, Verifications
from src.tasks.Tasks import Tasks
from src.utils.platenummbers import PlateNumberValidator
from src.utils.utililities import Utilities


class Registration:
    def __init__(self):
        self.utilities = Utilities()
        self.otp_expiry_minutes = 10  # OTP valid for 10 minutes

    def _create_verification(
        self, session: Session, user_id: UUID, phone_number: str, otp: str
    ) -> Verifications:
        """Create a new verification record"""
        verification = Verifications(
            user_id=user_id,
            phone_number=phone_number,
            otp=otp,
            is_active=True,
            is_verified=False,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        session.add(verification)
        session.commit()
        session.refresh(verification)
        return verification

    def register_user(self, data: dict, session: Session) -> Dict[str, Any]:
        """Register a new user and send OTP"""
        phone_number = data.get("phone_number")
        plate_number = data.get("plate_number")

        if not phone_number:
            raise ValueError("Phone number is required")

        valid_phone_number = self.utilities.validate_phone_number(phone_number)

        # Check if the user already exists
        user = session.exec(
            select(User).where(User.phone_number == valid_phone_number)
        ).first()

        if user:
            return {"message": "User already exists"}

        # Save the user to the database
        new_user = User(
            phone_number=valid_phone_number,
            plate_number=plate_number,
            is_verified=False,
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        if new_user:
            # Generate an OTP
            totp = pyotp.TOTP("base32secret3232")
            otp = totp.now()

            # Create verification record
            verification = self._create_verification(
                session=session,
                user_id=new_user.id,
                phone_number=valid_phone_number,
                otp=otp,
            )

            if verification:
                # Send the OTP to the user's phone number
                try:
                    task = Tasks(session=session)
                    send_sms = task.send_sms(
                        phone_number=valid_phone_number,
                        message=f"Hakiki OTP: {otp}",
                        user_id=new_user.id,
                    )
                except Exception as e:
                    print(e)
                    send_sms = False

                if send_sms:
                    return {
                        "message": "User registered successfully",
                        "user_id": str(new_user.id),
                    }

        return {"message": "Failed to register user"}

    def verify_otp(
        self, phone_number: str, otp: str, session: Session
    ):
        """Verify OTP for user registration"""

        # debug
        print("phone_number", phone_number)
        print("otp", otp)

        # use logging instead of print
        logging.info(f"phone_number: {phone_number}")
        logging.info(f"otp: {otp}")
        
        if not phone_number or not otp:
            raise ValueError("Phone number and OTP are required")

        valid_phone_number = self.utilities.validate_phone_number(phone_number)

        # Get the latest verification record for this phone number
        verification = session.exec(
            select(Verifications)
            .where(
                Verifications.phone_number == valid_phone_number,
                Verifications.is_active == True,
                Verifications.is_verified == False,
            )
            .order_by(Verifications.created_at.desc())
        ).first()

        if not verification:
            return {"message": "No verification found"}

        # Check if OTP has expired (10 minutes)
        created_at = datetime.fromisoformat(verification.created_at)
        if datetime.now() - created_at > timedelta(minutes=self.otp_expiry_minutes):
            verification.is_active = False
            session.commit()
            return {"message": "OTP has expired"}

        # Verify OTP
        if verification.otp != otp:
            return {"message": "Invalid OTP"}

        try:
            # Update user verification status
            user = session.exec(
                select(User).where(User.id == verification.user_id)
            ).first()
            if user:
                user.is_verified = True
                user.updated_at = datetime.now().isoformat()

                # Delete the verification record
                session.delete(verification)

                # Commit all changes in a single transaction
                session.commit()

                return {"message": "Verification successful"}
            else:
                return {"message": "User not found"}

        except Exception as e:
            session.rollback()
            return {"message": "Verification failed"}

    def resend_otp(self, phone_number: str, session: Session) -> Dict[str, Any]:
        """Resend OTP to user"""
        if not phone_number:
            raise ValueError("Phone number is required")

        valid_phone_number = self.utilities.validate_phone_number(phone_number)

        # Get the user
        user = session.exec(
            select(User).where(User.phone_number == valid_phone_number)
        ).first()

        if not user:
            return {"message": "User not found"}

        # Generate new OTP
        totp = pyotp.TOTP("base32secret3232")
        new_otp = totp.now()

        # Deactivate old verifications
        old_verifications = session.exec(
            select(Verifications).where(
                Verifications.phone_number == valid_phone_number,
                Verifications.is_active == True,
            )
        ).all()

        for verification in old_verifications:
            verification.is_active = False
            verification.updated_at = datetime.now().isoformat()

        # Create new verification
        verification = self._create_verification(
            session=session,
            user_id=user.id,
            phone_number=valid_phone_number,
            otp=new_otp,
        )

        # Send new OTP
        try:
            task = Tasks(session=session)
            send_sms = task.send_sms(
                phone_number=valid_phone_number,
                message=f"Hakiki OTP: {new_otp}",
                user_id=user.id,
            )
        except Exception as e:
            print(e)
            send_sms = False

        if send_sms:
            return {"message": "OTP resent successfully"}

        return {"message": "Failed to resend OTP"}
