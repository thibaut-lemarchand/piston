import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
    PORT = int(os.getenv("PORT", 5000))

    if EMAIL_ADDRESS is None:
        raise ValueError(
            "EMAIL_ADDRESS is not set. Please set it in your environment or .env file."
        )
    if EMAIL_PASSWORD is None:
        raise ValueError(
            "EMAIL_PASSWORD is not set. Please set it in your environment or .env file."
        )
    if RECIPIENT_EMAIL is None:
        raise ValueError(
            "RECIPIENT_EMAIL is not set. Please set it in your environment or .env file."
        )
