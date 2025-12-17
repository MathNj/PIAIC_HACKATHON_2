# Test Builder Skill

## Metadata
```yaml
name: test-builder
description: Builds comprehensive test suites including unit tests, integration tests, and E2E tests for backend (pytest) and frontend (Jest, Playwright). Implements test fixtures, mocks, and coverage reporting.
version: 1.0.0
category: testing
tags: [testing, pytest, jest, playwright, unit-tests, integration-tests, e2e, tdd, test-coverage]
dependencies: [pytest, jest, playwright, pytest-cov, testing-library]
```

## When to Use This Skill

Use this skill when:
- User says "Write tests" or "Create test suite"
- Need to test new features or APIs
- Implementing TDD (Test-Driven Development)
- Need to increase code coverage
- Building integration tests for API endpoints
- Creating E2E tests for user flows
- Setting up test fixtures and mocks
- Phase II/III: Testing backend and frontend code

## What This Skill Provides

### 1. Test Types
- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test API endpoints with database
- **E2E Tests**: Test complete user flows (browser automation)
- **Contract Tests**: Validate API request/response schemas
- **Performance Tests**: Load testing and benchmarking

### 2. Backend Testing (pytest)
- **Test fixtures**: Database setup/teardown, test data
- **Mocking**: Mock external APIs, services
- **Test client**: FastAPI TestClient for endpoint testing
- **Database fixtures**: Isolated test database, transactions
- **Authentication**: Mock JWT tokens for protected routes

### 3. Frontend Testing (Jest + Testing Library)
- **Component tests**: React component rendering and behavior
- **Hook tests**: Custom React hooks
- **Integration tests**: Component + API integration
- **Snapshot tests**: UI regression testing
- **Mock API**: MSW (Mock Service Worker) for API mocking

### 4. E2E Testing (Playwright)
- **User flows**: Complete user journeys
- **Cross-browser**: Test on Chrome, Firefox, Safari
- **Visual regression**: Screenshot comparison
- **Network mocking**: Intercept and mock API calls
- **Parallel execution**: Run tests concurrently

### 5. Coverage and Reporting
- **Code coverage**: Line, branch, function coverage
- **Coverage reports**: HTML, JSON, terminal output
- **Thresholds**: Enforce minimum coverage (e.g., 80%)
- **CI/CD integration**: Run tests in pipelines

---

## Installation

### Backend Testing (Python)
```bash
# Using uv (recommended)
uv add --dev pytest pytest-cov pytest-asyncio httpx

# Using pip
pip install pytest pytest-cov pytest-asyncio httpx
```

### Frontend Testing (JavaScript)
```bash
# Jest + Testing Library
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev @testing-library/user-event @testing-library/hooks

# Playwright for E2E
npm install --save-dev @playwright/test
npx playwright install
```

---

## Implementation Examples

### Example 1: Backend Unit Tests (pytest)

```python
"""
Unit tests for task service functions.
"""

import pytest
from datetime import datetime
from app.services.task_service import TaskService
from app.models import Task, TaskStatus, TaskPriority

class TestTaskService:
    """Unit tests for TaskService."""

    def test_create_task(self):
        """Test creating a new task."""
        service = TaskService()

        task_data = {
            "title": "Buy groceries",
            "description": "Get milk and eggs",
            "priority": TaskPriority.HIGH,
            "user_id": 1
        }

        task = service.create_task(task_data)

        assert task.title == "Buy groceries"
        assert task.description == "Get milk and eggs"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.user_id == 1

    def test_create_task_without_description(self):
        """Test creating task without optional description."""
        service = TaskService()

        task_data = {
            "title": "Quick task",
            "user_id": 1
        }

        task = service.create_task(task_data)

        assert task.title == "Quick task"
        assert task.description is None

    def test_create_task_invalid_title(self):
        """Test that empty title raises error."""
        service = TaskService()

        task_data = {
            "title": "",
            "user_id": 1
        }

        with pytest.raises(ValueError, match="Title cannot be empty"):
            service.create_task(task_data)

    def test_update_task_status(self):
        """Test updating task status."""
        service = TaskService()

        # Create task
        task = service.create_task({
            "title": "Test task",
            "user_id": 1
        })

        # Update status
        updated = service.update_task_status(task.id, TaskStatus.IN_PROGRESS)

        assert updated.status == TaskStatus.IN_PROGRESS
        assert updated.updated_at > task.created_at

    def test_calculate_overdue_tasks(self):
        """Test finding overdue tasks."""
        service = TaskService()

        # Create task with past due date
        past_date = datetime(2023, 1, 1)
        task = service.create_task({
            "title": "Overdue task",
            "due_date": past_date,
            "user_id": 1
        })

        overdue = service.get_overdue_tasks(user_id=1)

        assert len(overdue) == 1
        assert overdue[0].id == task.id

    @pytest.mark.parametrize("priority,expected_points", [
        (TaskPriority.LOW, 1),
        (TaskPriority.NORMAL, 3),
        (TaskPriority.HIGH, 5)
    ])
    def test_task_priority_points(self, priority, expected_points):
        """Test task priority point calculation (parameterized)."""
        service = TaskService()

        task = service.create_task({
            "title": "Test",
            "priority": priority,
            "user_id": 1
        })

        points = service.calculate_priority_points(task)
        assert points == expected_points
```

---

### Example 2: Backend Integration Tests (FastAPI + Database)

```python
"""
Integration tests for task API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import User, Task

@pytest.fixture(name="session")
def session_fixture():
    """
    Create test database session.
    Uses in-memory SQLite for fast tests.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create test client with test database."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashedpassword"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(test_user: User):
    """Create authentication headers with JWT token."""
    from app.auth import create_access_token

    token = create_access_token(user_id=test_user.id)
    return {"Authorization": f"Bearer {token}"}


class TestTaskAPI:
    """Integration tests for task endpoints."""

    def test_create_task(self, client: TestClient, auth_headers: dict):
        """Test POST /api/v1/tasks endpoint."""
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "New task",
                "description": "Task description",
                "priority": "high"
            },
            headers=auth_headers
        )

        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "New task"
        assert data["description"] == "Task description"
        assert data["priority"] == "high"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_task_unauthorized(self, client: TestClient):
        """Test that creating task without auth returns 401."""
        response = client.post(
            "/api/v1/tasks",
            json={"title": "New task"}
        )

        assert response.status_code == 401

    def test_create_task_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test validation errors."""
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "",  # Invalid: empty title
                "priority": "invalid"  # Invalid: not in enum
            },
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_list_tasks(self, client: TestClient, auth_headers: dict, session: Session, test_user: User):
        """Test GET /api/v1/tasks endpoint."""
        # Create test tasks
        for i in range(5):
            task = Task(
                title=f"Task {i}",
                user_id=test_user.id
            )
            session.add(task)
        session.commit()

        # List tasks
        response = client.get("/api/v1/tasks", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 5

    def test_list_tasks_with_filter(self, client: TestClient, auth_headers: dict, session: Session, test_user: User):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        task1 = Task(title="Task 1", status="pending", user_id=test_user.id)
        task2 = Task(title="Task 2", status="completed", user_id=test_user.id)
        session.add_all([task1, task2])
        session.commit()

        # Filter by status
        response = client.get(
            "/api/v1/tasks?status=pending",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_get_task(self, client: TestClient, auth_headers: dict, session: Session, test_user: User):
        """Test GET /api/v1/tasks/{id} endpoint."""
        # Create task
        task = Task(title="Test task", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)

        # Get task
        response = client.get(f"/api/v1/tasks/{task.id}", headers=auth_headers)

        assert response.status_code == 200

        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == "Test task"

    def test_get_task_not_found(self, client: TestClient, auth_headers: dict):
        """Test getting non-existent task returns 404."""
        response = client.get("/api/v1/tasks/999", headers=auth_headers)

        assert response.status_code == 404

    def test_update_task(self, client: TestClient, auth_headers: dict, session: Session, test_user: User):
        """Test PATCH /api/v1/tasks/{id} endpoint."""
        # Create task
        task = Task(title="Original", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)

        # Update task
        response = client.patch(
            f"/api/v1/tasks/{task.id}",
            json={"title": "Updated", "status": "completed"},
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated"
        assert data["status"] == "completed"

    def test_delete_task(self, client: TestClient, auth_headers: dict, session: Session, test_user: User):
        """Test DELETE /api/v1/tasks/{id} endpoint."""
        # Create task
        task = Task(title="To delete", user_id=test_user.id)
        session.add(task)
        session.commit()
        session.refresh(task)

        # Delete task
        response = client.delete(f"/api/v1/tasks/{task.id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify deleted
        response = client.get(f"/api/v1/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_user_isolation(self, client: TestClient, session: Session):
        """Test that users can only access their own tasks."""
        # Create two users
        user1 = User(email="user1@test.com", username="user1", hashed_password="hash")
        user2 = User(email="user2@test.com", username="user2", hashed_password="hash")
        session.add_all([user1, user2])
        session.commit()

        # Create task for user1
        task = Task(title="User 1 task", user_id=user1.id)
        session.add(task)
        session.commit()
        session.refresh(task)

        # User2 tries to access user1's task
        from app.auth import create_access_token
        user2_token = create_access_token(user_id=user2.id)
        headers = {"Authorization": f"Bearer {user2_token}"}

        response = client.get(f"/api/v1/tasks/{task.id}", headers=headers)

        assert response.status_code == 404  # or 403
```

---

### Example 3: Frontend Component Tests (Jest + React Testing Library)

```typescript
/**
 * Unit tests for TaskCard component.
 */

import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskCard } from '@/components/TaskCard';
import { Task, TaskStatus, TaskPriority } from '@/types';

describe('TaskCard', () => {
  const mockTask: Task = {
    id: 1,
    title: 'Test Task',
    description: 'Test description',
    status: TaskStatus.PENDING,
    priority: TaskPriority.NORMAL,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z',
  };

  const mockOnComplete = jest.fn();
  const mockOnDelete = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders task information correctly', () => {
    render(<TaskCard task={mockTask} />);

    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test description')).toBeInTheDocument();
  });

  it('displays priority badge with correct color', () => {
    const { rerender } = render(
      <TaskCard task={{ ...mockTask, priority: TaskPriority.HIGH }} />
    );

    const badge = screen.getByText('High');
    expect(badge).toHaveClass('bg-red-100'); // Assuming Tailwind classes

    rerender(<TaskCard task={{ ...mockTask, priority: TaskPriority.LOW }} />);
    expect(screen.getByText('Low')).toHaveClass('bg-green-100');
  });

  it('shows complete button for pending tasks', () => {
    render(<TaskCard task={mockTask} onComplete={mockOnComplete} />);

    const completeButton = screen.getByRole('button', { name: /complete/i });
    expect(completeButton).toBeInTheDocument();
  });

  it('does not show complete button for completed tasks', () => {
    render(
      <TaskCard
        task={{ ...mockTask, status: TaskStatus.COMPLETED }}
        onComplete={mockOnComplete}
      />
    );

    expect(screen.queryByRole('button', { name: /complete/i })).not.toBeInTheDocument();
  });

  it('calls onComplete when complete button is clicked', async () => {
    const user = userEvent.setup();

    render(<TaskCard task={mockTask} onComplete={mockOnComplete} />);

    const completeButton = screen.getByRole('button', { name: /complete/i });
    await user.click(completeButton);

    expect(mockOnComplete).toHaveBeenCalledTimes(1);
    expect(mockOnComplete).toHaveBeenCalledWith(mockTask.id);
  });

  it('calls onDelete when delete button is clicked', async () => {
    const user = userEvent.setup();

    render(<TaskCard task={mockTask} onDelete={mockOnDelete} />);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(mockOnDelete).toHaveBeenCalledTimes(1);
    expect(mockOnDelete).toHaveBeenCalledWith(mockTask.id);
  });

  it('shows confirmation dialog before deleting', async () => {
    const user = userEvent.setup();
    window.confirm = jest.fn(() => true);

    render(<TaskCard task={mockTask} onDelete={mockOnDelete} />);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(window.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete this task?'
    );
  });

  it('does not delete if confirmation is cancelled', async () => {
    const user = userEvent.setup();
    window.confirm = jest.fn(() => false);

    render(<TaskCard task={mockTask} onDelete={mockOnDelete} />);

    const deleteButton = screen.getByRole('button', { name: /delete/i });
    await user.click(deleteButton);

    expect(mockOnDelete).not.toHaveBeenCalled();
  });

  it('renders due date if provided', () => {
    render(
      <TaskCard
        task={{ ...mockTask, dueDate: '2024-12-31T23:59:59Z' }}
      />
    );

    expect(screen.getByText(/due:/i)).toBeInTheDocument();
    expect(screen.getByText(/dec 31, 2024/i)).toBeInTheDocument();
  });

  it('shows overdue indicator for past due dates', () => {
    const pastDate = new Date('2020-01-01').toISOString();

    render(
      <TaskCard
        task={{ ...mockTask, dueDate: pastDate, status: TaskStatus.PENDING }}
      />
    );

    expect(screen.getByText(/overdue/i)).toBeInTheDocument();
  });

  it('matches snapshot', () => {
    const { container } = render(<TaskCard task={mockTask} />);
    expect(container).toMatchSnapshot();
  });
});
```

---

### Example 4: Frontend Integration Tests (API Mocking)

```typescript
/**
 * Integration tests for TaskList page with API mocking.
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { TaskListPage } from '@/app/tasks/page';

// Mock API server
const server = setupServer(
  rest.get('/api/v1/tasks', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: 1,
          title: 'Task 1',
          status: 'pending',
          priority: 'normal',
        },
        {
          id: 2,
          title: 'Task 2',
          status: 'completed',
          priority: 'high',
        },
      ])
    );
  }),

  rest.post('/api/v1/tasks', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: 3,
        title: req.body.title,
        status: 'pending',
        priority: req.body.priority || 'normal',
      })
    );
  }),

  rest.delete('/api/v1/tasks/:id', (req, res, ctx) => {
    return res(ctx.status(204));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('TaskListPage', () => {
  it('fetches and displays tasks', async () => {
    render(<TaskListPage />);

    // Wait for tasks to load
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });
  });

  it('shows loading state while fetching', () => {
    render(<TaskListPage />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('creates new task when form is submitted', async () => {
    const user = userEvent.setup();

    render(<TaskListPage />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    // Fill out form
    const titleInput = screen.getByPlaceholderText(/task title/i);
    await user.type(titleInput, 'New Task');

    const submitButton = screen.getByRole('button', { name: /add task/i });
    await user.click(submitButton);

    // New task should appear in list
    await waitFor(() => {
      expect(screen.getByText('New Task')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    // Override handler to return error
    server.use(
      rest.get('/api/v1/tasks', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ message: 'Server error' }));
      })
    );

    render(<TaskListPage />);

    await waitFor(() => {
      expect(screen.getByText(/error loading tasks/i)).toBeInTheDocument();
    });
  });

  it('filters tasks by status', async () => {
    const user = userEvent.setup();

    render(<TaskListPage />);

    await waitFor(() => {
      expect(screen.getByText('Task 1')).toBeInTheDocument();
    });

    // Click completed filter
    const completedFilter = screen.getByRole('button', { name: /completed/i });
    await user.click(completedFilter);

    // Update mock to return only completed
    server.use(
      rest.get('/api/v1/tasks', (req, res, ctx) => {
        const status = req.url.searchParams.get('status');
        if (status === 'completed') {
          return res(
            ctx.status(200),
            ctx.json([
              { id: 2, title: 'Task 2', status: 'completed', priority: 'high' },
            ])
          );
        }
      })
    );

    // Should only show completed task
    await waitFor(() => {
      expect(screen.queryByText('Task 1')).not.toBeInTheDocument();
      expect(screen.getByText('Task 2')).toBeInTheDocument();
    });
  });
});
```

---

### Example 5: E2E Tests (Playwright)

```typescript
/**
 * End-to-end tests for task management flow.
 */

import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button:has-text("Login")');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');
  });

  test('complete task workflow', async ({ page }) => {
    // Navigate to tasks page
    await page.goto('/tasks');

    // Create new task
    await page.fill('[placeholder="Task title"]', 'E2E Test Task');
    await page.selectOption('[name="priority"]', 'high');
    await page.click('button:has-text("Add Task")');

    // Verify task appears in list
    await expect(page.locator('text=E2E Test Task')).toBeVisible();

    // Complete the task
    await page.click('[data-testid="task-1"] button:has-text("Complete")');

    // Verify status changed
    await expect(page.locator('[data-testid="task-1"] [data-status="completed"]')).toBeVisible();

    // Delete the task
    await page.click('[data-testid="task-1"] button:has-text("Delete")');
    await page.click('button:has-text("Confirm")');

    // Verify task removed
    await expect(page.locator('text=E2E Test Task')).not.toBeVisible();
  });

  test('filter tasks by priority', async ({ page }) => {
    await page.goto('/tasks');

    // Create tasks with different priorities
    const tasks = [
      { title: 'Low Priority Task', priority: 'low' },
      { title: 'High Priority Task', priority: 'high' },
    ];

    for (const task of tasks) {
      await page.fill('[placeholder="Task title"]', task.title);
      await page.selectOption('[name="priority"]', task.priority);
      await page.click('button:has-text("Add Task")');
    }

    // Filter by high priority
    await page.click('button:has-text("High Priority")');

    // Should show only high priority task
    await expect(page.locator('text=High Priority Task')).toBeVisible();
    await expect(page.locator('text=Low Priority Task')).not.toBeVisible();

    // Clear filter
    await page.click('button:has-text("All")');

    // Should show all tasks
    await expect(page.locator('text=High Priority Task')).toBeVisible();
    await expect(page.locator('text=Low Priority Task')).toBeVisible();
  });

  test('search tasks', async ({ page }) => {
    await page.goto('/tasks');

    // Create test task
    await page.fill('[placeholder="Task title"]', 'Searchable Task');
    await page.click('button:has-text("Add Task")');

    // Search for task
    await page.fill('[placeholder="Search tasks"]', 'Searchable');

    // Should show matching task
    await expect(page.locator('text=Searchable Task')).toBeVisible();

    // Search for non-existent task
    await page.fill('[placeholder="Search tasks"]', 'Nonexistent');

    // Should show no results
    await expect(page.locator('text=No tasks found')).toBeVisible();
  });

  test('handles offline mode', async ({ page, context }) => {
    await page.goto('/tasks');

    // Go offline
    await context.setOffline(true);

    // Try to create task
    await page.fill('[placeholder="Task title"]', 'Offline Task');
    await page.click('button:has-text("Add Task")');

    // Should show offline error
    await expect(page.locator('text=You are offline')).toBeVisible();

    // Go back online
    await context.setOffline(false);

    // Retry
    await page.click('button:has-text("Retry")');

    // Should succeed
    await expect(page.locator('text=Offline Task')).toBeVisible();
  });

  test('responsive design', async ({ page }) => {
    // Desktop view
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('/tasks');
    await expect(page.locator('[data-testid="sidebar"]')).toBeVisible();

    // Mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('[data-testid="sidebar"]')).not.toBeVisible();
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();
  });

  test('takes screenshot on failure', async ({ page }, testInfo) => {
    await page.goto('/tasks');

    try {
      // Intentionally fail
      await expect(page.locator('text=Nonexistent')).toBeVisible();
    } catch (error) {
      // Capture screenshot
      const screenshot = await page.screenshot();
      await testInfo.attach('failure', {
        body: screenshot,
        contentType: 'image/png',
      });
      throw error;
    }
  });
});
```

---

## Test Configuration Files

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v
    -s
markers =
    slow: marks tests as slow
    integration: integration tests
    e2e: end-to-end tests
```

### jest.config.js
```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts?(x)', '**/?(*.)+(spec|test).ts?(x)'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
};
```

### playwright.config.ts
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## CLI Commands

```bash
# Backend Tests (pytest)
pytest                              # Run all tests
pytest tests/test_tasks.py          # Run specific file
pytest -k test_create               # Run tests matching pattern
pytest -m integration               # Run tests with marker
pytest --cov-report=html            # Generate HTML coverage report

# Frontend Tests (Jest)
npm test                            # Run all tests
npm test -- TaskCard                # Run specific test file
npm test -- --coverage              # Run with coverage
npm test -- --watch                 # Watch mode

# E2E Tests (Playwright)
npx playwright test                 # Run all E2E tests
npx playwright test --headed        # Show browser
npx playwright test --debug         # Debug mode
npx playwright show-report          # View test report
```

---

## Best Practices

1. **Test Structure**:
   - Arrange-Act-Assert (AAA) pattern
   - One assertion per test (when possible)
   - Descriptive test names

2. **Coverage**:
   - Aim for 80%+ code coverage
   - Focus on critical paths first
   - Don't test implementation details

3. **Fixtures**:
   - Use fixtures for reusable setup
   - Clean up resources in teardown
   - Isolate test data

4. **Mocking**:
   - Mock external dependencies
   - Don't mock what you don't own
   - Verify mock interactions

5. **E2E Tests**:
   - Test critical user flows
   - Keep tests independent
   - Use data-testid for selectors

---

## Quality Checklist

Before considering tests complete:
- [ ] All new code has unit tests
- [ ] Critical paths have integration tests
- [ ] Main user flows have E2E tests
- [ ] Coverage meets threshold (80%+)
- [ ] All tests pass in CI/CD
- [ ] Tests are fast (< 10s for unit, < 60s for integration)
- [ ] Test data isolated per test
- [ ] No flaky tests
- [ ] Error cases tested
- [ ] Edge cases covered

This skill enables comprehensive test coverage for both backend and frontend code, ensuring quality and preventing regressions.
