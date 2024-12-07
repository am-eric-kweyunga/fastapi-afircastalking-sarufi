import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Union, Optional
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    NAME: str = "Filling Station API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./station.db"

    AFRICASTALKING_API_KEY: str = os.getenv("AFRICASTALKING_API_KEY", "")
    AFRICASTALKING_USERNAME: str = os.getenv("AFRICASTALKING_USERNAME", "")
    SENDER_ID: str = os.getenv("SENDER_ID", "")

    PRICE_PER_LITER: float = 2075.0


settings = Settings()
