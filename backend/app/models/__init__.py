"""
SQLModel database models.

All database entities are defined here using SQLModel.
Models are exported for use in routes and migrations.
"""

from app.models.user import User
from app.models.task import Task

__all__ = ["User", "Task"]
