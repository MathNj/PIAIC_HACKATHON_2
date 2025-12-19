"""
Pydantic schemas for User API requests and responses.

Schemas:
- UserCreate: Registration input (email, name, password)
- UserResponse: User data output (excludes password)
- UserLogin: Login credentials input
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "password": "SecurePass123"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    )


class UserResponse(BaseModel):
    """Schema for user data in API responses (excludes password)."""
    id: str = Field(..., description="Unique user ID (UUID)")
    email: str = Field(..., description="User's email address")
    name: str = Field(..., description="User's display name")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode for SQLModel compatibility (Pydantic v2)
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2025-12-06T10:00:00Z"
            }
        }
    )
