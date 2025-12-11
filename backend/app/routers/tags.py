"""
Tags router for tag management.

Provides endpoints for creating, reading, updating, and deleting tags.
Tags are global (not user-scoped) for consistent categorization.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagRead, TagList, TagUpdate
from datetime import datetime

router = APIRouter(prefix="/api/tags", tags=["Tags"])


@router.get("", response_model=TagList)
async def get_tags(
    session: Session = Depends(get_session)
):
    """
    Get all available tags.

    Returns:
        TagList: List of all tags ordered by name

    Example:
        GET /api/tags
        Response: {
            "tags": [
                {"id": 1, "name": "work", "created_at": "2025-12-11T12:00:00Z"},
                {"id": 2, "name": "personal", "created_at": "2025-12-11T12:05:00Z"}
            ]
        }
    """
    statement = select(Tag).order_by(Tag.name)
    tags = session.exec(statement).all()

    return TagList(tags=[TagRead.model_validate(t) for t in tags])


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    session: Session = Depends(get_session)
):
    """
    Create a new tag.

    Args:
        tag_data: Tag creation data (name will be normalized to lowercase)

    Returns:
        TagRead: Created tag object

    Raises:
        400: Tag name already exists

    Example:
        POST /api/tags
        Body: {"name": "Work"}
        Response: {"id": 1, "name": "work", "created_at": "2025-12-11T12:00:00Z"}
    """
    # Check if tag already exists (case-insensitive)
    statement = select(Tag).where(Tag.name == tag_data.name)
    existing_tag = session.exec(statement).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{tag_data.name}' already exists"
        )

    # Create new tag
    new_tag = Tag(
        name=tag_data.name,
        created_at=datetime.utcnow()
    )

    session.add(new_tag)
    session.commit()
    session.refresh(new_tag)

    return TagRead.model_validate(new_tag)


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(
    tag_id: int,
    session: Session = Depends(get_session)
):
    """
    Get a specific tag by ID.

    Args:
        tag_id: Tag identifier

    Returns:
        TagRead: Tag object

    Raises:
        404: Tag not found

    Example:
        GET /api/tags/1
        Response: {"id": 1, "name": "work", "created_at": "2025-12-11T12:00:00Z"}
    """
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    return TagRead.model_validate(tag)


@router.put("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    session: Session = Depends(get_session)
):
    """
    Update a tag's name.

    Args:
        tag_id: Tag identifier
        tag_data: Updated tag data

    Returns:
        TagRead: Updated tag object

    Raises:
        404: Tag not found
        400: New tag name already exists

    Example:
        PUT /api/tags/1
        Body: {"name": "urgent"}
        Response: {"id": 1, "name": "urgent", "created_at": "2025-12-11T12:00:00Z"}
    """
    # Find existing tag
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    # Check if new name already exists (case-insensitive)
    statement = select(Tag).where(Tag.name == tag_data.name, Tag.id != tag_id)
    existing_tag = session.exec(statement).first()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{tag_data.name}' already exists"
        )

    # Update tag name
    tag.name = tag_data.name
    session.add(tag)
    session.commit()
    session.refresh(tag)

    return TagRead.model_validate(tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    session: Session = Depends(get_session)
):
    """
    Delete a tag.

    Deleting a tag will remove all task-tag associations (CASCADE).

    Args:
        tag_id: Tag identifier

    Returns:
        204 No Content

    Raises:
        404: Tag not found

    Example:
        DELETE /api/tags/1
        Response: 204 No Content
    """
    # Find existing tag
    statement = select(Tag).where(Tag.id == tag_id)
    tag = session.exec(statement).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    # Delete tag (CASCADE will remove task_tags entries)
    session.delete(tag)
    session.commit()

    return None
