"""
Application configuration management.

Loads environment variables using Pydantic V2.
All sensitive configuration (DATABASE_URL, secrets) must be in environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file for local development, but never override system environment variables
# This ensures Vercel's environment variables are used in production
load_dotenv(override=False)


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
    # Required for AI chat functionality
    GEMINI_API_KEY: Optional[str] = None

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