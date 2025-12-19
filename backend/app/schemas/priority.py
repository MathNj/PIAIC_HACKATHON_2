"""
Priority Pydantic schemas for API request/response.

Defines read-only schemas for priority lookup table.
"""

from pydantic import BaseModel, ConfigDict, Field


class PriorityRead(BaseModel):
    """
    Priority read schema for API responses.

    Attributes:
        id: Unique identifier (1=High, 2=Medium, 3=Low)
        name: Display name ("High", "Medium", "Low")
        level: Numeric level for sorting (1=highest urgency)
        color: Hex color code for UI badges
    """

    id: int = Field(description="Unique identifier")
    name: str = Field(description="Priority display name")
    level: int = Field(description="Numeric level for sorting")
    color: str = Field(description="Hex color code for UI badges")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "High",
                "level": 1,
                "color": "#EF4444"
            }
        }
    )


class PriorityList(BaseModel):
    """
    List of priorities response schema.

    Attributes:
        priorities: List of priority objects
    """

    priorities: list[PriorityRead] = Field(description="List of available priorities")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "priorities": [
                    {"id": 1, "name": "High", "level": 1, "color": "#EF4444"},
                    {"id": 2, "name": "Medium", "level": 2, "color": "#F59E0B"},
                    {"id": 3, "name": "Low", "level": 3, "color": "#10B981"}
                ]
            }
        }
    )
