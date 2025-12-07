"""
Pytest fixtures and configuration for tests.

Provides reusable test fixtures for database, client, and authentication.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models.user import User
from app.models.task import Task
from app.auth.password import hash_password


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a fresh in-memory SQLite database for each test.

    This ensures test isolation - each test gets a clean database.
    """
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Create session
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a test client with overridden database session.

    This client uses the test database instead of the real one.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """
    Create a test user in the database.

    Returns the created user object with known credentials.
    """
    user = User(
        email="test@example.com",
        name="Test User",
        password_hash=hash_password("TestPass123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(client: TestClient, test_user: User):
    """
    Get a valid JWT token for the test user.

    Returns the authentication token that can be used in requests.
    """
    response = client.post(
        "/api/login",
        json={"email": "test@example.com", "password": "TestPass123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(auth_token: str):
    """
    Get authentication headers with Bearer token.

    Returns headers dict ready to use in requests.
    """
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(name="test_task")
def test_task_fixture(session: Session, test_user: User):
    """
    Create a test task in the database.

    Returns the created task object.
    """
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="This is a test task",
        completed=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="second_user")
def second_user_fixture(session: Session):
    """
    Create a second test user for authorization tests.

    Returns the created user object.
    """
    user = User(
        email="second@example.com",
        name="Second User",
        password_hash=hash_password("SecondPass123")
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
