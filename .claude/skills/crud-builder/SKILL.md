---
name: "crud-builder"
description: "Generates complete CRUD operations for data models including SQLModel schemas, FastAPI routers, Pydantic request/response models, and pytest tests. Use when scaffolding new resources, adding CRUD endpoints, or implementing standard database operations."
version: "1.0.0"
---

# CRUD Builder Skill

## When to Use
- User says "Create CRUD for..." or "Generate CRUD operations for [Model]"
- Need to scaffold a new data resource with full Create, Read, Update, Delete operations
- Adding standard database operations for a new entity
- Implementing REST API endpoints following CRUD conventions
- Phase II or later development requiring database-backed APIs

## Context
This skill implements the standard CRUD pattern for the Todo App architecture:
- **Tech Stack**: FastAPI + SQLModel + PostgreSQL
- **Authentication**: JWT-based user_id validation on all operations
- **Pattern**: Model → Schema → Router → Tests
- **Location**:
  - Models: `backend/app/models/`
  - Schemas: `backend/app/schemas/`
  - Routers: `backend/app/routers/`
  - Tests: `backend/tests/`

## Workflow

### 1. Analyze Requirements
- **Model Name**: Singular form (e.g., Task, Comment, Profile)
- **Fields**: Data types, constraints, defaults
- **Relationships**: Foreign keys, one-to-many, many-to-many
- **User Scoping**: Does this resource belong to a user? (user_id required)
- **Validation Rules**: Custom validators, business logic

### 2. Generate SQLModel (Database Model)
Create in `backend/app/models/[model_name].py`

**Template**:
```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID, uuid4

class [ModelName](SQLModel, table=True):
    __tablename__ = "[table_name]"

    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign Keys
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)

    # Data Fields
    [field_name]: [type] = Field([constraints])

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="[plural_model_name]")
```

**Constraints Examples**:
- `max_length=255` - String length limit
- `nullable=False` - Required field
- `index=True` - Database index for faster queries
- `unique=True` - Unique constraint
- `default="value"` - Default value
- `ge=0, le=100` - Numeric range (greater/equal, less/equal)

### 3. Generate Pydantic Schemas
Create in `backend/app/schemas/[model_name].py`

**Template**:
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

# Create Request
class [ModelName]Create(BaseModel):
    [field_name]: [type] = Field(..., description="[Description]")
    # user_id is NOT included (extracted from JWT token)

    @validator('[field_name]')
    def validate_field(cls, v):
        # Custom validation logic
        return v

# Update Request
class [ModelName]Update(BaseModel):
    [field_name]: Optional[[type]] = Field(None, description="[Description]")
    # All fields optional for partial updates

# Response
class [ModelName]Response(BaseModel):
    id: int
    user_id: str  # UUID as string
    [field_name]: [type]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode

# List Response
class [ModelName]ListResponse(BaseModel):
    items: list[[ModelName]Response]
    total: int
    page: int
    page_size: int
```

### 4. Generate FastAPI Router
Create in `backend/app/routers/[model_name].py`

**Template**:
```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from uuid import UUID

from app.database import get_session
from app.models.[model_name] import [ModelName]
from app.schemas.[model_name] import (
    [ModelName]Create,
    [ModelName]Update,
    [ModelName]Response,
    [ModelName]ListResponse
)
from app.auth import get_current_user_id

router = APIRouter(
    prefix="/[plural_name]",
    tags=["[ModelName]"]
)

# CREATE
@router.post("/", response_model=[ModelName]Response, status_code=status.HTTP_201_CREATED)
async def create_[model_name](
    [model_name]_data: [ModelName]Create,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new [model_name]."""
    [model_name] = [ModelName](
        user_id=user_id,
        **[model_name]_data.model_dump()
    )
    session.add([model_name])
    session.commit()
    session.refresh([model_name])
    return [model_name]

# READ (List with Pagination)
@router.get("/", response_model=[ModelName]ListResponse)
async def list_[plural_name](
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """List all [plural_name] for the current user."""
    offset = (page - 1) * page_size

    # Count total
    count_statement = select([ModelName]).where([ModelName].user_id == user_id)
    total = len(session.exec(count_statement).all())

    # Get paginated results
    statement = (
        select([ModelName])
        .where([ModelName].user_id == user_id)
        .offset(offset)
        .limit(page_size)
        .order_by([ModelName].created_at.desc())
    )
    [plural_name] = session.exec(statement).all()

    return {
        "items": [plural_name],
        "total": total,
        "page": page,
        "page_size": page_size
    }

# READ (Single)
@router.get("/{[model_name]_id}", response_model=[ModelName]Response)
async def get_[model_name](
    [model_name]_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get a specific [model_name] by ID."""
    statement = select([ModelName]).where(
        [ModelName].id == [model_name]_id,
        [ModelName].user_id == user_id
    )
    [model_name] = session.exec(statement).first()

    if not [model_name]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="[ModelName] not found"
        )

    return [model_name]

# UPDATE
@router.patch("/{[model_name]_id}", response_model=[ModelName]Response)
async def update_[model_name](
    [model_name]_id: int,
    [model_name]_data: [ModelName]Update,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update a [model_name]."""
    statement = select([ModelName]).where(
        [ModelName].id == [model_name]_id,
        [ModelName].user_id == user_id
    )
    [model_name] = session.exec(statement).first()

    if not [model_name]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="[ModelName] not found"
        )

    # Update only provided fields
    update_data = [model_name]_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr([model_name], key, value)

    [model_name].updated_at = datetime.utcnow()
    session.add([model_name])
    session.commit()
    session.refresh([model_name])

    return [model_name]

# DELETE
@router.delete("/{[model_name]_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_[model_name](
    [model_name]_id: int,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Delete a [model_name]."""
    statement = select([ModelName]).where(
        [ModelName].id == [model_name]_id,
        [ModelName].user_id == user_id
    )
    [model_name] = session.exec(statement).first()

    if not [model_name]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="[ModelName] not found"
        )

    session.delete([model_name])
    session.commit()

    return None
```

### 5. Generate Pytest Tests
Create in `backend/tests/test_[model_name].py`

**Template**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from uuid import uuid4

from app.main import app
from app.models.[model_name] import [ModelName]

client = TestClient(app)

@pytest.fixture
def auth_headers(test_user):
    """Get auth headers for test user."""
    return {"Authorization": f"Bearer {test_user['token']}"}

def test_create_[model_name](auth_headers, db_session: Session):
    """Test creating a [model_name]."""
    payload = {
        "[field_name]": "[test_value]"
    }

    response = client.post("/[plural_name]/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["[field_name]"] == "[test_value]"
    assert "id" in data
    assert "created_at" in data

def test_list_[plural_name](auth_headers, db_session: Session):
    """Test listing [plural_name] with pagination."""
    response = client.get("/[plural_name]/?page=1&page_size=10", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert data["page"] == 1

def test_get_[model_name](auth_headers, db_session: Session):
    """Test getting a specific [model_name]."""
    # Create a test [model_name]
    [model_name] = [ModelName](user_id=uuid4(), [field_name]="[test_value]")
    db_session.add([model_name])
    db_session.commit()
    db_session.refresh([model_name])

    response = client.get(f"/[plural_name]/{[model_name].id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == [model_name].id

def test_update_[model_name](auth_headers, db_session: Session):
    """Test updating a [model_name]."""
    # Create a test [model_name]
    [model_name] = [ModelName](user_id=uuid4(), [field_name]="[old_value]")
    db_session.add([model_name])
    db_session.commit()
    db_session.refresh([model_name])

    payload = {"[field_name]": "[new_value]"}
    response = client.patch(f"/[plural_name]/{[model_name].id}", json=payload, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["[field_name]"] == "[new_value]"

def test_delete_[model_name](auth_headers, db_session: Session):
    """Test deleting a [model_name]."""
    # Create a test [model_name]
    [model_name] = [ModelName](user_id=uuid4(), [field_name]="[test_value]")
    db_session.add([model_name])
    db_session.commit()
    db_session.refresh([model_name])

    response = client.delete(f"/[plural_name]/{[model_name].id}", headers=auth_headers)

    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/[plural_name]/{[model_name].id}", headers=auth_headers)
    assert response.status_code == 404

def test_user_isolation(auth_headers, db_session: Session):
    """Test that users can only access their own [plural_name]."""
    # Create [model_name] for different user
    other_user_id = uuid4()
    [model_name] = [ModelName](user_id=other_user_id, [field_name]="[test_value]")
    db_session.add([model_name])
    db_session.commit()
    db_session.refresh([model_name])

    # Try to access with different user token
    response = client.get(f"/[plural_name]/{[model_name].id}", headers=auth_headers)

    assert response.status_code == 404  # Should not find other user's data
```

### 6. Register Router
Update `backend/app/main.py`:

```python
from app.routers import [model_name]

app.include_router([model_name].router)
```

### 7. Create Database Migration
Run Alembic to generate migration:

```bash
cd backend
alembic revision --autogenerate -m "Add [model_name] table"
alembic upgrade head
```

## Output Format

### File Structure
```
backend/
├── app/
│   ├── models/
│   │   └── [model_name].py          # SQLModel
│   ├── schemas/
│   │   └── [model_name].py          # Pydantic schemas
│   └── routers/
│       └── [model_name].py          # FastAPI router
└── tests/
    └── test_[model_name].py          # Pytest tests
```

### Summary Output
```markdown
## CRUD Operations Created for [ModelName]

### Files Created:
1. ✅ Model: `backend/app/models/[model_name].py`
2. ✅ Schemas: `backend/app/schemas/[model_name].py`
3. ✅ Router: `backend/app/routers/[model_name].py`
4. ✅ Tests: `backend/tests/test_[model_name].py`

### Endpoints:
- POST   /[plural_name]/              - Create
- GET    /[plural_name]/              - List (paginated)
- GET    /[plural_name]/{id}          - Get by ID
- PATCH  /[plural_name]/{id}          - Update
- DELETE /[plural_name]/{id}          - Delete

### Security:
- ✅ JWT authentication required
- ✅ User isolation (user_id scoping)
- ✅ Authorization checks on all operations

### Next Steps:
1. Run migration: `alembic revision --autogenerate -m "Add [model_name] table"`
2. Apply migration: `alembic upgrade head`
3. Run tests: `pytest backend/tests/test_[model_name].py -v`
4. Register router in `backend/app/main.py`
```

## Examples

### Example 1: Comment Model

**Trigger**: "Create CRUD for Comment model with task_id, content, and user_id"

**Output**:

```python
# backend/app/models/comment.py
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID

class Comment(SQLModel, table=True):
    __tablename__ = "comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False, index=True)
    content: str = Field(max_length=2000, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="comments")
    task: Optional["Task"] = Relationship(back_populates="comments")
```

```python
# backend/app/schemas/comment.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    task_id: int = Field(..., description="ID of the task to comment on")
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=2000, description="Comment content")

class CommentResponse(BaseModel):
    id: int
    user_id: str
    task_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int
```

**Endpoints Created**:
- POST /comments/ - Create comment
- GET /comments/ - List comments (filtered by user_id)
- GET /comments/{id} - Get comment by ID
- PATCH /comments/{id} - Update comment
- DELETE /comments/{id} - Delete comment

---

### Example 2: Profile Model

**Trigger**: "Generate CRUD for Profile with avatar_url, bio, and display_name"

**Output**:

```python
# backend/app/models/profile.py
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from uuid import UUID

class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, unique=True, index=True)
    display_name: str = Field(max_length=100, nullable=False)
    bio: Optional[str] = Field(max_length=500, default=None)
    avatar_url: Optional[str] = Field(max_length=255, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="profile")
```

**Special Consideration**: One-to-one relationship (unique user_id)

## Quality Checklist

Before finalizing CRUD operations:
- [ ] SQLModel has proper table name and relationships
- [ ] All fields have appropriate constraints (max_length, nullable, etc.)
- [ ] user_id field present for user scoping (unless global resource)
- [ ] Timestamps (created_at, updated_at) included
- [ ] Pydantic schemas have proper validation
- [ ] Create schema excludes user_id (extracted from JWT)
- [ ] Update schema has all fields as Optional
- [ ] Response schema has from_attributes = True
- [ ] Router has all 5 CRUD endpoints (POST, GET list, GET id, PATCH, DELETE)
- [ ] All endpoints check user_id for authorization
- [ ] List endpoint has pagination (page, page_size)
- [ ] Proper HTTP status codes (201 for create, 204 for delete, 404 for not found)
- [ ] Tests cover all CRUD operations
- [ ] Test for user isolation included
- [ ] Router registered in main.py
- [ ] Database migration created and applied

## Common Patterns

### One-to-Many Relationship
```python
# Parent model
comments: list["Comment"] = Relationship(back_populates="task")

# Child model
task_id: int = Field(foreign_key="tasks.id", nullable=False, index=True)
task: Optional["Task"] = Relationship(back_populates="comments")
```

### Soft Delete (instead of hard delete)
```python
# Add to model
deleted_at: Optional[datetime] = Field(default=None)

# Modify delete endpoint
@router.delete("/{id}")
async def delete_[model_name](...):
    [model_name].deleted_at = datetime.utcnow()
    session.add([model_name])
    session.commit()
```

### Custom Query Filters
```python
@router.get("/")
async def list_[plural_name](
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    ...
):
    statement = select([ModelName]).where([ModelName].user_id == user_id)

    if status:
        statement = statement.where([ModelName].status == status)
    if priority:
        statement = statement.where([ModelName].priority == priority)

    [plural_name] = session.exec(statement).all()
```

## Post-Creation

After generating CRUD:
1. **Run Migration**: `alembic revision --autogenerate -m "Add [model_name]"`
2. **Apply Migration**: `alembic upgrade head`
3. **Run Tests**: `pytest backend/tests/test_[model_name].py -v`
4. **Register Router**: Add to `backend/app/main.py`
5. **Update OpenAPI Docs**: Verify at http://localhost:8000/docs
6. **Create Frontend Types**: Use api-schema-sync skill to generate TypeScript types
7. **Document in Spec**: Update `@specs/api/rest-endpoints.md`
