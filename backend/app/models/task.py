"""
Task SQLModel for TODO application.

Represents a task item owned by a user.
Each task has a title, optional description, completion status, priority, due date, and timestamps.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Index
from enum import Enum
from pydantic import ConfigDict


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class Task(SQLModel, table=True):
    """
    Task model for multi-user TODO application.

    Attributes:
        id: Unique task identifier (auto-incrementing integer)
        user_id: Foreign key to User (UUID)
        title: Task title/summary (required, max 200 chars)
        description: Optional detailed description (max 2000 chars)
        completed: Completion status (default False)
        priority: Task priority (low, normal, high) - default normal
        due_date: Optional due date for the task
        created_at: Task creation timestamp
        updated_at: Last modification timestamp

    Indexes:
        - user_id: For efficient filtering by user
        - completed: For efficient status filtering
        - priority: For efficient priority filtering

    Relations:
        user: Many-to-one relationship with User model
    """

    __tablename__ = "tasks"

    # Primary key (auto-incrementing integer)
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        nullable=False
    )

    # Foreign key to users table
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        index=True,
        description="User who owns this task"
    )

    # Task content
    title: str = Field(
        nullable=False,
        max_length=200,
        description="Task title (required, max 200 characters)"
    )

    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description (max 2000 characters)"
    )

    # Status
    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Task completion status"
    )

    # Priority (V2: foreign key to priorities table)
    priority_id: Optional[int] = Field(
        default=None,
        foreign_key="priorities.id",
        nullable=True,
        index=True,
        description="Foreign key to priorities table (nullable)"
    )

    # Due date
    due_date: Optional[datetime] = Field(
        default=None,
        nullable=True,
        index=True,
        description="Optional due date for the task (UTC)"
    )

    # Recurring task fields (V2)
    is_recurring: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Whether task regenerates on completion"
    )

    recurrence_pattern: Optional[str] = Field(
        default=None,
        nullable=True,
        max_length=20,
        description="Recurrence frequency: 'daily', 'weekly', 'monthly', 'yearly'"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "normal",
                "due_date": "2025-12-15T12:00:00Z",
                "created_at": "2025-12-06T12:00:00Z",
                "updated_at": "2025-12-06T12:00:00Z"
            }
        }
    )


# Create composite indexes for efficient filtering
# This is defined outside the class to ensure it's created in migrations
__table_args__ = (
    Index("idx_tasks_user_completed", "user_id", "completed"),
    Index("idx_tasks_user_priority", "user_id", "priority"),
)
