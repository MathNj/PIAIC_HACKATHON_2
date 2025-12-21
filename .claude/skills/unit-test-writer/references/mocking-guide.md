# Database Mocking Guide

Comprehensive guide to mocking databases and external services in pytest.

## Table of Contents
- Database Session Mocking
- SQLAlchemy/SQLModel Mocking
- FastAPI Dependency Injection Mocking
- Async Database Mocking
- External Service Mocking
- Common Patterns and Pitfalls

## Database Session Mocking

### Basic Session Mock

```python
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy session."""
    mock_session = MagicMock(spec=Session)
    return mock_session
```

### Query Chain Mocking

```python
def test_get_user(mock_db_session):
    # Configure mock query chain
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.email = "test@example.com"

    # Setup query chain: db.query(User).filter(...).first()
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user

    mock_db_session.query.return_value = mock_query

    # Test code
    result = get_user_by_id(mock_db_session, user_id=1)
    assert result.email == "test@example.com"
```

### Multiple Query Results

```python
def test_get_all_users(mock_db_session):
    # Mock multiple results
    mock_users = [
        MagicMock(id=1, email="user1@example.com"),
        MagicMock(id=2, email="user2@example.com"),
    ]

    mock_query = MagicMock()
    mock_query.all.return_value = mock_users

    mock_db_session.query.return_value = mock_query

    # Test code
    result = get_all_users(mock_db_session)
    assert len(result) == 2
```

## SQLAlchemy/SQLModel Mocking

### Mocking Add/Commit/Refresh

```python
def test_create_user(mock_db_session):
    # Mock the add, commit, refresh cycle
    mock_db_session.add = MagicMock()
    mock_db_session.commit = MagicMock()
    mock_db_session.refresh = MagicMock()

    # Configure refresh to populate the ID
    def mock_refresh(obj):
        obj.id = 1

    mock_db_session.refresh.side_effect = mock_refresh

    # Test code
    user = create_user(mock_db_session, email="test@example.com")

    # Verify database interactions
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    assert user.id == 1
```

### Mocking Delete

```python
def test_delete_user(mock_db_session):
    # Mock user to delete
    mock_user = MagicMock()
    mock_user.id = 1

    # Configure query to return user
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user
    mock_db_session.query.return_value = mock_query

    # Mock delete and commit
    mock_db_session.delete = MagicMock()
    mock_db_session.commit = MagicMock()

    # Test code
    delete_user(mock_db_session, user_id=1)

    # Verify delete was called
    mock_db_session.delete.assert_called_once_with(mock_user)
    mock_db_session.commit.assert_called_once()
```

### Mocking Complex Filters

```python
def test_filter_users_by_criteria(mock_db_session):
    # Mock users matching filter
    mock_users = [MagicMock(id=1, is_active=True)]

    # Setup complex query chain
    mock_query = MagicMock()
    mock_filter1 = MagicMock()
    mock_filter2 = MagicMock()

    # Chain: db.query(User).filter(a).filter(b).all()
    mock_db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter1
    mock_filter1.filter.return_value = mock_filter2
    mock_filter2.all.return_value = mock_users

    # Test code
    result = get_active_users_by_role(mock_db_session, role="admin")
    assert len(result) == 1
```

## FastAPI Dependency Injection Mocking

### Basic Dependency Override

```python
def test_endpoint_with_db_dependency(client, mock_db):
    from app.main import app
    from app.database import get_db

    # Override the dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Configure mock behavior
    mock_user = MagicMock(id=1, email="test@example.com")
    mock_query = MagicMock()
    mock_query.filter.return_value.first.return_value = mock_user
    mock_db.query.return_value = mock_query

    # Make request
    response = client.get("/users/1")

    # Assertions
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    # Cleanup
    app.dependency_overrides.clear()
```

### Multiple Dependency Overrides

```python
def test_endpoint_with_multiple_dependencies(client):
    from app.main import app
    from app.dependencies import get_db, get_current_user

    mock_db = MagicMock()
    mock_user = MagicMock(id=1, is_admin=True)

    # Override both dependencies
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Test code
    response = client.post("/admin/action")
    assert response.status_code == 200

    # Cleanup
    app.dependency_overrides.clear()
```

### Autouse Cleanup Fixture

```python
@pytest.fixture(autouse=True)
def clear_overrides():
    """Automatically clear dependency overrides after each test."""
    yield
    from app.main import app
    app.dependency_overrides.clear()

# Now you don't need manual cleanup in each test
def test_endpoint(client, mock_db):
    from app.main import app
    from app.database import get_db

    app.dependency_overrides[get_db] = lambda: mock_db
    # Test code here
    # Cleanup happens automatically
```

## Async Database Mocking

### AsyncMock for Async Sessions

```python
from unittest.mock import AsyncMock
import pytest

@pytest.fixture
def mock_async_db():
    """Mock async database session."""
    return AsyncMock()

@pytest.mark.asyncio
async def test_async_query(mock_async_db):
    # Configure async mock
    mock_user = MagicMock(id=1, email="test@example.com")

    # Setup async query chain
    mock_result = AsyncMock()
    mock_result.first.return_value = mock_user

    mock_async_db.execute.return_value = mock_result

    # Test code
    result = await get_user_async(mock_async_db, user_id=1)
    assert result.email == "test@example.com"
```

### Async Context Manager Mocking

```python
@pytest.mark.asyncio
async def test_async_transaction():
    mock_session = AsyncMock()

    # Mock async context manager
    mock_session.__aenter__.return_value = mock_session
    mock_session.__aexit__.return_value = None

    async with mock_session as session:
        # Test code
        await session.commit()

    mock_session.commit.assert_called_once()
```

## External Service Mocking

### HTTP Requests Mocking

```python
from unittest.mock import patch

@patch('requests.get')
def test_external_api_call(mock_get):
    # Configure mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    mock_get.return_value = mock_response

    # Test code
    result = fetch_external_data()
    assert result["data"] == "test"

    # Verify API was called
    mock_get.assert_called_once()
```

### Async HTTP Requests

```python
@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_async_http(mock_get):
    # Configure async mock
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"data": "test"}

    # Mock context manager
    mock_get.return_value.__aenter__.return_value = mock_response

    # Test code
    result = await fetch_data_async()
    assert result["data"] == "test"
```

### Environment Variables

```python
@patch.dict('os.environ', {'API_KEY': 'test_key'})
def test_with_env_vars():
    # Test code that uses os.environ['API_KEY']
    result = get_api_key()
    assert result == 'test_key'
```

## Common Patterns and Pitfalls

### Pattern: Side Effects for Stateful Mocking

```python
def test_create_and_update(mock_db_session):
    created_user = None

    def mock_add(obj):
        nonlocal created_user
        created_user = obj

    def mock_refresh(obj):
        obj.id = 1

    mock_db_session.add.side_effect = mock_add
    mock_db_session.refresh.side_effect = mock_refresh
    mock_db_session.commit = MagicMock()

    # Test create
    user = create_user(mock_db_session, email="test@example.com")
    assert user.id == 1

    # Test update (uses same mock)
    assert created_user is not None
```

### Pattern: Testing Database Errors

```python
def test_database_error_handling(mock_db_session):
    # Make commit raise an exception
    mock_db_session.commit.side_effect = Exception("Database error")

    # Test code should handle exception
    with pytest.raises(DatabaseError):
        create_user(mock_db_session, email="test@example.com")

    # Verify rollback was called
    mock_db_session.rollback.assert_called_once()
```

### Pitfall: Forgetting to Configure return_value

```python
# ❌ WRONG - query returns MagicMock, not actual result
def test_wrong():
    mock_db = MagicMock()
    result = mock_db.query(User).all()  # Returns MagicMock!
    assert len(result) == 0  # This will FAIL

# ✅ CORRECT - Configure the return value
def test_correct():
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.all.return_value = []
    mock_db.query.return_value = mock_query

    result = mock_db.query(User).all()
    assert len(result) == 0  # This PASSES
```

### Pitfall: Not Clearing Dependency Overrides

```python
# ❌ WRONG - Overrides leak to other tests
def test_a(client, mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    # ... test code ...
    # Missing cleanup!

def test_b(client):
    # This test will use mock_db from test_a!
    response = client.get("/users")

# ✅ CORRECT - Always cleanup
def test_a(client, mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    # ... test code ...
    app.dependency_overrides.clear()
```

### Pitfall: Over-Mocking

```python
# ❌ WRONG - Mocking too much (testing the mock, not the code)
def test_over_mocked():
    mock_user = MagicMock()
    mock_user.get_full_name.return_value = "Test User"

    # This test is useless - just testing the mock!
    assert mock_user.get_full_name() == "Test User"

# ✅ CORRECT - Mock only external dependencies
def test_correct(mock_db):
    # Mock only the database
    mock_db.query(...).first.return_value = User(
        first_name="Test",
        last_name="User"
    )

    # Test the actual business logic
    user = get_user(mock_db, user_id=1)
    assert user.get_full_name() == "Test User"  # Tests real method
```

## Quick Reference

### Mock Database Query Patterns

```python
# Get single record
mock_db.query.return_value.filter.return_value.first.return_value = obj

# Get all records
mock_db.query.return_value.all.return_value = [obj1, obj2]

# Get none (not found)
mock_db.query.return_value.filter.return_value.first.return_value = None

# Create (add/commit/refresh)
mock_db.add = MagicMock()
mock_db.commit = MagicMock()
mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)

# Update (commit)
mock_db.commit = MagicMock()

# Delete
mock_db.delete = MagicMock()
mock_db.commit = MagicMock()

# Error simulation
mock_db.commit.side_effect = Exception("DB Error")
```
