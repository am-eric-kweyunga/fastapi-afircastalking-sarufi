import phonenumbers
from src.utils.platenummbers import PlateNumberValidator
from random import SystemRandom
from typing import Literal

class Utilities:
    def __init__(self):
        pass

    def validate_phone_number(self, phone_number: str) -> str:
        """
        Validate a phone number
        """
        valid_phone_number = phonenumbers.is_valid_number(
            phonenumbers.parse(phone_number, "TZ")
        )
        if not valid_phone_number:
            raise ValueError("Invalid phone number")

        new_phone_number = phonenumbers.format_number(
            phonenumbers.parse(phone_number, "TZ"),
            phonenumbers.PhoneNumberFormat.E164,
        )
        return new_phone_number

    def buttons_list(self, _id: str, title: str):
        return {"type": "reply", "reply": {"id": f"{_id}", "title": title}}


    def response_buttons(self, text: str, buttons: list):
        # generating the buttons
        _buttons: list = [self.buttons_list(button["id"], button["title"]) for button in buttons]

        response: dict = {
            "send_reply_button": {
                "type": "button",
                "body": {"text": f"{text}"},
                "action": {
                    "buttons": _buttons,
                },
            }
        }

        return response


    def build_menu(self, body: str, footer: str, header_text: str, button: str, title: str, rows: list):
        return {
            "send_button": {
                "body": body,
                "action": {
                    "button": button,
                    "sections": [
                        {
                            "title": title,
                            "rows": rows,
                        }
                    ],
                },
                "header": header_text,
                "footer": footer
            }
        }