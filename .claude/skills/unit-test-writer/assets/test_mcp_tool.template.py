"""
Unit tests for MCP Tool: [TOOL_NAME]

This template demonstrates testing MCP server tools with:
1. Happy Path (Successful tool execution)
2. Validation Error (Invalid input schema)
3. Logic Error (Business logic failure)

CRITICAL: All database/external service calls must be mocked.
Output schema must match Pydantic model exactly.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pydantic import BaseModel, ValidationError


# ============================================================================
# Pydantic Models (Define your tool's input/output schemas)
# ============================================================================

class ToolInput(BaseModel):
    """Input schema for the MCP tool."""
    task_id: int
    user_id: int
    action: str


class ToolOutput(BaseModel):
    """Output schema for the MCP tool."""
    success: bool
    task_id: int
    message: str
    data: dict | None = None


# ============================================================================
# Test Setup and Fixtures
# ============================================================================

@pytest.fixture
def valid_tool_input():
    """Valid input for the MCP tool."""
    return {
        "task_id": 1,
        "user_id": 100,
        "action": "complete",
    }


@pytest.fixture
def invalid_tool_input():
    """Invalid input (missing required field)."""
    return {
        "task_id": 1,
        # Missing user_id
        "action": "complete",
    }


@pytest.fixture
def mock_task_data():
    """Mock task data from database."""
    return {
        "id": 1,
        "title": "Test Task",
        "completed": False,
        "user_id": 100,
    }


# ============================================================================
# Test Case 1: Happy Path (Successful Execution)
# ============================================================================

@pytest.mark.asyncio
async def test_tool_execution_success(valid_tool_input, mock_task_data):
    """
    Test successful MCP tool execution (Happy Path).

    Expected:
    - Tool returns ToolOutput model
    - Output schema matches Pydantic model exactly
    - success=True in response
    - All database calls mocked
    """
    # Import the tool function
    from mcp_server.tools.task_tools import complete_task_tool

    # Mock database session
    with patch("mcp_server.tools.task_tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Configure mock task query
        mock_task = MagicMock()
        mock_task.id = mock_task_data["id"]
        mock_task.title = mock_task_data["title"]
        mock_task.completed = mock_task_data["completed"]
        mock_task.user_id = mock_task_data["user_id"]

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_task
        mock_db.query.return_value = mock_query

        # Execute tool
        result = await complete_task_tool(**valid_tool_input)

        # Verify output is ToolOutput instance
        assert isinstance(result, ToolOutput)

        # Verify output schema matches exactly
        assert result.success is True
        assert result.task_id == valid_tool_input["task_id"]
        assert isinstance(result.message, str)
        assert result.data is not None

        # Verify Pydantic validation works
        validated_output = ToolOutput(**result.model_dump())
        assert validated_output == result

        # Verify database was called correctly
        mock_db.query.assert_called()
        mock_db.commit.assert_called_once()


def test_tool_output_schema_validation():
    """
    Test that ToolOutput schema validation works correctly.

    This ensures the Pydantic model enforces correct types.
    """
    # Valid output
    valid_output = ToolOutput(
        success=True,
        task_id=1,
        message="Task completed",
        data={"status": "done"},
    )
    assert valid_output.success is True
    assert valid_output.task_id == 1

    # Invalid output (wrong type for task_id)
    with pytest.raises(ValidationError) as exc_info:
        ToolOutput(
            success=True,
            task_id="not-an-integer",  # Should be int
            message="Task completed",
        )

    # Verify validation error details
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("task_id",) for error in errors)


# ============================================================================
# Test Case 2: Validation Error (Invalid Input)
# ============================================================================

def test_tool_input_validation_error(invalid_tool_input):
    """
    Test MCP tool with invalid input schema (Validation Error).

    Expected:
    - Pydantic raises ValidationError
    - Error details specify missing field
    - No database calls made
    """
    # Attempt to create ToolInput with invalid data
    with pytest.raises(ValidationError) as exc_info:
        ToolInput(**invalid_tool_input)

    # Verify validation error
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any(error["loc"] == ("user_id",) for error in errors)


@pytest.mark.asyncio
async def test_tool_execution_invalid_action(valid_tool_input):
    """
    Test tool execution with invalid action value.

    Expected:
    - Tool returns error response
    - success=False in response
    - Database not modified
    """
    from mcp_server.tools.task_tools import complete_task_tool

    # Mock database
    with patch("mcp_server.tools.task_tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Invalid action
        invalid_input = valid_tool_input.copy()
        invalid_input["action"] = "invalid_action"

        # Execute tool
        result = await complete_task_tool(**invalid_input)

        # Assertions
        assert isinstance(result, ToolOutput)
        assert result.success is False
        assert "invalid" in result.message.lower()

        # Verify database was not committed
        mock_db.commit.assert_not_called()


# ============================================================================
# Test Case 3: Logic Error / Edge Case
# ============================================================================

@pytest.mark.asyncio
async def test_tool_execution_task_not_found(valid_tool_input):
    """
    Test tool execution when task doesn't exist (Logic Error - 404).

    Expected:
    - Tool returns error response
    - success=False
    - Appropriate error message
    """
    from mcp_server.tools.task_tools import complete_task_tool

    # Mock database to return None (task not found)
    with patch("mcp_server.tools.task_tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Configure mock to return None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query

        # Execute tool
        result = await complete_task_tool(**valid_tool_input)

        # Assertions
        assert isinstance(result, ToolOutput)
        assert result.success is False
        assert "not found" in result.message.lower()
        assert result.task_id == valid_tool_input["task_id"]


@pytest.mark.asyncio
async def test_tool_execution_permission_denied(valid_tool_input, mock_task_data):
    """
    Test tool execution when user doesn't own the task (Logic Error).

    Expected:
    - Tool returns error response
    - success=False
    - Permission denied message
    """
    from mcp_server.tools.task_tools import complete_task_tool

    # Mock database
    with patch("mcp_server.tools.task_tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Configure mock task with different user_id
        mock_task = MagicMock()
        mock_task.id = mock_task_data["id"]
        mock_task.user_id = 999  # Different from valid_tool_input["user_id"]

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_task
        mock_db.query.return_value = mock_query

        # Execute tool
        result = await complete_task_tool(**valid_tool_input)

        # Assertions
        assert isinstance(result, ToolOutput)
        assert result.success is False
        assert "permission" in result.message.lower() or "unauthorized" in result.message.lower()

        # Verify database was not committed
        mock_db.commit.assert_not_called()


@pytest.mark.asyncio
async def test_tool_execution_database_error(valid_tool_input, mock_task_data):
    """
    Test tool execution when database error occurs (Edge Case - 500).

    Expected:
    - Tool returns error response
    - success=False
    - Database error handled gracefully
    """
    from mcp_server.tools.task_tools import complete_task_tool

    # Mock database to raise exception
    with patch("mcp_server.tools.task_tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Configure mock to raise exception on commit
        mock_task = MagicMock()
        mock_task.id = mock_task_data["id"]
        mock_task.user_id = valid_tool_input["user_id"]

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_task
        mock_db.query.return_value = mock_query
        mock_db.commit.side_effect = Exception("Database connection failed")

        # Execute tool
        result = await complete_task_tool(**valid_tool_input)

        # Assertions
        assert isinstance(result, ToolOutput)
        assert result.success is False
        assert "error" in result.message.lower()


# ============================================================================
# Parametrized Tests (Optional - for comprehensive coverage)
# ============================================================================

@pytest.mark.parametrize(
    "action,expected_status",
    [
        ("complete", True),
        ("uncomplete", True),
        ("delete", True),
        ("invalid", False),
        ("", False),
    ],
)
@pytest.mark.asyncio
async def test_tool_various_actions(valid_tool_input, mock_task_data, action, expected_status):
    """
    Test tool with various action types.

    Parametrized test for comprehensive action coverage.
    """
    from mcp_server.tools.task_tools import complete_task_tool

    # Mock database
    with patch("mcp_server.tools.task_tools.get_db_session") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value.__enter__.return_value = mock_db

        # Configure mock task
        mock_task = MagicMock()
        mock_task.id = mock_task_data["id"]
        mock_task.user_id = valid_tool_input["user_id"]

        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_task
        mock_db.query.return_value = mock_query

        # Modify input with different action
        test_input = valid_tool_input.copy()
        test_input["action"] = action

        # Execute tool
        result = await complete_task_tool(**test_input)

        # Assertions
        assert isinstance(result, ToolOutput)
        assert result.success == expected_status


# ============================================================================
# Schema Compliance Tests (Critical for MCP)
# ============================================================================

def test_tool_output_schema_completeness():
    """
    Verify ToolOutput schema has all required fields.

    This is critical for MCP tool compatibility.
    """
    # Get schema
    schema = ToolOutput.model_json_schema()

    # Verify required fields
    assert "success" in schema["properties"]
    assert "task_id" in schema["properties"]
    assert "message" in schema["properties"]
    assert "data" in schema["properties"]

    # Verify types
    assert schema["properties"]["success"]["type"] == "boolean"
    assert schema["properties"]["task_id"]["type"] == "integer"
    assert schema["properties"]["message"]["type"] == "string"


def test_tool_output_serialization():
    """
    Test that ToolOutput can be serialized to JSON correctly.

    This ensures MCP can transmit the output properly.
    """
    output = ToolOutput(
        success=True,
        task_id=123,
        message="Operation successful",
        data={"key": "value"},
    )

    # Serialize to JSON
    json_output = output.model_dump_json()
    assert isinstance(json_output, str)

    # Verify can be deserialized
    deserialized = ToolOutput.model_validate_json(json_output)
    assert deserialized == output
