"""
Tag SQLModel for task categorization.

User-scoped tags for flexible multi-dimensional task organization.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from pydantic import ConfigDict, field_validator


class Tag(SQLModel, table=True):
    """
    Tag model for task categorization.

    Attributes:
        id: Unique auto-incrementing identifier
        name: Tag name (lowercase, trimmed, unique, max 30 chars)
        created_at: Tag creation timestamp

    Validation:
        - Tag names normalized to lowercase
        - Whitespace trimmed
        - Empty strings rejected
        - Maximum length: 30 characters
    """

    __tablename__ = "tags"

    # Primary key (auto-incrementing)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False,
        description="Unique tag identifier"
    )

    # Tag name (unique, lowercase, trimmed)
    name: str = Field(
        nullable=False,
        max_length=30,
        unique=True,
        index=True,
        description="Tag name (lowercase, max 30 characters)"
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Tag creation timestamp (UTC)"
    )

    @field_validator('name')
    @classmethod
    def normalize_tag_name(cls, v: str) -> str:
        """
        Normalize tag name to lowercase and trim whitespace.

        Args:
            v: Raw tag name

        Returns:
            Normalized tag name

        Raises:
            ValueError: If tag name is empty after trimming
        """
        normalized = v.strip().lower()
        if not normalized:
            raise ValueError("Tag name cannot be empty")
        if len(normalized) > 30:
            raise ValueError("Tag name cannot exceed 30 characters")
        return normalized

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "work",
                "created_at": "2025-12-11T12:00:00Z"
            }
        }
    )
