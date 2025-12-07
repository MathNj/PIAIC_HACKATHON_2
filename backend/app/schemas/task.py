"""
Task Pydantic schemas for API validation.

Defines request/response models for task endpoints.
Separates database models from API contracts for flexibility.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal


class TaskBase(BaseModel):
    """Base schema with common task fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[Literal["low", "normal", "high"]] = Field("normal", description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Optional due date for the task")


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.

    User ID will be extracted from JWT token, not provided in request body.
    Completed status defaults to False.
    Priority defaults to 'normal'.
    """
    @validator('due_date')
    def validate_due_date(cls, v):
        """Ensure due date is not in the past."""
        if v and v < datetime.utcnow():
            raise ValueError("Due date cannot be in the past")
        return v


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.

    All fields are optional to support partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[Literal["low", "normal", "high"]] = None
    due_date: Optional[datetime] = None


class TaskRead(TaskBase):
    """
    Schema for task responses.

    Includes all database fields including auto-generated ones.
    Note: user_id is returned as string for consistent JSON serialization.
    """
    id: int
    user_id: str  # UUID serialized as string for JSON compatibility
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Enable ORM mode for SQLModel compatibility (Pydantic v1)
