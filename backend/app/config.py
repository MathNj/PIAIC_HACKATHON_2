"""
Application configuration management.

Loads environment variables using Pydantic V2.
All sensitive configuration (DATABASE_URL, secrets) must be in environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Force load .env file from backend directory, override any system environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set in:
    - .env file in backend/ directory
    - System environment variables
    - Docker/deployment environment
    """

    # Database configuration
    DATABASE_URL: str

    # Authentication secrets
    BETTER_AUTH_SECRET: str

    # Application settings
    APP_NAME: str = "TODO API"
    DEBUG: bool = False

    # CORS settings (frontend URL)
    FRONTEND_URL: str = "http://localhost:3000"

    # OpenAI API Key (Phase III)
    OPENAI_API_KEY: str = ""

    # Gemini API Key (Phase III - AI Agent)
    GEMINI_API_KEY: str = ""

    # Pydantic V2 Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


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