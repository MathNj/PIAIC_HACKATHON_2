---
name: unit-test-writer
description: Generate comprehensive pytest unit tests for FastAPI endpoints and MCP tools with strict database mocking. Use when: (1) Writing unit tests for FastAPI API endpoints, (2) Creating tests for MCP server tools, (3) Testing database operations with mocked sessions, (4) Implementing test coverage for CRUD operations, (5) Ensuring proper validation and error handling in tests, or (6) Setting up pytest fixtures and test infrastructure. Enforces isolation with unittest.mock, minimum 3 test cases per function (Happy Path, Validation Error, Logic Error), and Pydantic schema validation for MCP tools.
---

# Unit Test Writer

Generate comprehensive pytest unit tests for FastAPI endpoints and MCP tools with strict database mocking and quality enforcement.

## Quick Start

### Step 1: Copy Base Fixtures

Copy the shared fixtures template to your test directory:

```bash
cp assets/conftest.template.py tests/conftest.py
```

This provides reusable fixtures:
- `mock_db_session` - Mock SQLAlchemy session
- `mock_db` - Mock database for dependency injection
- `client` - FastAPI TestClient
- `mock_current_user` - Mock authenticated user

### Step 2: Choose Template Based on What You're Testing

**For FastAPI Endpoints:**
```bash
cp assets/test_fastapi_endpoint.template.py tests/test_[endpoint_name].py
```

**For MCP Tools:**
```bash
cp assets/test_mcp_tool.template.py tests/test_[tool_name].py
```

### Step 3: Customize the Template

Replace placeholders with your actual code:
- `[ENDPOINT_NAME]` / `[TOOL_NAME]` - Your endpoint/tool name
- Import statements - Your actual imports
- Mock data - Your actual data models
- Assertions - Your expected behavior

## Quality Criteria (Mandatory)

Every generated test MUST meet these criteria:

### 1. Isolation - Strict Database Mocking

**RULE:** NO actual database connections allowed.

Use `unittest.mock` or `pytest-mock` to mock all database sessions:

```python
from unittest.mock import MagicMock

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)
```

**Verify isolation:**
- ✅ All `db.query()`, `db.add()`, `db.commit()` are mocked
- ✅ No SQLite/PostgreSQL connections created
- ✅ Tests run without database server
- ❌ NEVER use real database in unit tests

### 2. Coverage - Minimum 3 Test Cases Per Function

**RULE:** Each function must have at least 3 test cases:

**Test Case 1: Happy Path (Success 200/201)**
```python
def test_create_task_success(client, mock_db, valid_payload):
    """Test successful creation."""
    response = client.post("/api/tasks", json=valid_payload)
    assert response.status_code == 201
    assert "id" in response.json()
```

**Test Case 2: Validation Error (422 Unprocessable Entity)**
```python
def test_create_task_validation_error(client, mock_db, invalid_payload):
    """Test with invalid data."""
    response = client.post("/api/tasks", json=invalid_payload)
    assert response.status_code == 422
    assert "detail" in response.json()
```

**Test Case 3: Logic Error/Edge Case (404 or 500)**
```python
def test_get_task_not_found(client, mock_db):
    """Test non-existent resource."""
    mock_db.query.return_value.filter.return_value.first.return_value = None
    response = client.get("/api/tasks/99999")
    assert response.status_code == 404
```

### 3. MCP Specifics - Schema Validation

**RULE:** For MCP tools, verify output schema matches Pydantic model exactly.

```python
from pydantic import BaseModel

class ToolOutput(BaseModel):
    success: bool
    message: str
    data: dict | None = None

def test_tool_output_schema(valid_input):
    result = execute_tool(**valid_input)

    # Verify it's the correct model
    assert isinstance(result, ToolOutput)

    # Verify schema compliance
    validated = ToolOutput(**result.model_dump())
    assert validated == result
```

**Schema compliance tests:**
- Field types match Pydantic definitions
- Required fields are present
- Output can be serialized/deserialized
- Validation errors are caught

### 4. Cleanliness - Use pytest.fixture

**RULE:** Use `pytest.fixture` for reusable mocks.

```python
@pytest.fixture
def mock_task_model():
    """Reusable mock task."""
    task = MagicMock()
    task.id = 1
    task.title = "Test Task"
    return task

def test_get_task(client, mock_db, mock_task_model):
    mock_db.query.return_value.filter.return_value.first.return_value = mock_task_model
    # Test logic
```

**Benefits:**
- DRY (Don't Repeat Yourself)
- Consistent test data
- Easy to maintain
- Clear test dependencies

## FastAPI Endpoint Testing Workflow

### 1. Identify the Endpoint

Determine:
- HTTP method (GET, POST, PUT, PATCH, DELETE)
- Route path (e.g., `/api/tasks/{task_id}`)
- Request payload schema
- Response schema
- Database operations involved

### 2. Setup Mocks

Mock the database dependency:

```python
from app.main import app
from app.database import get_db

def test_endpoint(client, mock_db):
    # Override dependency
    app.dependency_overrides[get_db] = lambda: mock_db

    # Configure mock behavior
    mock_db.query.return_value.filter.return_value.first.return_value = mock_obj

    # Make request
    response = client.get("/api/resource/1")

    # Cleanup
    app.dependency_overrides.clear()
```

### 3. Write the 3 Required Test Cases

**Happy Path:**
- Valid input
- Successful response (200/201/204)
- Verify response data
- Verify database calls

**Validation Error:**
- Invalid/missing fields
- 422 status code
- Error details in response
- Database not modified

**Logic Error:**
- Resource not found (404)
- Permission denied (403)
- Server error (500)
- Appropriate error handling

### 4. Add Edge Cases (Optional but Recommended)

```python
def test_get_tasks_empty_list(client, mock_db):
    """Test when no tasks exist."""
    mock_db.query.return_value.all.return_value = []
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.parametrize("task_id", [0, -1, -999])
def test_invalid_task_id(client, mock_db, task_id):
    """Test invalid ID values."""
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code in [404, 422]
```

## MCP Tool Testing Workflow

### 1. Define Input/Output Schemas

```python
from pydantic import BaseModel

class ToolInput(BaseModel):
    task_id: int
    action: str

class ToolOutput(BaseModel):
    success: bool
    message: str
    data: dict | None = None
```

### 2. Mock Database/External Services

```python
@pytest.mark.asyncio
async def test_mcp_tool(valid_input, mock_task_data):
    with patch("mcp_server.tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Configure mock
        mock_db.query.return_value.filter.return_value.first.return_value = mock_task_data

        # Execute tool
        result = await tool_function(**valid_input)

        # Assertions
        assert isinstance(result, ToolOutput)
        assert result.success is True
```

### 3. Validate Schema Compliance

```python
def test_output_schema_validation():
    """Ensure Pydantic validation works."""
    # Valid output
    output = ToolOutput(success=True, message="Done", data={})
    assert output.success is True

    # Invalid output (wrong type)
    with pytest.raises(ValidationError):
        ToolOutput(success="yes", message="Done")  # success should be bool
```

### 4. Test Error Scenarios

```python
@pytest.mark.asyncio
async def test_tool_not_found(valid_input):
    """Test when resource doesn't exist."""
    with patch("mcp_server.tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Return None (not found)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = await tool_function(**valid_input)

        assert isinstance(result, ToolOutput)
        assert result.success is False
        assert "not found" in result.message.lower()
```

## Common Mocking Patterns

### Database Query Chain

```python
# Pattern: db.query(Model).filter(...).first()
mock_db.query.return_value.filter.return_value.first.return_value = mock_object

# Pattern: db.query(Model).all()
mock_db.query.return_value.all.return_value = [obj1, obj2]

# Pattern: None (not found)
mock_db.query.return_value.filter.return_value.first.return_value = None
```

### Create Operations

```python
mock_db.add = MagicMock()
mock_db.commit = MagicMock()

def mock_refresh(obj):
    obj.id = 1  # Simulate auto-increment

mock_db.refresh.side_effect = mock_refresh
```

### Delete Operations

```python
mock_db.delete = MagicMock()
mock_db.commit = MagicMock()

# Test
delete_resource(mock_db, resource_id=1)

mock_db.delete.assert_called_once()
mock_db.commit.assert_called_once()
```

### Database Errors

```python
mock_db.commit.side_effect = Exception("Database error")

# Test should handle exception
with pytest.raises(DatabaseError):
    create_resource(mock_db, data)

mock_db.rollback.assert_called_once()
```

## Advanced Patterns

For advanced pytest patterns including parametrized tests, fixtures, markers, and async testing, see:

**`references/pytest-patterns.md`** - Comprehensive pytest patterns guide

For detailed database mocking strategies, see:

**`references/mocking-guide.md`** - Database and external service mocking guide

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tasks.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run verbose
pytest -v

# Run only failed tests
pytest --lf

# Stop on first failure
pytest -x
```

## Checklist for Generated Tests

Before considering tests complete, verify:

- [ ] All database operations are mocked (no actual DB connections)
- [ ] At least 3 test cases per function (Happy, Validation Error, Logic Error)
- [ ] For MCP tools: Pydantic schema validation included
- [ ] pytest fixtures used for reusable mocks
- [ ] FastAPI dependency overrides cleared after each test
- [ ] Assertions verify both status code and response data
- [ ] Database interactions verified (add/commit/query called correctly)
- [ ] Error cases tested (404, 422, 500)
- [ ] Edge cases considered (empty lists, invalid IDs, etc.)
- [ ] Tests are isolated (can run in any order)

## Best Practices

1. **One Assert Per Concept**: Group related assertions, but keep focused
2. **Descriptive Test Names**: `test_create_task_with_missing_title_returns_422`
3. **AAA Pattern**: Arrange (setup), Act (execute), Assert (verify)
4. **Mock Only External Dependencies**: Don't mock the code you're testing
5. **Use Fixtures for Setup**: Keep test functions clean
6. **Test Behavior, Not Implementation**: Focus on what, not how
7. **Clear Error Messages**: Use descriptive assertion messages
8. **Cleanup Resources**: Always clear dependency overrides

## Troubleshooting

**Tests fail with "No database connection":**
- Verify all database calls are mocked
- Check `app.dependency_overrides[get_db]` is set
- Ensure conftest.py fixtures are loaded

**Mock not returning expected value:**
- Configure `return_value` or `side_effect` correctly
- Check query chain matches actual code
- Use `assert_called_once()` to verify mock was called

**Pydantic validation errors in tests:**
- Ensure output matches exact schema
- Check field types (bool vs str, int vs str)
- Verify required fields are present

**Tests interfere with each other:**
- Add autouse fixture to clear overrides
- Reset mock state between tests
- Use fresh fixtures (default scope="function")
