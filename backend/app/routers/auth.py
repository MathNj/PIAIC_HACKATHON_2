"""
Authentication router with signup and login endpoints.

Endpoints:
- POST /api/signup: Register new user account
- POST /api/login: Authenticate user and issue JWT token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.auth.password import hash_password, verify_password
from app.auth.utils import create_access_token


router = APIRouter(prefix="/api", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    session: Session = Depends(get_session)
):
    """
    Register a new user account.

    Args:
        user_data: User registration data (email, name, password)
        session: Database session

    Returns:
        UserResponse: Created user data (without password)

    Raises:
        HTTPException 400: Email already registered or validation fails
    """
    # Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Validate password requirements (minimum 8 characters enforced by schema)
    # Additional validation: at least one uppercase, one lowercase, one number
    password = user_data.password
    if not any(c.isupper() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one uppercase letter"
        )
    if not any(c.islower() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter"
        )
    if not any(c.isdigit() for c in password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one number"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Convert to response schema with string ID
    return UserResponse(
        id=str(new_user.id),
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at
    )


@router.post("/login")
async def login(
    credentials: UserLogin,
    session: Session = Depends(get_session)
):
    """
    Authenticate user and issue JWT token.

    Args:
        credentials: User login credentials (email, password)
        session: Database session

    Returns:
        dict: Access token, token type, and user data

    Raises:
        HTTPException 401: Invalid credentials
    """
    # Find user by email
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "user_id": str(user.id), "email": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat()
        }
    }
