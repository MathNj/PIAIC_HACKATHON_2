"""
Tag Pydantic schemas for API request/response.

Defines schemas for tag CRUD operations.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TagCreate(BaseModel):
    """
    Tag creation schema for POST requests.

    Attributes:
        name: Tag name (will be normalized to lowercase, max 30 chars)
    """

    name: str = Field(
        min_length=1,
        max_length=30,
        description="Tag name (will be normalized to lowercase)"
    )

    @field_validator('name')
    @classmethod
    def normalize_tag_name(cls, v: str) -> str:
        """Normalize tag name to lowercase and trim whitespace."""
        normalized = v.strip().lower()
        if not normalized:
            raise ValueError("Tag name cannot be empty")
        if len(normalized) > 30:
            raise ValueError("Tag name cannot exceed 30 characters")
        return normalized

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "work"
            }
        }
    )


class TagRead(BaseModel):
    """
    Tag read schema for API responses.

    Attributes:
        id: Unique tag identifier
        name: Tag name (lowercase)
        created_at: Tag creation timestamp
    """

    id: int = Field(description="Unique tag identifier")
    name: str = Field(description="Tag name (lowercase)")
    created_at: datetime = Field(description="Tag creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "work",
                "created_at": "2025-12-11T12:00:00Z"
            }
        }
    )


class TagList(BaseModel):
    """
    List of tags response schema.

    Attributes:
        tags: List of tag objects
    """

    tags: list[TagRead] = Field(description="List of tags")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tags": [
                    {"id": 1, "name": "work", "created_at": "2025-12-11T12:00:00Z"},
                    {"id": 2, "name": "personal", "created_at": "2025-12-11T12:05:00Z"}
                ]
            }
        }
    )


class TagUpdate(BaseModel):
    """
    Tag update schema for PUT requests.

    Attributes:
        name: New tag name (will be normalized to lowercase)
    """

    name: str = Field(
        min_length=1,
        max_length=30,
        description="New tag name (will be normalized to lowercase)"
    )

    @field_validator('name')
    @classmethod
    def normalize_tag_name(cls, v: str) -> str:
        """Normalize tag name to lowercase and trim whitespace."""
        normalized = v.strip().lower()
        if not normalized:
            raise ValueError("Tag name cannot be empty")
        if len(normalized) > 30:
            raise ValueError("Tag name cannot exceed 30 characters")
        return normalized

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "urgent"
            }
        }
    )
