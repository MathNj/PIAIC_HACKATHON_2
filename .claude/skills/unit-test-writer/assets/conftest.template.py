"""
Shared pytest fixtures for FastAPI and MCP tool testing.

This conftest.py provides reusable fixtures for database mocking and test setup.
Place this file in your tests/ directory.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ============================================================================
# FastAPI TestClient Fixture
# ============================================================================

@pytest.fixture
def client():
    """
    FastAPI TestClient fixture.

    Replace 'app.main:app' with your actual FastAPI app import.
    """
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# Database Mocking Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """
    Mock SQLAlchemy database session.

    Usage:
        def test_my_endpoint(mock_db_session):
            # Configure mock behavior
            mock_db_session.query.return_value.filter.return_value.first.return_value = MockUser()
    """
    mock_session = MagicMock(spec=Session)
    return mock_session


@pytest.fixture
def mock_db():
    """
    Mock database dependency for FastAPI dependency injection.

    Usage:
        from app.main import app
        from app.database import get_db

        def test_endpoint(client, mock_db):
            app.dependency_overrides[get_db] = lambda: mock_db
            response = client.get("/endpoint")
            # ... assertions
            app.dependency_overrides.clear()
    """
    mock_session = MagicMock(spec=Session)
    yield mock_session
    # Cleanup after test


@pytest.fixture
def mock_async_db_session():
    """
    Mock async SQLAlchemy database session.

    Use this for async database operations.
    """
    mock_session = AsyncMock()
    return mock_session


# ============================================================================
# Common Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User",
        "is_active": True,
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        "id": 1,
        "title": "Test Task",
        "description": "Test Description",
        "completed": False,
        "user_id": 1,
    }


# ============================================================================
# MCP Tool Testing Fixtures
# ============================================================================

@pytest.fixture
def mock_mcp_context():
    """
    Mock MCP context for tool testing.

    Use this when testing MCP server tools that require context.
    """
    return MagicMock()


# ============================================================================
# Authentication/Authorization Mocking
# ============================================================================

@pytest.fixture
def mock_current_user(sample_user_data):
    """
    Mock current authenticated user.

    Usage:
        from app.dependencies import get_current_user

        def test_protected_endpoint(client, mock_current_user):
            app.dependency_overrides[get_current_user] = lambda: mock_current_user
            response = client.get("/protected")
            # ... assertions
            app.dependency_overrides.clear()
    """
    user = MagicMock()
    user.id = sample_user_data["id"]
    user.email = sample_user_data["email"]
    user.name = sample_user_data["name"]
    user.is_active = sample_user_data["is_active"]
    return user


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for authentication testing."""
    return "mock.jwt.token"


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """
    Automatically clear FastAPI dependency overrides after each test.

    This prevents test pollution when using dependency_overrides.
    """
    yield
    # Cleanup runs after each test
    from app.main import app
    app.dependency_overrides.clear()
