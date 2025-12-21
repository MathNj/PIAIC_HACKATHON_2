# Pytest Patterns Reference

Advanced pytest patterns for comprehensive test coverage.

## Table of Contents
- Parametrized Tests
- Fixtures and Scopes
- Markers and Test Organization
- Async Testing
- Exception Testing
- Test Coverage Strategies

## Parametrized Tests

Test multiple scenarios with a single test function.

### Basic Parametrization

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("status_code,expected_message", [
    (200, "Success"),
    (404, "Not Found"),
    (500, "Internal Server Error"),
])
def test_http_responses(client, status_code, expected_message):
    response = client.get(f"/endpoint?code={status_code}")
    assert expected_message in response.json()["message"]
```

### Combining Fixtures with Parameters

```python
@pytest.fixture
def user():
    return {"id": 1, "name": "Test User"}

@pytest.mark.parametrize("role", ["admin", "user", "guest"])
def test_user_roles(user, role):
    user["role"] = role
    # Test logic here
```

## Fixtures and Scopes

### Fixture Scopes

```python
# Function scope (default) - runs once per test
@pytest.fixture
def temp_data():
    return {"key": "value"}

# Class scope - runs once per test class
@pytest.fixture(scope="class")
def db_connection():
    conn = setup_connection()
    yield conn
    conn.close()

# Module scope - runs once per module
@pytest.fixture(scope="module")
def expensive_setup():
    data = load_large_dataset()
    return data

# Session scope - runs once per test session
@pytest.fixture(scope="session")
def global_config():
    return load_config()
```

### Fixture Dependencies

```python
@pytest.fixture
def database():
    return MagicMock()

@pytest.fixture
def user_service(database):
    return UserService(database)

def test_create_user(user_service):
    # user_service already has mocked database injected
    result = user_service.create_user("test@example.com")
    assert result is not None
```

### Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_state():
    """Automatically runs before each test."""
    global_state.clear()
    yield
    # Cleanup after test
```

## Markers and Test Organization

### Built-in Markers

```python
# Skip test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

# Skip conditionally
@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_python_310_feature():
    pass

# Expected to fail
@pytest.mark.xfail(reason="Known bug in library")
def test_known_issue():
    assert False
```

### Custom Markers

```python
# In pytest.ini or pyproject.toml:
# [tool.pytest.ini_options]
# markers =
#     slow: marks tests as slow
#     integration: marks tests as integration tests

@pytest.mark.slow
def test_large_dataset():
    # Long-running test
    pass

@pytest.mark.integration
def test_api_integration():
    # Integration test
    pass

# Run only specific markers:
# pytest -m "not slow"
# pytest -m "integration"
```

## Async Testing

### Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    result = await async_function()
    assert result == expected_value
```

### Async Fixtures

```python
@pytest.fixture
async def async_client():
    async with AsyncClient() as client:
        yield client

@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    response = await async_client.get("/endpoint")
    assert response.status_code == 200
```

## Exception Testing

### Testing Expected Exceptions

```python
import pytest
from pydantic import ValidationError

def test_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        Model(invalid_field="bad value")

    # Access exception details
    assert "invalid_field" in str(exc_info.value)

def test_exception_message():
    with pytest.raises(ValueError, match="must be positive"):
        validate_number(-1)
```

### Testing Multiple Exceptions

```python
@pytest.mark.parametrize("input,exception", [
    ("", ValueError),
    (None, TypeError),
    (-1, ValueError),
])
def test_various_exceptions(input, exception):
    with pytest.raises(exception):
        process_input(input)
```

## Test Coverage Strategies

### Boundary Testing

```python
@pytest.mark.parametrize("value", [
    -1,      # Below minimum
    0,       # Minimum
    1,       # Valid
    99,      # Valid
    100,     # Maximum
    101,     # Above maximum
])
def test_value_boundaries(value):
    result = validate_range(value)
    # Assert based on boundary conditions
```

### State Transition Testing

```python
def test_task_state_transitions():
    task = Task(status="pending")

    # Valid transition
    task.start()
    assert task.status == "in_progress"

    # Another valid transition
    task.complete()
    assert task.status == "completed"

    # Invalid transition
    with pytest.raises(InvalidStateError):
        task.start()  # Can't start completed task
```

### Combination Testing

```python
@pytest.mark.parametrize("is_admin,is_active,expected", [
    (True, True, True),    # Admin + Active = Access
    (True, False, False),  # Admin + Inactive = No Access
    (False, True, False),  # User + Active = No Access
    (False, False, False), # User + Inactive = No Access
])
def test_permission_combinations(is_admin, is_active, expected):
    user = User(is_admin=is_admin, is_active=is_active)
    assert user.has_admin_access() == expected
```

## Mocking Best Practices

### Patch Decorators

```python
from unittest.mock import patch

@patch('module.external_api_call')
def test_with_patch(mock_api):
    mock_api.return_value = {"status": "success"}
    result = function_that_calls_api()
    assert result["status"] == "success"
    mock_api.assert_called_once()
```

### Context Manager Mocking

```python
def test_with_context_manager():
    with patch('module.database_connection') as mock_db:
        mock_db.return_value.query.return_value = [{"id": 1}]
        result = get_users()
        assert len(result) == 1
```

### Multiple Patches

```python
@patch('module.service_b')
@patch('module.service_a')
def test_multiple_patches(mock_service_a, mock_service_b):
    # Note: patches are applied bottom-to-top
    mock_service_a.return_value = "A"
    mock_service_b.return_value = "B"
    result = function_using_both_services()
    # Assertions
```

## Test Organization

### Class-Based Tests

```python
class TestUserEndpoints:
    """Group related tests in a class."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db):
        """Runs before each test method."""
        self.db = mock_db

    def test_create_user(self):
        # Test logic
        pass

    def test_get_user(self):
        # Test logic
        pass
```

### Nested Test Classes

```python
class TestTaskAPI:
    class TestCreateTask:
        def test_success(self):
            pass

        def test_validation_error(self):
            pass

    class TestUpdateTask:
        def test_success(self):
            pass

        def test_not_found(self):
            pass
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_create_user

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v

# Run with print statements
pytest -s

# Run only failed tests
pytest --lf

# Run tests matching pattern
pytest -k "test_user"

# Run with specific markers
pytest -m "not slow"

# Stop on first failure
pytest -x
```
