"""
Application configuration management.

Loads environment variables using Pydantic Settings.
All sensitive configuration (DATABASE_URL, secrets) must be in environment variables.
"""

from pydantic_settings import BaseSettings


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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


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
    print(f"  - Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"  - Frontend URL: {settings.FRONTEND_URL}")
    print(f"  - Debug mode: {settings.DEBUG}")
