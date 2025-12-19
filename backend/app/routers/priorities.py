"""
Priorities router for read-only priority lookup.

Provides endpoint to fetch all available priority levels.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models.priority import Priority
from app.schemas.priority import PriorityRead, PriorityList

router = APIRouter(prefix="/api/priorities", tags=["Priorities"])


@router.get("", response_model=PriorityList)
async def get_priorities(
    session: Session = Depends(get_session)
):
    """
    Get all available priority levels.

    Returns:
        PriorityList: List of all priorities (High, Medium, Low)

    Example:
        GET /api/priorities
        Response: {
            "priorities": [
                {"id": 1, "name": "High", "level": 1, "color": "#EF4444"},
                {"id": 2, "name": "Medium", "level": 2, "color": "#F59E0B"},
                {"id": 3, "name": "Low", "level": 3, "color": "#10B981"}
            ]
        }
    """
    statement = select(Priority).order_by(Priority.level)
    priorities = session.exec(statement).all()

    return PriorityList(priorities=[PriorityRead.model_validate(p) for p in priorities])
