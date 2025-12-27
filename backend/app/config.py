"""
Application configuration management.

Reads environment variables directly using os.environ.
All sensitive configuration (DATABASE_URL, secrets) must be in environment variables.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file for local development only
# Don't override system environment variables (Vercel uses system env vars)
# Get the directory where this file is located (backend/app/)
BASE_DIR = Path(__file__).resolve().parent.parent  # Go up to backend/
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path, override=False)
print(f"[DEBUG] Looking for .env at: {dotenv_path}")
print(f"[DEBUG] .env exists: {dotenv_path.exists()}")


class Settings:
    """
    Application settings loaded from environment variables.

    Uses direct os.environ.get() instead of Pydantic for maximum compatibility
    with Vercel and other deployment platforms.
    """

    def __init__(self):
        # Database configuration (required)
        self.DATABASE_URL = os.environ.get("DATABASE_URL", "")

        # Authentication secrets (required)
        self.BETTER_AUTH_SECRET = os.environ.get("BETTER_AUTH_SECRET", "")

        # Application settings
        self.APP_NAME = os.environ.get("APP_NAME", "TODO API")
        self.DEBUG = os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes")

        # CORS settings (frontend URL)
        self.FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

        # OpenAI API Key (Phase III)
        self.OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

        # Gemini API Key (Phase III - AI Agent)
        self.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

        # SMTP Configuration (Email Notifications)
        self.SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
        self.SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "")
        self.SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "TODO App Notifications")
        self.EMAIL_NOTIFICATIONS_ENABLED = os.environ.get(
            "EMAIL_NOTIFICATIONS_ENABLED", "true"
        ).lower() in ("true", "1", "yes")

        # Debug logging for Vercel deployments
        if os.environ.get("VERCEL") or "vercel" in os.environ.get("VERCEL_URL", "").lower():
            print(f"[CONFIG] Running on Vercel", file=sys.stderr)
            print(f"[CONFIG] DATABASE_URL: {'SET' if self.DATABASE_URL else 'MISSING'}", file=sys.stderr)
            print(f"[CONFIG] GEMINI_API_KEY: {'SET' if self.GEMINI_API_KEY else 'MISSING'}", file=sys.stderr)
            print(f"[CONFIG] BETTER_AUTH_SECRET: {'SET' if self.BETTER_AUTH_SECRET else 'MISSING'}", file=sys.stderr)


# Global settings instance
settings = Settings()


# Validate critical settings at startup
def validate_settings() -> None:
    """Validate that all critical settings are present and valid."""
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    if not settings.BETTER_AUTH_SECRET:
        raise ValueError("BETTER_AUTH_SECRET environment variable is required")

    if len(settings.BETTER_AUTH_SECRET) < 32:
        raise ValueError("BETTER_AUTH_SECRET must be at least 32 characters")

    print(f"[OK] Configuration loaded successfully")
    # Safe printing of database URL (hiding credentials)
    db_host = "configured"
    if '@' in settings.DATABASE_URL:
        db_host = settings.DATABASE_URL.split('@')[1]

    print(f"  - Database: {db_host}")
    print(f"  - Frontend URL: {settings.FRONTEND_URL}")
    print(f"  - Debug mode: {settings.DEBUG}")

    # Debug: Print OpenAI configuration
    import os
    openai_key = os.getenv("OPENAI_API_KEY", "")
    openai_base = os.getenv("OPENAI_BASE_URL", "")
    openai_model = os.getenv("OPENAI_MODEL", "")
    print(f"  - OpenAI API Key: {'SET (len=' + str(len(openai_key)) + ')' if openai_key else 'NOT SET'}")
    print(f"  - OpenAI Base URL: {openai_base if openai_base else 'NOT SET (using default)'}")
    print(f"  - OpenAI Model: {openai_model if openai_model else 'NOT SET (using default)'}")

    # Email notification configuration
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        print(f"  - Email Notifications: ENABLED")
        print(f"  - SMTP Server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
        print(f"  - SMTP From: {settings.SMTP_FROM_EMAIL}")
        if not settings.SMTP_USERNAME:
            print(f"  - WARNING: SMTP_USERNAME not set - emails will fail")
        if not settings.SMTP_PASSWORD:
            print(f"  - WARNING: SMTP_PASSWORD not set - emails will fail")
    else:
        print(f"  - Email Notifications: DISABLED")