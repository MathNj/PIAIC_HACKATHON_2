"""
Task Pydantic schemas for API validation.

Defines request/response models for task endpoints.
Separates database models from API contracts for flexibility.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal


class TaskBase(BaseModel):
    """Base schema with common task fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority_id: Optional[int] = Field(None, description="Priority ID (1=High, 2=Medium, 3=Low)")
    due_date: Optional[datetime] = Field(None, description="Optional due date for the task")
    is_recurring: bool = Field(False, description="Whether task regenerates on completion")
    recurrence_pattern: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = Field(
        None, description="Recurrence frequency"
    )
    tag_ids: list[int] = Field(default_factory=list, description="List of tag IDs")


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.

    User ID will be extracted from JWT token, not provided in request body.
    Completed status defaults to False.
    """
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v):
        """Ensure due date is not in the past."""
        if v and v < datetime.utcnow():
            raise ValueError("Due date cannot be in the past")
        return v

    @field_validator('priority_id')
    @classmethod
    def validate_priority_id(cls, v):
        """Validate priority_id is within valid range."""
        if v is not None and v not in [1, 2, 3]:
            raise ValueError("Priority ID must be 1 (High), 2 (Medium), or 3 (Low)")
        return v

    @field_validator('recurrence_pattern')
    @classmethod
    def validate_recurrence_pattern(cls, v, info):
        """Ensure recurrence_pattern is only set if is_recurring is True."""
        if v and not info.data.get('is_recurring'):
            raise ValueError("recurrence_pattern can only be set when is_recurring is True")
        if info.data.get('is_recurring') and not v:
            raise ValueError("recurrence_pattern is required when is_recurring is True")
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    All fields are optional to support partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority_id: Optional[int] = Field(None, description="Priority ID (1=High, 2=Medium, 3=Low)")
    due_date: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = None
    tag_ids: Optional[list[int]] = Field(None, description="List of tag IDs")

    @field_validator('priority_id')
    @classmethod
    def validate_priority_id(cls, v):
        """Validate priority_id is within valid range."""
        if v is not None and v not in [1, 2, 3]:
            raise ValueError("Priority ID must be 1 (High), 2 (Medium), or 3 (Low)")
        return v


class TaskRead(BaseModel):
    """
    Schema for task responses.

    Includes all database fields including auto-generated ones.
    Note: user_id is returned as string for consistent JSON serialization.
    """
    id: int
    user_id: str  # UUID serialized as string for JSON compatibility
    title: str
    description: Optional[str]
    completed: bool
    priority_id: Optional[int]
    due_date: Optional[datetime]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    tag_ids: list[int] = Field(default_factory=list, description="List of tag IDs associated with this task")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode for SQLModel compatibility (Pydantic v2)
