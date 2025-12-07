# Backend Guidelines

## Stack
- **Framework**: FastAPI 0.95.2
- **ORM**: SQLModel 0.0.14
- **Database**: Neon Serverless PostgreSQL (SQLite for local development)
- **Authentication**: JWT with python-jose
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic (for PostgreSQL production)
- **Python**: 3.13+

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point, CORS, routers
│   ├── config.py            # Settings loaded from environment variables
│   ├── database.py          # SQLModel engine, session factory
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User SQLModel
│   │   └── task.py          # Task SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # UserCreate, UserLogin, UserResponse
│   │   └── task.py          # TaskCreate, TaskUpdate, TaskRead
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py          # POST /api/signup, /api/login
│   │   └── tasks.py         # Task CRUD endpoints
│   └── auth/
│       ├── __init__.py
│       ├── utils.py         # JWT verification
│       ├── password.py      # Password hashing
│       └── dependencies.py  # get_current_user dependency
├── alembic/                 # Database migrations (PostgreSQL)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment variable template
└── README.md
```

## API Conventions

### Routing
- All routes under `/api/`
- Auth routes: `/api/signup`, `/api/login` (no JWT required)
- Task routes: `/api/{user_id}/tasks/...` (JWT required)
- Health check: `/health` (public)

### Response Format
Return JSON responses with consistent structure:

```python
# Success
return {"id": 1, "title": "Task", ...}

# Error
raise HTTPException(
    status_code=400,
    detail="Validation error message"
)
```

### Status Codes
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid JWT
- `403 Forbidden` - User ID mismatch
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Unexpected error

## Database Operations

### Using SQLModel

**Query Pattern**:
```python
from sqlmodel import Session, select
from app.models.task import Task
from app.database import get_session

def get_tasks(user_id: str, session: Session):
    # ✅ CORRECT: Filter by user_id
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks

def get_task_by_id(task_id: int, user_id: str, session: Session):
    # ✅ CORRECT: Filter by both ID and user_id (security)
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    task = session.exec(statement).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

**Create/Update Pattern**:
```python
# Create
new_task = Task(
    user_id=current_user_id,
    title=task_data.title,
    description=task_data.description,
    completed=False
)
session.add(new_task)
session.commit()
session.refresh(new_task)
return new_task

# Update
task = get_task_by_id(task_id, user_id, session)
task.title = updated_data.title
task.description = updated_data.description
task.updated_at = datetime.utcnow()
session.add(task)
session.commit()
session.refresh(task)
return task

# Delete
task = get_task_by_id(task_id, user_id, session)
session.delete(task)
session.commit()
```

### Session Management

Use FastAPI dependency injection:
```python
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session

@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: str = Depends(get_current_user)
):
    # Verify user_id matches JWT
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Query tasks
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return tasks
```

## Authentication

### JWT Token Flow

1. **User Login**: Verify credentials, generate JWT
2. **Include Token**: Frontend sends `Authorization: Bearer <token>`
3. **Verify Token**: Extract user_id from JWT
4. **Authorize**: Compare JWT user_id with URL user_id

### Implementation

**Generate Token** (`auth/utils.py`):
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=30))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )
    return encoded_jwt
```

**Verify Token** (`auth/dependencies.py`):
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Use in Endpoint**:
```python
@router.get("/api/{user_id}/tasks")
async def list_tasks(
    user_id: str,
    current_user: str = Depends(get_current_user)
):
    # Verify user owns this resource
    if user_id != current_user:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Continue with operation...
```

### Password Security

**Hash Password** (`auth/password.py`):
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Use in Signup/Login**:
```python
# Signup
hashed = hash_password(user_data.password)
new_user = User(email=user_data.email, password_hash=hashed, ...)

# Login
if not verify_password(credentials.password, user.password_hash):
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

## Environment Variables

**Configuration** (`config.py`):
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    APP_NAME: str = "TODO API"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

**`.env` File**:
```env
DATABASE_URL=sqlite:///./todo_app.db
BETTER_AUTH_SECRET=your-secret-key-must-be-at-least-32-characters-long
FRONTEND_URL=http://localhost:3000
DEBUG=true
```

## CORS Configuration

**In `main.py`**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling

### Validation Errors
```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Title cannot be empty')
        return v
```

### Custom Exceptions
```python
from fastapi import HTTPException

# 400 Bad Request
if not task_data.title:
    raise HTTPException(status_code=400, detail="Title is required")

# 401 Unauthorized
raise HTTPException(status_code=401, detail="Invalid or expired token")

# 403 Forbidden
if user_id != current_user:
    raise HTTPException(status_code=403, detail="Not authorized")

# 404 Not Found
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

## Database Migrations (PostgreSQL)

### Initialize Alembic
```bash
cd backend
alembic init alembic
```

### Configure `alembic/env.py`
```python
from app.models.user import User
from app.models.task import Task
from sqlmodel import SQLModel

target_metadata = SQLModel.metadata
```

### Create Migration
```bash
alembic revision --autogenerate -m "Initial schema"
```

### Apply Migration
```bash
alembic upgrade head
```

## Running the Backend

```bash
# Development
cd backend
uvicorn app.main:app --reload --port 8000

# With custom host
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Testing

### Manual Testing
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### See `TESTING.md` for:
- Postman collection
- curl examples
- Test scenarios

## Security Checklist

- [ ] All passwords hashed with bcrypt
- [ ] JWT tokens validated on protected endpoints
- [ ] User ID verification (JWT vs URL parameter)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevented (SQLModel parameterized queries)
- [ ] CORS configured for frontend domain only
- [ ] Environment variables for secrets (no hardcoding)
- [ ] HTTPS in production

## Performance Tips

- Use database indexes on `user_id` and `completed` fields
- Connection pooling for PostgreSQL (configured in `database.py`)
- Cache static data when possible
- Use `select().where()` instead of fetching all and filtering
- Limit query results for large datasets

## Deployment

### Railway/Render
```bash
# Procfile
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables (Production)
```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
BETTER_AUTH_SECRET=production-secret-at-least-32-characters
FRONTEND_URL=https://your-app.vercel.app
DEBUG=false
```

## References
- Spec: `@specs/features/task-crud.md`, `@specs/features/authentication.md`
- API: `@specs/api/rest-endpoints.md`
- Database: `@specs/database/schema.md`
- Testing: `TESTING.md`
- Deployment: `DEPLOYMENT.md`
