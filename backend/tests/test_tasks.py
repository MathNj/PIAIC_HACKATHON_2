"""
Tests for task CRUD operations.

Tests cover:
- List tasks (with filtering and sorting)
- Create task
- Get task by ID
- Update task
- Delete task
- Toggle task completion
- Authorization and data isolation
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User
from app.models.task import Task


@pytest.mark.tasks
class TestListTasks:
    """Tests for GET /api/{user_id}/tasks endpoint."""

    def test_list_tasks_empty(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test listing tasks when user has no tasks."""
        response = client.get(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_list_tasks_with_data(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test listing tasks returns user's tasks."""
        response = client.get(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Test Task"
        assert tasks[0]["user_id"] == str(test_user.id)

    def test_list_tasks_filter_pending(
        self, client: TestClient, test_user: User, session: Session, auth_headers: dict
    ):
        """Test filtering tasks by pending status."""
        # Create completed and pending tasks
        completed_task = Task(
            user_id=test_user.id, title="Completed", completed=True
        )
        pending_task = Task(
            user_id=test_user.id, title="Pending", completed=False
        )
        session.add(completed_task)
        session.add(pending_task)
        session.commit()

        response = client.get(
            f"/api/{test_user.id}/tasks?status=pending",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Pending"
        assert tasks[0]["completed"] is False

    def test_list_tasks_filter_completed(
        self, client: TestClient, test_user: User, session: Session, auth_headers: dict
    ):
        """Test filtering tasks by completed status."""
        # Create completed and pending tasks
        completed_task = Task(
            user_id=test_user.id, title="Completed", completed=True
        )
        pending_task = Task(
            user_id=test_user.id, title="Pending", completed=False
        )
        session.add(completed_task)
        session.add(pending_task)
        session.commit()

        response = client.get(
            f"/api/{test_user.id}/tasks?status=completed",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "Completed"
        assert tasks[0]["completed"] is True

    def test_list_tasks_sort_by_title(
        self, client: TestClient, test_user: User, session: Session, auth_headers: dict
    ):
        """Test sorting tasks by title."""
        # Create tasks in random order
        task_c = Task(user_id=test_user.id, title="C Task")
        task_a = Task(user_id=test_user.id, title="A Task")
        task_b = Task(user_id=test_user.id, title="B Task")

        session.add_all([task_c, task_a, task_b])
        session.commit()

        response = client.get(
            f"/api/{test_user.id}/tasks?sort=title",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert tasks[0]["title"] == "A Task"
        assert tasks[1]["title"] == "B Task"
        assert tasks[2]["title"] == "C Task"

    def test_list_tasks_user_isolation(
        self,
        client: TestClient,
        test_user: User,
        second_user: User,
        session: Session,
        auth_headers: dict
    ):
        """Test users only see their own tasks."""
        # Create tasks for both users
        user1_task = Task(user_id=test_user.id, title="User 1 Task")
        user2_task = Task(user_id=second_user.id, title="User 2 Task")

        session.add_all([user1_task, user2_task])
        session.commit()

        response = client.get(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers
        )

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "User 1 Task"


@pytest.mark.tasks
class TestCreateTask:
    """Tests for POST /api/{user_id}/tasks endpoint."""

    def test_create_task_success(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test creating a new task."""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers,
            json={
                "title": "New Task",
                "description": "Task description"
            }
        )

        assert response.status_code == 201
        task = response.json()

        assert task["title"] == "New Task"
        assert task["description"] == "Task description"
        assert task["completed"] is False
        assert task["user_id"] == str(test_user.id)
        assert "id" in task
        assert "created_at" in task
        assert "updated_at" in task

    def test_create_task_without_description(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test creating task with only title."""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers,
            json={"title": "Minimal Task"}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["title"] == "Minimal Task"
        assert task["description"] is None or task["description"] == ""

    def test_create_task_empty_title(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test creating task with empty title fails."""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers,
            json={"title": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_create_task_title_too_long(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test creating task with title exceeding max length."""
        response = client.post(
            f"/api/{test_user.id}/tasks",
            headers=auth_headers,
            json={"title": "x" * 201}  # Max is 200
        )

        assert response.status_code == 422


@pytest.mark.tasks
class TestGetTask:
    """Tests for GET /api/{user_id}/tasks/{task_id} endpoint."""

    def test_get_task_success(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test getting a task by ID."""
        response = client.get(
            f"/api/{test_user.id}/tasks/{test_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        task = response.json()
        assert task["id"] == test_task.id
        assert task["title"] == "Test Task"

    def test_get_task_not_found(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test getting non-existent task returns 404."""
        response = client.get(
            f"/api/{test_user.id}/tasks/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_get_task_wrong_user(
        self,
        client: TestClient,
        test_user: User,
        second_user: User,
        session: Session,
        auth_headers: dict
    ):
        """Test getting another user's task returns 404."""
        # Create task for second user
        other_task = Task(user_id=second_user.id, title="Other User Task")
        session.add(other_task)
        session.commit()
        session.refresh(other_task)

        # Try to access it with first user's token
        response = client.get(
            f"/api/{test_user.id}/tasks/{other_task.id}",
            headers=auth_headers
        )

        # Should return 404 (don't expose existence)
        assert response.status_code == 404


@pytest.mark.tasks
class TestUpdateTask:
    """Tests for PUT /api/{user_id}/tasks/{task_id} endpoint."""

    def test_update_task_title(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test updating task title."""
        response = client.put(
            f"/api/{test_user.id}/tasks/{test_task.id}",
            headers=auth_headers,
            json={"title": "Updated Title"}
        )

        assert response.status_code == 200
        task = response.json()
        assert task["title"] == "Updated Title"
        assert task["description"] == test_task.description  # Unchanged

    def test_update_task_description(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test updating task description."""
        response = client.put(
            f"/api/{test_user.id}/tasks/{test_task.id}",
            headers=auth_headers,
            json={"description": "Updated description"}
        )

        assert response.status_code == 200
        task = response.json()
        assert task["description"] == "Updated description"

    def test_update_task_completed(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test updating task completion status."""
        response = client.put(
            f"/api/{test_user.id}/tasks/{test_task.id}",
            headers=auth_headers,
            json={"completed": True}
        )

        assert response.status_code == 200
        task = response.json()
        assert task["completed"] is True

    def test_update_task_multiple_fields(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test updating multiple fields at once."""
        response = client.put(
            f"/api/{test_user.id}/tasks/{test_task.id}",
            headers=auth_headers,
            json={
                "title": "New Title",
                "description": "New description",
                "completed": True
            }
        )

        assert response.status_code == 200
        task = response.json()
        assert task["title"] == "New Title"
        assert task["description"] == "New description"
        assert task["completed"] is True


@pytest.mark.tasks
class TestDeleteTask:
    """Tests for DELETE /api/{user_id}/tasks/{task_id} endpoint."""

    def test_delete_task_success(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict, session: Session
    ):
        """Test deleting a task."""
        response = client.delete(
            f"/api/{test_user.id}/tasks/{test_task.id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert "deleted" in response.json()["detail"].lower()

        # Verify task was deleted from database
        task = session.query(Task).filter(Task.id == test_task.id).first()
        assert task is None

    def test_delete_task_not_found(
        self, client: TestClient, test_user: User, auth_headers: dict
    ):
        """Test deleting non-existent task returns 404."""
        response = client.delete(
            f"/api/{test_user.id}/tasks/99999",
            headers=auth_headers
        )

        assert response.status_code == 404


@pytest.mark.tasks
class TestToggleCompletion:
    """Tests for PATCH /api/{user_id}/tasks/{task_id}/complete endpoint."""

    def test_toggle_completion_false_to_true(
        self, client: TestClient, test_user: User, test_task: Task, auth_headers: dict
    ):
        """Test toggling task from incomplete to complete."""
        assert test_task.completed is False

        response = client.patch(
            f"/api/{test_user.id}/tasks/{test_task.id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200
        task = response.json()
        assert task["completed"] is True

    def test_toggle_completion_true_to_false(
        self, client: TestClient, test_user: User, session: Session, auth_headers: dict
    ):
        """Test toggling task from complete to incomplete."""
        # Create completed task
        completed_task = Task(
            user_id=test_user.id,
            title="Completed Task",
            completed=True
        )
        session.add(completed_task)
        session.commit()
        session.refresh(completed_task)

        response = client.patch(
            f"/api/{test_user.id}/tasks/{completed_task.id}/complete",
            headers=auth_headers
        )

        assert response.status_code == 200
        task = response.json()
        assert task["completed"] is False
