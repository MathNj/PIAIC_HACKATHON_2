# TODO API Test Suite

Comprehensive test suite for the TODO API backend using pytest.

## Test Coverage

### Authentication Tests (`test_auth.py`)
- ✅ User signup with validation
- ✅ Password requirements (uppercase, lowercase, number, min length)
- ✅ Duplicate email prevention
- ✅ User login with JWT token generation
- ✅ Invalid credentials handling
- ✅ JWT token validation
- ✅ Protected endpoint authorization
- ✅ User isolation and access control

### Task CRUD Tests (`test_tasks.py`)
- ✅ List tasks (empty, with data, filtering, sorting)
- ✅ Create task (success, validation, missing fields)
- ✅ Get task by ID (success, not found, wrong user)
- ✅ Update task (title, description, completed, multiple fields)
- ✅ Delete task (success, not found)
- ✅ Toggle task completion (false→true, true→false)
- ✅ Multi-user data isolation

## Running Tests

### All Tests
```bash
# Windows
run_tests.bat

# Linux/Mac
./run_tests.sh

# Or directly with pytest
python -m pytest
```

### Specific Test Categories
```bash
# Authentication tests only
python -m pytest -m auth

# Task CRUD tests only
python -m pytest -m tasks

# Integration tests only
python -m pytest -m integration
```

### Verbose Output
```bash
python -m pytest -v

# Very verbose
python -m pytest -vv
```

### With Coverage Report
```bash
# Windows
run_tests.bat --cov

# Linux/Mac
./run_tests.sh --cov

# View HTML coverage report
open htmlcov/index.html  # Linux/Mac
start htmlcov\index.html  # Windows
```

## Test Structure

### Fixtures (`conftest.py`)
- `session` - Fresh in-memory SQLite database for each test
- `client` - FastAPI test client with dependency overrides
- `test_user` - Pre-created test user with known credentials
- `auth_token` - Valid JWT token for test user
- `auth_headers` - Authorization headers with Bearer token
- `test_task` - Pre-created test task
- `second_user` - Second test user for authorization tests

### Test Markers
Tests are organized with pytest markers:
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.tasks` - Task operation tests
- `@pytest.mark.integration` - Integration tests

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Isolated from the production database

## Common Test Patterns

### Testing Protected Endpoints
```python
def test_protected_endpoint(client, test_user, auth_headers):
    response = client.get(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers  # Includes JWT token
    )
    assert response.status_code == 200
```

### Testing Validation
```python
def test_invalid_input(client, test_user, auth_headers):
    response = client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={"title": ""}  # Empty title
    )
    assert response.status_code == 422  # Validation error
```

### Testing Authorization
```python
def test_user_isolation(client, test_user, second_user, auth_headers):
    # Try to access another user's resources
    response = client.get(
        f"/api/{second_user.id}/tasks",
        headers=auth_headers  # First user's token
    )
    assert response.status_code == 403  # Forbidden
```

## Test Results

Latest test run:
```
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-7.4.3, pluggy-1.6.0
collected 37 items

tests/test_auth.py::TestSignup ✓✓✓✓✓✓✓                               [19%]
tests/test_auth.py::TestLogin ✓✓✓✓                                    [29%]
tests/test_auth.py::TestJWTAuthentication ✓✓✓✓✓                       [43%]
tests/test_tasks.py::TestListTasks ✓✓✓✓✓✓                             [59%]
tests/test_tasks.py::TestCreateTask ✓✓✓✓                              [70%]
tests/test_tasks.py::TestGetTask ✓✓✓                                  [78%]
tests/test_tasks.py::TestUpdateTask ✓✓✓✓                              [89%]
tests/test_tasks.py::TestDeleteTask ✓✓                                [94%]
tests/test_tasks.py::TestToggleCompletion ✓✓                          [100%]

====================== 37 passed in 16.23s ===============================
```

## Adding New Tests

1. Create test file in `tests/` directory (prefix with `test_`)
2. Import fixtures from `conftest.py`
3. Use `@pytest.mark` decorators to categorize tests
4. Follow naming convention: `test_<action>_<scenario>`

Example:
```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.tasks
def test_create_task_success(client, test_user, auth_headers):
    response = client.post(
        f"/api/{test_user.id}/tasks",
        headers=auth_headers,
        json={"title": "New Task"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "New Task"
```

## CI/CD Integration

The test scripts can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    python -m pytest --cov=app --cov-report=xml

# GitLab CI example
test:
  script:
    - cd backend
    - pip install -r requirements.txt
    - python -m pytest -v
```

## Troubleshooting

### Tests not found
- Ensure test files are prefixed with `test_`
- Check `pytest.ini` configuration
- Run `pytest --collect-only` to see discovered tests

### Import errors
- Install test dependencies: `pip install -r requirements.txt`
- Check Python path includes project root

### Database errors
- Tests use in-memory SQLite (no setup needed)
- Each test gets fresh database
- Check fixture imports in test files

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLModel testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)
