---
name: "backend-scaffolder"
description: "Scaffolds complete FastAPI vertical slices (Model, Schema, Router) with SQLModel, JWT auth, and pytest tests. Use for Phase II backend implementations."
version: "2.0.0"
---

# Backend Scaffolder Skill

## When to Use
- User asks to "implement the backend" for a feature
- User says "Generate CRUD endpoints" or "Scaffold backend"
- After creating a feature spec (`@specs/features/[feature].md`)
- Phase II backend development

## Context
This skill implements backend features following:
- **Project Structure**: See `@backend/CLAUDE.md`
- **Tech Stack**: FastAPI 0.95.2, SQLModel 0.0.14, JWT auth, SQLite/Neon PostgreSQL
- **Patterns**: Multi-user isolation with `user_id` verification, dependency injection
- **Security**: All routes require JWT authentication via `Depends(get_current_user)`

## Workflow
1. **Read Spec**: Read `@specs/features/[feature-name].md` for data model and API contract
2. **Model Generation**: Create SQLModel class in `backend/app/models/[feature].py`
3. **Schema Generation**: Create Pydantic DTOs in `backend/app/schemas/[feature].py`
4. **Router Creation**: Create FastAPI router in `backend/app/routers/[feature].py`
5. **Security Integration**: Inject `Depends(get_current_user)` on ALL endpoints
6. **Multi-User Isolation**: Filter queries by `user_id` from JWT
7. **Test Generation**: Create pytest tests in `backend/tests/test_[feature].py`
8. **Registration**: Update `backend/app/main.py` to include router

## Output Format

### 1. Model File: `backend/app/models/[feature].py`
```python
"""
[Feature] SQLModel for TODO application.

[Description of what this model represents]
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Index


class [FeatureName](SQLModel, table=True):
    """
    [Feature] model for multi-user TODO application.

    Attributes:
        id: Unique identifier (auto-incrementing integer)
        user_id: Foreign key to User (UUID)
        [field]: [description]
        created_at: Creation timestamp
        updated_at: Last modification timestamp

    Indexes:
        - user_id: For efficient filtering by user
        - [additional indexes]

    Relations:
        user: Many-to-one relationship with User model
    """

    __tablename__ = "[table_name]"

    # Primary key
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
        description="User who owns this resource"
    )

    # Feature-specific fields
    [field_name]: [type] = Field(
        [constraints],
        description="[description]"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)"
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                # ... example data
            }
        }
```

### 2. Schema File: `backend/app/schemas/[feature].py`
```python
"""
[Feature] Pydantic schemas for API validation.

Defines request/response models for [feature] endpoints.
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, Literal


class [Feature]Base(BaseModel):
    """Base schema with common [feature] fields."""
    [field]: [type] = Field(..., [constraints], description="[description]")


class [Feature]Create([Feature]Base):
    """
    Schema for creating a new [feature].

    user_id extracted from JWT, not provided in request body.
    """
    @validator('[field]')
    def validate_[field](cls, v):
        """Validation logic."""
        if [condition]:
            raise ValueError('[error message]')
        return v


class [Feature]Update(BaseModel):
    """
    Schema for updating an existing [feature].

    All fields optional for partial updates.
    """
    [field]: Optional[type] = Field(None, [constraints])


class [Feature]Read([Feature]Base):
    """
    Schema for [feature] responses.

    Includes all database fields including auto-generated ones.
    """
    id: int
    user_id: str  # UUID serialized as string
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Enable ORM mode for SQLModel compatibility
```

### 3. Router File: `backend/app/routers/[feature].py`
```python
"""
[Feature] API routes.

Endpoints for [feature] CRUD operations with multi-user isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from uuid import UUID
from typing import Annotated

from app.database import get_session
from app.models.[feature] import [Feature]
from app.schemas.[feature] import [Feature]Read, [Feature]Create, [Feature]Update
from app.auth.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api", tags=["[Features]"])


@router.get("/{user_id}/[features]", response_model=list[[Feature]Read])
async def get_[features](
    user_id: UUID,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> list[[Feature]Read]:
    """
    Get all [features] for a user.

    Authorization: User can only access their own [features].
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot access [features] for user {user_id}"
        )

    # Query with multi-user isolation
    statement = select([Feature]).where([Feature].user_id == user_id)

    try:
        [features] = session.exec(statement).all()
        return [
            [Feature]Read(
                id=[feature].id,
                user_id=str([feature].user_id),
                # ... all fields
                created_at=[feature].created_at,
                updated_at=[feature].updated_at
            )
            for [feature] in [features]
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve [features]: {str(e)}"
        )


@router.post("/{user_id}/[features]", response_model=[Feature]Read, status_code=status.HTTP_201_CREATED)
async def create_[feature](
    user_id: UUID,
    [feature]_data: [Feature]Create,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> [Feature]Read:
    """
    Create a new [feature] for a user.

    Authorization: User can only create [features] for themselves.
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot create [features] for user {user_id}"
        )

    # Create object with user_id from JWT
    new_[feature] = [Feature](
        user_id=current_user,
        **[feature]_data.dict()
    )

    try:
        session.add(new_[feature])
        session.commit()
        session.refresh(new_[feature])

        return [Feature]Read(
            id=new_[feature].id,
            user_id=str(new_[feature].user_id),
            # ... all fields
            created_at=new_[feature].created_at,
            updated_at=new_[feature].updated_at
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create [feature]: {str(e)}"
        )


@router.put("/{user_id}/[features]/{[feature]_id}", response_model=[Feature]Read)
async def update_[feature](
    user_id: UUID,
    [feature]_id: int,
    [feature]_update: [Feature]Update,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> [Feature]Read:
    """
    Update an existing [feature].

    Authorization: User can only update their own [features].
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot update [features] for user {user_id}"
        )

    # Fetch with multi-user isolation
    statement = select([Feature]).where(
        [Feature].id == [feature]_id,
        [Feature].user_id == user_id
    )
    [feature] = session.exec(statement).first()

    if not [feature]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"[Feature] {[feature]_id} not found"
        )

    # Partial update
    update_data = [feature]_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr([feature], field, value)

    [feature].updated_at = datetime.utcnow()

    try:
        session.add([feature])
        session.commit()
        session.refresh([feature])

        return [Feature]Read(
            id=[feature].id,
            user_id=str([feature].user_id),
            # ... all fields
            created_at=[feature].created_at,
            updated_at=[feature].updated_at
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update [feature]: {str(e)}"
        )


@router.delete("/{user_id}/[features]/{[feature]_id}", status_code=status.HTTP_200_OK)
async def delete_[feature](
    user_id: UUID,
    [feature]_id: int,
    current_user: Annotated[UUID, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a [feature].

    Authorization: User can only delete their own [features].
    """
    # Authorization check
    if user_id != current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: Cannot delete [features] for user {user_id}"
        )

    # Fetch with multi-user isolation
    statement = select([Feature]).where(
        [Feature].id == [feature]_id,
        [Feature].user_id == user_id
    )
    [feature] = session.exec(statement).first()

    if not [feature]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"[Feature] {[feature]_id} not found"
        )

    try:
        session.delete([feature])
        session.commit()
        return {"detail": "[Feature] deleted"}
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete [feature]: {str(e)}"
        )
```

### 4. Test File: `backend/tests/test_[feature].py`
```python
"""
Tests for [Feature] API endpoints.
"""

import pytest
from httpx import AsyncClient
from app.models.[feature] import [Feature]


@pytest.mark.[feature]
class Test[Feature]Operations:
    """Test CRUD operations for [features]."""

    @pytest.mark.asyncio
    async def test_create_[feature](self, client: AsyncClient, auth_headers: dict, test_user):
        """Test creating a new [feature]."""
        [feature]_data = {
            "[field]": "value"
        }

        response = await client.post(
            f"/api/{test_user.id}/[features]",
            json=[feature]_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["[field]"] == "value"
        assert data["user_id"] == str(test_user.id)

    @pytest.mark.asyncio
    async def test_list_[features](self, client: AsyncClient, auth_headers: dict, test_user, test_[feature]):
        """Test listing [features] for a user."""
        response = await client.get(
            f"/api/{test_user.id}/[features]",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    # Add more tests: update, delete, authorization checks, etc.
```

## Post-Scaffolding Steps
1. **Update main.py**: Add router to app
   ```python
   from app.routers import [feature]
   app.include_router([feature].router)
   ```

2. **Restart Backend Server**: Apply new routes
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

3. **Run Tests**: Verify implementation
   ```bash
   cd backend
   pytest tests/test_[feature].py -v
   ```

4. **Create PHR**: Document the implementation
   - Title: "[Feature] Backend Implementation"
   - Stage: `green`
   - Feature: `[feature-name]`

5. **Test with Swagger**: http://localhost:8000/docs

## Example
**Input**: "Scaffold backend for tagging system"

**Output**:
- `backend/app/models/tag.py` - Tag SQLModel with user_id, name, color
- `backend/app/schemas/tag.py` - TagCreate, TagUpdate, TagRead schemas
- `backend/app/routers/tag.py` - CRUD endpoints for tags with JWT auth
- `backend/tests/test_tag.py` - Pytest tests for tag operations
- Router registered in `main.py`

## Quality Checklist
Before finalizing:
- [ ] All fields in model match the spec
- [ ] All endpoints have `Depends(get_current_user)` for JWT auth
- [ ] All queries filter by `user_id` for multi-user isolation
- [ ] Authorization check compares path `user_id` with JWT `current_user`
- [ ] Timestamps (created_at, updated_at) are included
- [ ] Response schemas convert UUID to string
- [ ] Error handling with appropriate HTTP status codes
- [ ] Pytest tests cover main CRUD operations
- [ ] Router registered in main.py
- [ ] Swagger docs accessible at /docs
