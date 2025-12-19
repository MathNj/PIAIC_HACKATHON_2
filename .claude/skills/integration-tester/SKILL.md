---
name: "integration-tester"
description: "Creates comprehensive integration tests for API endpoints, frontend-backend communication, database operations, and third-party services. Use when testing component interactions, E2E workflows, or validating system integration."
version: "1.0.0"
---

# Integration Tester Skill

## When to Use
- User says "Create integration tests for..." or "Test the integration between..."
- New feature needs integration testing
- API endpoints need end-to-end validation
- Frontend-backend integration needs verification
- Database transactions and operations need testing
- Third-party service integrations need testing
- After CRUD or endpoint creation

## Context
This skill creates integration tests for the Todo App:
- **Backend**: pytest with TestClient for API testing
- **Frontend**: Jest + React Testing Library for component integration
- **E2E**: Playwright for full-stack testing
- **Database**: Transaction rollback for test isolation
- **Authentication**: JWT token fixtures for authenticated tests

## Workflow

### 1. Identify Integration Scope
- **API Integration**: Backend endpoint with database
- **Frontend-Backend**: React components calling APIs
- **Component Integration**: Multiple React components working together
- **E2E**: Full user workflow from UI to database
- **Third-Party**: External service integration

### 2. Set Up Test Environment
- Database fixtures
- Authentication tokens
- Mock data
- Test configuration

### 3. Write Integration Tests
- Happy path scenarios
- Error scenarios
- Edge cases
- Data validation

### 4. Run and Validate
- Execute tests
- Check coverage
- Verify assertions

## Output Format

### Backend API Integration Tests (pytest)

**Location**: `backend/tests/integration/test_[feature].py`

**Template**:
```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.main import app
from app.database import get_session
from app.models.task import Task
from app.models.user import User

# Test database setup
@pytest.fixture(name="session", scope="function")
def session_fixture():
    """Create a fresh database for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client", scope="function")
def client_fixture(session: Session):
    """Create test client with database dependency override."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(session: Session):
    """Create a test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Generate JWT token for test user."""
    from app.auth import create_access_token
    return create_access_token(str(test_user.id))

@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}

# Integration Tests
class TestTaskIntegration:
    """Integration tests for Task API with database."""

    def test_create_task_flow(self, client: TestClient, auth_headers, session: Session):
        """Test complete task creation flow."""
        # Create task via API
        payload = {
            "title": "Integration Test Task",
            "description": "Testing full flow",
            "priority": "high"
        }
        response = client.post("/tasks/", json=payload, headers=auth_headers)

        # Verify API response
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["id"] is not None

        # Verify database persistence
        task = session.get(Task, data["id"])
        assert task is not None
        assert task.title == payload["title"]
        assert task.status == "pending"  # Default status

    def test_update_task_flow(self, client: TestClient, auth_headers, session: Session, test_user):
        """Test complete task update flow."""
        # Create initial task in database
        task = Task(
            user_id=test_user.id,
            title="Original Title",
            status="pending"
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Update via API
        update_payload = {
            "title": "Updated Title",
            "status": "completed"
        }
        response = client.patch(f"/tasks/{task.id}", json=update_payload, headers=auth_headers)

        # Verify API response
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "completed"

        # Verify database changes
        session.refresh(task)
        assert task.title == "Updated Title"
        assert task.status == "completed"

    def test_list_tasks_with_pagination(self, client: TestClient, auth_headers, session: Session, test_user):
        """Test task listing with pagination integration."""
        # Create multiple tasks in database
        tasks = [
            Task(user_id=test_user.id, title=f"Task {i}", status="pending")
            for i in range(25)
        ]
        for task in tasks:
            session.add(task)
        session.commit()

        # Test page 1
        response = client.get("/tasks/?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1

        # Test page 2
        response = client.get("/tasks/?page=2&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 2

        # Test page 3 (partial)
        response = client.get("/tasks/?page=3&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 3

    def test_user_isolation(self, client: TestClient, auth_headers, session: Session):
        """Test that users can only access their own tasks."""
        # Create tasks for different users
        user1_id = uuid4()
        user2_id = uuid4()

        task1 = Task(user_id=user1_id, title="User 1 Task", status="pending")
        task2 = Task(user_id=user2_id, title="User 2 Task", status="pending")
        session.add(task1)
        session.add(task2)
        session.commit()

        # User 1 tries to access User 2's task
        # (auth_headers should have user1_id from fixture)
        response = client.get(f"/tasks/{task2.id}", headers=auth_headers)
        assert response.status_code == 404  # Should not find other user's task

    def test_cascade_delete_with_relationships(self, client: TestClient, auth_headers, session: Session, test_user):
        """Test cascading deletion of related entities."""
        # Create task with comments
        from app.models.comment import Comment

        task = Task(user_id=test_user.id, title="Task with Comments", status="pending")
        session.add(task)
        session.commit()
        session.refresh(task)

        # Add comments
        comments = [
            Comment(user_id=test_user.id, task_id=task.id, content=f"Comment {i}")
            for i in range(3)
        ]
        for comment in comments:
            session.add(comment)
        session.commit()

        # Delete task via API
        response = client.delete(f"/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify task is deleted
        assert session.get(Task, task.id) is None

        # Verify comments are deleted (if cascade configured)
        from sqlmodel import select
        comment_query = select(Comment).where(Comment.task_id == task.id)
        remaining_comments = session.exec(comment_query).all()
        assert len(remaining_comments) == 0
```

### Frontend Integration Tests (Jest + React Testing Library)

**Location**: `frontend/__tests__/integration/[feature].test.tsx`

**Template**:
```typescript
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { rest } from 'msw'
import { setupServer } from 'msw/node'
import TaskList from '@/components/TaskList'
import { TaskProvider } from '@/contexts/TaskContext'

// Mock API server
const server = setupServer(
  rest.get('/api/tasks/', (req, res, ctx) => {
    return res(ctx.json({
      items: [
        { id: 1, title: 'Test Task 1', status: 'pending', priority: 'high' },
        { id: 2, title: 'Test Task 2', status: 'completed', priority: 'normal' },
      ],
      total: 2,
      page: 1,
      page_size: 20
    }))
  }),

  rest.post('/api/tasks/', (req, res, ctx) => {
    const body = req.body as any
    return res(ctx.status(201), ctx.json({
      id: 3,
      ...body,
      status: 'pending',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }))
  }),

  rest.patch('/api/tasks/:id', (req, res, ctx) => {
    const { id } = req.params
    const body = req.body as any
    return res(ctx.json({
      id: Number(id),
      ...body,
      updated_at: new Date().toISOString()
    }))
  }),

  rest.delete('/api/tasks/:id', (req, res, ctx) => {
    return res(ctx.status(204))
  })
)

beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

describe('TaskList Integration', () => {
  it('fetches and displays tasks from API', async () => {
    render(
      <TaskProvider>
        <TaskList />
      </TaskProvider>
    )

    // Wait for API call and rendering
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument()
      expect(screen.getByText('Test Task 2')).toBeInTheDocument()
    })
  })

  it('creates new task and updates list', async () => {
    const user = userEvent.setup()

    render(
      <TaskProvider>
        <TaskList />
      </TaskProvider>
    )

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument()
    })

    // Fill in new task form
    const titleInput = screen.getByLabelText(/task title/i)
    const submitButton = screen.getByRole('button', { name: /add task/i })

    await user.type(titleInput, 'New Integration Task')
    await user.click(submitButton)

    // Wait for API call and UI update
    await waitFor(() => {
      expect(screen.getByText('New Integration Task')).toBeInTheDocument()
    })
  })

  it('updates task status and reflects in UI', async () => {
    const user = userEvent.setup()

    render(
      <TaskProvider>
        <TaskList />
      </TaskProvider>
    )

    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument()
    })

    // Click complete button for first task
    const completeButtons = screen.getAllByRole('button', { name: /complete/i })
    await user.click(completeButtons[0])

    // Wait for API call and UI update
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toHaveClass('completed')
    })
  })

  it('handles API errors gracefully', async () => {
    // Override handler to return error
    server.use(
      rest.get('/api/tasks/', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ detail: 'Server error' }))
      })
    )

    render(
      <TaskProvider>
        <TaskList />
      </TaskProvider>
    )

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/error loading tasks/i)).toBeInTheDocument()
    })
  })
})
```

### E2E Tests (Playwright)

**Location**: `e2e/[feature].spec.ts`

**Template**:
```typescript
import { test, expect } from '@playwright/test'

test.describe('Task Management E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('http://localhost:3000/login')
    await page.fill('[name="email"]', 'test@example.com')
    await page.fill('[name="password"]', 'password123')
    await page.click('button[type="submit"]')
    await page.waitForURL('http://localhost:3000/tasks')
  })

  test('complete task workflow', async ({ page }) => {
    // Navigate to tasks page
    await page.goto('http://localhost:3000/tasks')

    // Create new task
    await page.click('button:has-text("New Task")')
    await page.fill('[name="title"]', 'E2E Test Task')
    await page.fill('[name="description"]', 'Testing complete workflow')
    await page.selectOption('[name="priority"]', 'high')
    await page.click('button:has-text("Save")')

    // Verify task appears in list
    await expect(page.locator('text=E2E Test Task')).toBeVisible()

    // Mark as completed
    await page.click('[aria-label="Complete task"]')
    await expect(page.locator('.task-status')).toContainText('Completed')

    // Edit task
    await page.click('[aria-label="Edit task"]')
    await page.fill('[name="title"]', 'E2E Test Task (Updated)')
    await page.click('button:has-text("Save")')
    await expect(page.locator('text=E2E Test Task (Updated)')).toBeVisible()

    // Delete task
    await page.click('[aria-label="Delete task"]')
    await page.click('button:has-text("Confirm")')
    await expect(page.locator('text=E2E Test Task (Updated)')).not.toBeVisible()
  })

  test('task filtering and search', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks')

    // Filter by status
    await page.selectOption('[name="status"]', 'pending')
    await expect(page.locator('.task-item')).not.toContainText('Completed')

    // Search tasks
    await page.fill('[name="search"]', 'groceries')
    await page.keyboard.press('Enter')
    await expect(page.locator('.task-item')).toContainText('groceries')
  })

  test('pagination', async ({ page }) => {
    await page.goto('http://localhost:3000/tasks')

    // Check pagination controls
    const nextButton = page.locator('button:has-text("Next")')
    await nextButton.click()

    // Verify page changed
    await expect(page.locator('[aria-label="Current page"]')).toContainText('2')

    // Go back
    await page.click('button:has-text("Previous")')
    await expect(page.locator('[aria-label="Current page"]')).toContainText('1')
  })
})
```

## Examples

### Example 1: Authentication Flow Integration Test

```python
# backend/tests/integration/test_auth_flow.py

def test_complete_authentication_flow(client: TestClient, session: Session):
    """Test complete registration → login → authenticated request flow."""

    # Step 1: Register new user
    register_payload = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
        "name": "New User"
    }
    register_response = client.post("/auth/register", json=register_payload)
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["email"] == register_payload["email"]

    # Step 2: Login
    login_payload = {
        "email": "newuser@example.com",
        "password": "SecurePass123!"
    }
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data

    # Step 3: Use token for authenticated request
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "newuser@example.com"

    # Step 4: Create task with authentication
    task_payload = {"title": "Authenticated Task", "priority": "normal"}
    task_response = client.post("/tasks/", json=task_payload, headers=headers)
    assert task_response.status_code == 201
    assert task_response.json()["user_id"] == me_data["id"]
```

### Example 2: Database Transaction Rollback Test

```python
def test_transaction_rollback_on_error(client: TestClient, session: Session, test_user):
    """Test that database changes are rolled back on error."""

    # Create initial task
    initial_count = session.query(Task).count()

    # Attempt to create task with invalid data (should fail validation)
    invalid_payload = {
        "title": "",  # Empty title should fail validation
        "priority": "invalid_priority"  # Invalid enum
    }

    response = client.post("/tasks/", json=invalid_payload)
    assert response.status_code == 422

    # Verify no task was created (transaction rolled back)
    final_count = session.query(Task).count()
    assert final_count == initial_count
```

## Quality Checklist

Before finalizing integration tests:
- [ ] Database fixtures set up correctly
- [ ] Authentication fixtures available
- [ ] Test isolation (each test independent)
- [ ] Happy path covered
- [ ] Error scenarios tested
- [ ] Edge cases handled
- [ ] Transaction rollback tested
- [ ] User isolation verified
- [ ] API mock server configured (frontend tests)
- [ ] E2E tests cover full user workflows
- [ ] Tests run consistently (no flakiness)
- [ ] Coverage metrics tracked

## Common Patterns

### 1. Test Data Factory
```python
class TaskFactory:
    """Factory for creating test tasks."""

    @staticmethod
    def create(session: Session, **kwargs):
        defaults = {
            "user_id": uuid4(),
            "title": "Test Task",
            "status": "pending",
            "priority": "normal"
        }
        task = Task(**{**defaults, **kwargs})
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
```

### 2. API Client Helper
```python
class AuthenticatedClient:
    """Helper for making authenticated API requests."""

    def __init__(self, client: TestClient, token: str):
        self.client = client
        self.headers = {"Authorization": f"Bearer {token}"}

    def get(self, url: str, **kwargs):
        return self.client.get(url, headers=self.headers, **kwargs)

    def post(self, url: str, **kwargs):
        return self.client.post(url, headers=self.headers, **kwargs)
```

### 3. Wait for Condition
```python
import time

def wait_for_condition(condition_fn, timeout=5, interval=0.1):
    """Wait for a condition to become true."""
    start = time.time()
    while time.time() - start < timeout:
        if condition_fn():
            return True
        time.sleep(interval)
    return False
```

## Post-Creation

After creating integration tests:
1. **Run Tests**: `pytest backend/tests/integration/ -v`
2. **Check Coverage**: `pytest --cov=app --cov-report=html`
3. **Fix Failures**: Debug and fix any failing tests
4. **Add to CI/CD**: Include in GitHub Actions workflow
5. **Document**: Update TESTING.md with integration test info
6. **Create PHR**: Document test creation process
