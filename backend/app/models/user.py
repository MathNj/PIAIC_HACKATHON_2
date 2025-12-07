"""
User SQLModel for authentication and task ownership.

Represents a registered user account with email-based authentication.
Each user has a unique email and can own multiple tasks.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User model for multi-user TODO application.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (unique, used for login)
        name: User's display name
        password_hash: Hashed password (bcrypt)
        created_at: Account creation timestamp

    Relations:
        tasks: One-to-many relationship with Task model
    """

    __tablename__ = "users"

    # Primary key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )

    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=255,
        description="User's email address (must be unique)"
    )

    password_hash: str = Field(
        nullable=False,
        description="Bcrypt hashed password"
    )

    # Profile fields
    name: str = Field(
        nullable=False,
        max_length=100,
        description="User's display name"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp (UTC)"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2025-12-06T12:00:00Z"
            }
        }
