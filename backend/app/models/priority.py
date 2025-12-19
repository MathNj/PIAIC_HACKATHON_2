"""
Priority SQLModel for task priority levels.

Lookup table with three predefined priority levels: High, Medium, Low.
"""

from sqlmodel import Field, SQLModel
from pydantic import ConfigDict


class Priority(SQLModel, table=True):
    """
    Priority model for task urgency levels.

    Attributes:
        id: Unique identifier (1=High, 2=Medium, 3=Low)
        name: Display name ("High", "Medium", "Low")
        level: Numeric level for sorting (1=highest urgency)
        color: Hex color code for UI badges

    Seed Data:
        (1, "High", 1, "#EF4444")    - Red
        (2, "Medium", 2, "#F59E0B")  - Yellow
        (3, "Low", 3, "#10B981")     - Green
    """

    __tablename__ = "priorities"

    # Primary key (manually assigned: 1, 2, 3)
    id: int = Field(
        primary_key=True,
        nullable=False,
        description="Unique identifier (1=High, 2=Medium, 3=Low)"
    )

    # Display name
    name: str = Field(
        nullable=False,
        max_length=50,
        unique=True,
        index=True,
        description="Priority display name"
    )

    # Numeric level for sorting
    level: int = Field(
        nullable=False,
        unique=True,
        description="Numeric level for sorting (1=highest urgency)"
    )

    # UI color code
    color: str = Field(
        nullable=False,
        max_length=7,
        description="Hex color code for UI badges (e.g., #EF4444)"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "High",
                "level": 1,
                "color": "#EF4444"
            }
        }
    )
