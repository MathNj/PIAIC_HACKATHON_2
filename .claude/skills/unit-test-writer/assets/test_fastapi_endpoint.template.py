"""
Unit tests for FastAPI endpoint: [ENDPOINT_NAME]

This template demonstrates the 3 required test cases for FastAPI endpoints:
1. Happy Path (Success 200/201)
2. Validation Error (422 Unprocessable Entity)
3. Logic Error/Edge Case (404 Not Found or 500 Internal Error)

All database interactions are strictly mocked - no actual database connections.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import status


# ============================================================================
# Test Setup and Fixtures
# ============================================================================

@pytest.fixture
def mock_task_model():
    """Mock SQLModel Task instance."""
    task = MagicMock()
    task.id = 1
    task.title = "Test Task"
    task.description = "Test Description"
    task.completed = False
    task.user_id = 1
    return task


@pytest.fixture
def valid_task_payload():
    """Valid request payload for creating a task."""
    return {
        "title": "New Task",
        "description": "Task description",
        "completed": False,
    }


@pytest.fixture
def invalid_task_payload():
    """Invalid request payload (missing required fields)."""
    return {
        "description": "Missing title field",
    }


# ============================================================================
# Test Case 1: Happy Path (Success 200/201)
# ============================================================================

def test_create_task_success(client, mock_db, valid_task_payload, mock_task_model):
    """
    Test successful task creation (Happy Path).

    Expected:
    - Status: 201 Created
    - Response contains created task data
    - Database session methods called correctly
    """
    from app.main import app
    from app.database import get_db

    # Configure mock database behavior
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    # Mock the created task that gets returned
    def mock_refresh(task):
        task.id = mock_task_model.id
        task.title = valid_task_payload["title"]
        task.description = valid_task_payload["description"]
        task.completed = valid_task_payload["completed"]

    mock_db.refresh.side_effect = mock_refresh

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request
    response = client.post("/api/tasks", json=valid_task_payload)

    # Assertions
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["title"] == valid_task_payload["title"]
    assert response.json()["description"] == valid_task_payload["description"]
    assert "id" in response.json()

    # Verify database interactions
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

    # Cleanup
    app.dependency_overrides.clear()


def test_get_task_success(client, mock_db, mock_task_model):
    """
    Test successful task retrieval (Happy Path).

    Expected:
    - Status: 200 OK
    - Response contains task data
    """
    from app.main import app
    from app.database import get_db

    # Configure mock database query
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_task_model
    mock_db.query.return_value = mock_query

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request
    response = client.get(f"/api/tasks/{mock_task_model.id}")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == mock_task_model.id
    assert response.json()["title"] == mock_task_model.title

    # Cleanup
    app.dependency_overrides.clear()


# ============================================================================
# Test Case 2: Validation Error (422 Unprocessable Entity)
# ============================================================================

def test_create_task_validation_error(client, mock_db, invalid_task_payload):
    """
    Test task creation with invalid payload (Validation Error).

    Expected:
    - Status: 422 Unprocessable Entity
    - Response contains validation error details
    - Database not touched
    """
    from app.main import app
    from app.database import get_db

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request with invalid payload
    response = client.post("/api/tasks", json=invalid_task_payload)

    # Assertions
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()

    # Verify database was NOT touched (no add/commit calls)
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()

    # Cleanup
    app.dependency_overrides.clear()


def test_update_task_validation_error(client, mock_db):
    """
    Test task update with invalid data type.

    Expected:
    - Status: 422 Unprocessable Entity
    - Response contains validation error
    """
    from app.main import app
    from app.database import get_db

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Invalid payload (completed should be boolean, not string)
    invalid_update = {
        "completed": "not-a-boolean",
    }

    response = client.patch("/api/tasks/1", json=invalid_update)

    # Assertions
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Cleanup
    app.dependency_overrides.clear()


# ============================================================================
# Test Case 3: Logic Error / Edge Case (404 / 500)
# ============================================================================

def test_get_task_not_found(client, mock_db):
    """
    Test retrieving non-existent task (Logic Error - 404).

    Expected:
    - Status: 404 Not Found
    - Response contains error message
    """
    from app.main import app
    from app.database import get_db

    # Configure mock database to return None (task not found)
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db.query.return_value = mock_query

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request for non-existent task
    response = client.get("/api/tasks/99999")

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()

    # Cleanup
    app.dependency_overrides.clear()


def test_delete_task_not_found(client, mock_db):
    """
    Test deleting non-existent task (Logic Error - 404).

    Expected:
    - Status: 404 Not Found
    - Database not modified
    """
    from app.main import app
    from app.database import get_db

    # Configure mock database to return None
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = None
    mock_db.query.return_value = mock_query

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request
    response = client.delete("/api/tasks/99999")

    # Assertions
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Verify database commit was NOT called
    mock_db.commit.assert_not_called()

    # Cleanup
    app.dependency_overrides.clear()


def test_create_task_database_error(client, mock_db, valid_task_payload):
    """
    Test database error during task creation (Edge Case - 500).

    Expected:
    - Status: 500 Internal Server Error
    - Response contains error message
    """
    from app.main import app
    from app.database import get_db

    # Configure mock database to raise exception on commit
    mock_db.add = MagicMock()
    mock_db.commit.side_effect = Exception("Database connection failed")

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request
    response = client.post("/api/tasks", json=valid_task_payload)

    # Assertions
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in response.json()

    # Cleanup
    app.dependency_overrides.clear()


# ============================================================================
# Additional Edge Cases (Optional but Recommended)
# ============================================================================

def test_get_tasks_empty_list(client, mock_db):
    """
    Test retrieving tasks when database is empty.

    Expected:
    - Status: 200 OK
    - Response contains empty list
    """
    from app.main import app
    from app.database import get_db

    # Configure mock database to return empty list
    mock_query = MagicMock()
    mock_query.all.return_value = []
    mock_db.query.return_value = mock_query

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request
    response = client.get("/api/tasks")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

    # Cleanup
    app.dependency_overrides.clear()


@pytest.mark.parametrize("task_id", [0, -1, -999])
def test_get_task_invalid_id(client, mock_db, task_id):
    """
    Test retrieving task with invalid ID (negative or zero).

    Expected:
    - Status: 404 Not Found or 422 Unprocessable Entity
    """
    from app.main import app
    from app.database import get_db

    # Override database dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Make request
    response = client.get(f"/api/tasks/{task_id}")

    # Assertions (depending on your validation logic)
    assert response.status_code in [
        status.HTTP_404_NOT_FOUND,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
    ]

    # Cleanup
    app.dependency_overrides.clear()
