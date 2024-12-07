import logging
import json
import requests
from typing import Optional, Dict, Any
from sqlmodel import Session, select

from src.config.settings import settings
from src.schemas.sms import SMSMessageResponseData
from src.schemas.users import User

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

sms_url = "https://api.africastalking.com/version1/messaging/bulk"


class Tasks:
    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    def _validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format
        """
        cleaned_number = phone_number.strip().replace(" ", "")
        if not cleaned_number:
            self.logger.error(f"Invalid phone number: {phone_number}")
            return False
        return True

    def _make_api_request(
        self, url: str, headers: Dict[str, str], data: Dict[str, Any]
    ) -> Optional[requests.Response]:
        """
        Make API request with error handling and logging
        """
        try:
            self.logger.debug(f"Making API request to {url}")
            self.logger.debug(f"Request data: {json.dumps(data, indent=2)}")

            response = requests.post(url=url, headers=headers, json=data)

            self.logger.debug(f"Response status code: {response.status_code}")
            self.logger.debug(f"Response content: {response.text}")

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            return None

    def _update_user_verification(self, user_id: str) -> bool:
        """
        Update user verification status
        """
        try:
            user = self.session.exec(select(User).where(User.id == user_id)).first()
            if not user:
                self.logger.error(f"User not found with ID: {user_id}")
                return False

            user.is_verified = True
            self.session.commit()
            self.session.refresh(user)
            self.logger.info(
                f"Successfully updated verification status for user: {user_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to update user verification: {str(e)}")
            return False

    def send_sms(self, phone_number: str, message: str, user_id: str) -> bool:
        """
        Send an SMS to a phone number with enhanced error handling and logging
        """
        self.logger.info(f"Attempting to send SMS to {phone_number}")

        # Validate inputs
        if not self._validate_phone_number(phone_number):
            return False

        if not message.strip():
            self.logger.error("Empty message provided")
            return False

        # Prepare message body
        message_body = {
            "username": settings.AFRICASTALKING_USERNAME,
            "message": message,
            "senderId": settings.SENDER_ID,
            "phoneNumbers": [phone_number.replace("+", "")],
        }

        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "apiKey": settings.AFRICASTALKING_API_KEY,
            "Accept": "application/json",
        }

        try:
            # Make API request
            response = self._make_api_request(sms_url, headers, message_body)
            if not response:
                return False

            # Parse response
            response = response.json()
            response_data = response.get("SMSMessageData", {})

            self.logger.debug(
                f"Parsed response data: {json.dumps(response_data, indent=2)}"
            )

            # Check response structure
            if "Recipients" not in response_data:
                self.logger.error("Invalid response structure: 'Recipients' not found")
                return False

            recipient = response_data["Recipients"][0]
            if (
                recipient.get("statusCode") == 101
                and recipient.get("status") == "Success"
            ):
                self.logger.info(f"Successfully sent SMS to {phone_number}")
                return True
            else:
                self.logger.error(
                    f"SMS sending failed with status: {recipient.get('status')}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Unexpected error in send_sms: {str(e)}", exc_info=True)
            return False

    def make_payment(self, amount: float):
        """
        Make a payment
        """
        pass

    async def verify_otp(self, user_id: str, otp: str) -> bool:
        """
        Verify OTP
        """
        try:
            user = self.session.exec(select(User).where(User.id == user_id)).first()
            if not user:
                self.logger.error(f"User not found with ID: {user_id}")
                return False
            if not user.is_verified:
                # Update user verification
                if self._update_user_verification(user_id):
                    self.logger.info(f"User verified successfully: {user_id}")
                    return True
                else:
                    self.logger.error("Failed to update user verification status")
                    return False
        except Exception as e:
            self.logger.error(f"Failed to verify OTP: {str(e)}")
            return False
