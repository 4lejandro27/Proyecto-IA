"""Configuración central del sistema."""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App
    app_name: str = os.getenv("APP_NAME", "ServiceBot")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", "8000"))

    # WhatsApp
    whatsapp_token: str = os.getenv("WHATSAPP_TOKEN", "")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    whatsapp_verify_token: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "webhook_verify_123")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Google Sheets
    google_sheets_credentials_path: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "./credentials.json")
    google_sheet_name: str = os.getenv("GOOGLE_SHEET_NAME", "LeadsServicios")

    # Telegram
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # Email
    email_from: str = os.getenv("EMAIL_FROM", "")
    email_to: str = os.getenv("EMAIL_TO", "")
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.resend.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_pass: str = os.getenv("SMTP_PASS", "")

    class Config:
        env_file = ".env"

settings = Settings()
