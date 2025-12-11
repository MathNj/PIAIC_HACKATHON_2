"""
TaskTag SQLModel for many-to-many relationship between tasks and tags.

Junction table enabling multiple tags per task and multiple tasks per tag.
"""

from sqlmodel import Field, SQLModel
from pydantic import ConfigDict


class TaskTag(SQLModel, table=True):
    """
    TaskTag junction model for many-to-many relationship.

    Attributes:
        task_id: Foreign key to tasks table (part of composite primary key)
        tag_id: Foreign key to tags table (part of composite primary key)

    Constraints:
        - Composite primary key: (task_id, tag_id)
        - CASCADE delete: Deleting task removes tag associations
        - CASCADE delete: Deleting tag removes all task associations
    """

    __tablename__ = "task_tags"

    # Composite primary key with foreign keys
    task_id: int = Field(
        foreign_key="tasks.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Foreign key to tasks table"
    )

    tag_id: int = Field(
        foreign_key="tags.id",
        primary_key=True,
        ondelete="CASCADE",
        description="Foreign key to tags table"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": 1,
                "tag_id": 5
            }
        }
    )
