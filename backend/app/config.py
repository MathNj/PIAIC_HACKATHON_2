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
load_dotenv(override=False)


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