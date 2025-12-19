---
name: mcp-server-builder
description: Build MCP (Model Context Protocol) servers to expose tools and resources to AI agents. Use when: (1) Creating MCP servers for agent tool integration, (2) Exposing database operations as MCP tools, (3) Building custom tools for AI agents, (4) Implementing MCP resources for data access, (5) Integrating MCP servers with FastAPI backends, (6) Creating reusable MCP tool libraries, or (7) Implementing MCP prompts and sampling. This skill provides production-ready patterns for Python MCP server development aligned with the OpenAI Agents SDK.
---

# MCP Server Builder

This skill provides production-ready patterns for building MCP (Model Context Protocol) servers that expose tools and resources to AI agents.

## What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol for exposing capabilities to AI agents:
- **Tools**: Functions agents can call (e.g., create_task, search_database)
- **Resources**: Data sources agents can access (e.g., file contents, API data)
- **Prompts**: Pre-defined prompt templates
- **Sampling**: Request LLM completions

## Quick Start

### 1. Install MCP SDK

```bash
pip install mcp anthropic-mcp
```

### 2. Basic MCP Server

```python
# server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio

# Create server
server = Server("my-mcp-server")

# Define a tool
@server.tool()
async def get_weather(location: str) -> str:
    """Get current weather for a location"""
    # Implement weather API call
    return f"Weather in {location}: 72°F, sunny"

# Define another tool
@server.tool()
async def search_database(query: str) -> str:
    """Search database for information"""
    # Implement database search
    return f"Search results for '{query}': Found 3 items"

# Run server
if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.serve(server))
```

### 3. Run the Server

```bash
python server.py
```

The server communicates via stdio (standard input/output) and can be connected to AI agents.

## Pattern 1: Tools (Function Calling)

### Simple Tool

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("task-tools")

@server.tool()
async def create_task(
    title: str,
    description: str = "",
    priority: str = "medium"
) -> dict:
    """
    Create a new task in the todo list.

    Args:
        title: Task title (required)
        description: Task description
        priority: Priority level (low, medium, high)

    Returns:
        Created task information
    """
    # Database logic
    task_id = save_task_to_db(title, description, priority)

    return {
        "success": True,
        "task_id": task_id,
        "message": f"Created task: {title}"
    }
```

### Tool with Type Annotations

```python
from typing import Literal
from pydantic import BaseModel, Field

class TaskInput(BaseModel):
    title: str = Field(description="Task title")
    description: str = Field(default="", description="Task description")
    priority: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="Task priority level"
    )

@server.tool()
async def create_task_typed(input: TaskInput) -> dict:
    """Create a task with structured input validation"""
    return {
        "success": True,
        "task": {
            "title": input.title,
            "description": input.description,
            "priority": input.priority
        }
    }
```

### Tool with Database Integration

```python
from sqlmodel import Session, select
from app.database import get_session
from app.models.task import Task

@server.tool()
async def list_tasks(
    status: str = "all",
    user_id: int = None
) -> dict:
    """
    List tasks filtered by status and user.

    Args:
        status: Filter by status (all, pending, completed)
        user_id: User ID for filtering (required for multi-tenancy)

    Returns:
        List of tasks
    """
    with next(get_session()) as session:
        statement = select(Task)

        if user_id:
            statement = statement.where(Task.user_id == user_id)

        if status != "all":
            statement = statement.where(Task.status == status)

        tasks = session.exec(statement).all()

        return {
            "success": True,
            "count": len(tasks),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority
                }
                for t in tasks
            ]
        }
```

## Pattern 2: Resources (Data Access)

### File Resource

```python
from mcp.types import Resource, TextContent

@server.resource("file://{path}")
async def read_file(path: str) -> TextContent:
    """
    Read file contents.

    Args:
        path: File path to read

    Returns:
        File contents as text
    """
    try:
        with open(path, "r") as f:
            content = f.read()

        return TextContent(
            type="text",
            text=content,
            mimeType="text/plain"
        )
    except FileNotFoundError:
        return TextContent(
            type="text",
            text=f"Error: File not found: {path}",
            mimeType="text/plain"
        )
```

### Database Resource

```python
@server.resource("task://{task_id}")
async def get_task_resource(task_id: int) -> TextContent:
    """
    Get task details as a resource.

    Args:
        task_id: Task ID

    Returns:
        Task details as formatted text
    """
    with next(get_session()) as session:
        task = session.get(Task, task_id)

        if not task:
            return TextContent(
                type="text",
                text=f"Task {task_id} not found"
            )

        content = f"""
Task #{task.id}
Title: {task.title}
Description: {task.description}
Status: {task.status}
Priority: {task.priority}
Created: {task.created_at}
        """

        return TextContent(type="text", text=content.strip())
```

### API Resource

```python
import httpx

@server.resource("api://weather/{location}")
async def get_weather_resource(location: str) -> TextContent:
    """
    Get weather data from external API.

    Args:
        location: City name

    Returns:
        Weather information
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weather.com/current",
            params={"location": location, "api_key": os.getenv("WEATHER_API_KEY")}
        )

        data = response.json()

        return TextContent(
            type="text",
            text=f"Weather in {location}: {data['temp']}°F, {data['conditions']}"
        )
```

## Pattern 3: FastAPI Integration

### MCP Server as FastAPI Dependency

```python
# app/mcp/server.py
from mcp.server import Server
from sqlmodel import Session
from app.database import get_session

# Create MCP server instance
mcp_server = Server("todo-mcp-server")

def get_mcp_server() -> Server:
    """Dependency to get MCP server instance"""
    return mcp_server

# Register tools with database access
@mcp_server.tool()
async def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    user_id: int = None
) -> dict:
    """Create a task (MCP tool)"""
    with next(get_session()) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task_id": task.id,
            "title": task.title
        }

@mcp_server.tool()
async def update_task(
    task_id: int,
    status: str = None,
    priority: str = None,
    user_id: int = None
) -> dict:
    """Update a task (MCP tool)"""
    with next(get_session()) as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        if status:
            task.status = status
        if priority:
            task.priority = priority

        session.commit()

        return {"success": True, "task_id": task.id}
```

### Expose MCP Server via FastAPI

```python
# app/routers/mcp.py
from fastapi import APIRouter, Depends
from app.mcp.server import get_mcp_server, mcp_server

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    tools = [
        {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
        for tool in mcp_server.list_tools()
    ]
    return {"tools": tools}

@router.post("/tools/{tool_name}")
async def execute_mcp_tool(tool_name: str, arguments: dict):
    """Execute an MCP tool"""
    try:
        result = await mcp_server.call_tool(tool_name, arguments)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/resources")
async def list_mcp_resources():
    """List available MCP resources"""
    resources = mcp_server.list_resources()
    return {"resources": [r.uri for r in resources]}
```

## Pattern 4: Complete MCP Server for Todo App

### Full Implementation

```python
# app/mcp/todo_server.py
from mcp.server import Server
from mcp.types import Tool, Resource, TextContent
from sqlmodel import Session, select
from app.database import get_session
from app.models.task import Task
from app.models.user import User
import json

# Create server
todo_server = Server("todo-mcp-server")

# ============================================
# TOOLS (Functions agents can call)
# ============================================

@todo_server.tool()
async def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str = None,
    user_id: int = None
) -> dict:
    """
    Create a new task in the todo list.

    Args:
        title: Task title (required)
        description: Task description
        priority: Priority level (low, medium, high)
        due_date: Due date in YYYY-MM-DD format
        user_id: User ID (required for multi-tenancy)
    """
    if not user_id:
        return {"success": False, "error": "user_id required"}

    with next(get_session()) as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task_id": task.id,
            "title": task.title,
            "status": task.status
        }

@todo_server.tool()
async def list_tasks(
    status: str = "all",
    priority: str = "all",
    user_id: int = None
) -> dict:
    """
    List tasks with optional filters.

    Args:
        status: Filter by status (all, pending, completed)
        priority: Filter by priority (all, low, medium, high)
        user_id: User ID (required)
    """
    if not user_id:
        return {"success": False, "error": "user_id required"}

    with next(get_session()) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status != "all":
            statement = statement.where(Task.status == status)
        if priority != "all":
            statement = statement.where(Task.priority == priority)

        tasks = session.exec(statement).all()

        return {
            "success": True,
            "count": len(tasks),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "status": t.status,
                    "priority": t.priority,
                    "due_date": str(t.due_date) if t.due_date else None
                }
                for t in tasks
            ]
        }

@todo_server.tool()
async def update_task(
    task_id: int,
    title: str = None,
    description: str = None,
    status: str = None,
    priority: str = None,
    user_id: int = None
) -> dict:
    """
    Update an existing task.

    Args:
        task_id: Task ID (required)
        title: New title
        description: New description
        status: New status (pending, completed)
        priority: New priority (low, medium, high)
        user_id: User ID (required)
    """
    if not user_id:
        return {"success": False, "error": "user_id required"}

    with next(get_session()) as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        if title:
            task.title = title
        if description:
            task.description = description
        if status:
            task.status = status
        if priority:
            task.priority = priority

        session.commit()
        session.refresh(task)

        return {
            "success": True,
            "task_id": task.id,
            "updated_fields": [
                k for k, v in {
                    "title": title,
                    "description": description,
                    "status": status,
                    "priority": priority
                }.items() if v is not None
            ]
        }

@todo_server.tool()
async def delete_task(task_id: int, user_id: int = None) -> dict:
    """
    Delete a task by ID.

    Args:
        task_id: Task ID (required)
        user_id: User ID (required)
    """
    if not user_id:
        return {"success": False, "error": "user_id required"}

    with next(get_session()) as session:
        task = session.get(Task, task_id)

        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        session.delete(task)
        session.commit()

        return {"success": True, "deleted_task_id": task_id}

@todo_server.tool()
async def search_tasks(query: str, user_id: int = None) -> dict:
    """
    Search tasks by keyword in title or description.

    Args:
        query: Search query
        user_id: User ID (required)
    """
    if not user_id:
        return {"success": False, "error": "user_id required"}

    with next(get_session()) as session:
        statement = select(Task).where(
            Task.user_id == user_id
        ).where(
            (Task.title.contains(query)) | (Task.description.contains(query))
        )

        tasks = session.exec(statement).all()

        return {
            "success": True,
            "query": query,
            "count": len(tasks),
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "status": t.status
                }
                for t in tasks
            ]
        }

# ============================================
# RESOURCES (Data sources agents can access)
# ============================================

@todo_server.resource("task://{task_id}")
async def get_task_details(task_id: int) -> TextContent:
    """
    Get detailed task information.

    URI: task://123
    """
    with next(get_session()) as session:
        task = session.get(Task, task_id)

        if not task:
            return TextContent(
                type="text",
                text=f"Task {task_id} not found"
            )

        content = f"""
Task #{task.id}
Title: {task.title}
Description: {task.description or '(no description)'}
Status: {task.status}
Priority: {task.priority}
Due Date: {task.due_date or 'Not set'}
Created: {task.created_at}
Updated: {task.updated_at}
        """

        return TextContent(type="text", text=content.strip())

@todo_server.resource("tasks://user/{user_id}/summary")
async def get_user_task_summary(user_id: int) -> TextContent:
    """
    Get user task summary statistics.

    URI: tasks://user/123/summary
    """
    with next(get_session()) as session:
        total = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

        pending = len([t for t in total if t.status == "pending"])
        completed = len([t for t in total if t.status == "completed"])

        high_priority = len([t for t in total if t.priority == "high"])

        content = f"""
Task Summary for User {user_id}
================================
Total Tasks: {len(total)}
Pending: {pending}
Completed: {completed}
High Priority: {high_priority}
        """

        return TextContent(type="text", text=content.strip())

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import asyncio
    import mcp.server.stdio

    asyncio.run(mcp.server.stdio.serve(todo_server))
```

## Pattern 5: Agent Integration

### Using MCP Tools in OpenAI Agent

```python
# app/services/agent_with_mcp.py
from openai import OpenAI
from app.mcp.todo_server import todo_server
import json

client = OpenAI()

def mcp_tools_to_openai_format(mcp_server: Server) -> list:
    """Convert MCP tools to OpenAI function calling format"""
    tools = []

    for tool in mcp_server.list_tools():
        tools.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        })

    return tools

async def agent_with_mcp_tools(user_message: str, user_id: int):
    """Agent that uses MCP tools"""

    # Convert MCP tools to OpenAI format
    tools = mcp_tools_to_openai_format(todo_server)

    messages = [
        {"role": "system", "content": "You are a helpful task management assistant."},
        {"role": "user", "content": user_message}
    ]

    # Agent loop
    for _ in range(5):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content

        messages.append(message)

        # Execute MCP tools
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Add user_id to all tool calls
            function_args["user_id"] = user_id

            # Call MCP tool
            result = await todo_server.call_tool(function_name, function_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    return "Agent exceeded maximum iterations"
```

## Pattern 6: Testing MCP Servers

### Unit Tests

```python
# tests/test_mcp_server.py
import pytest
from app.mcp.todo_server import todo_server

@pytest.mark.asyncio
async def test_create_task_tool():
    """Test create_task MCP tool"""

    result = await todo_server.call_tool(
        "create_task",
        {
            "title": "Test task",
            "priority": "high",
            "user_id": 1
        }
    )

    assert result["success"] is True
    assert "task_id" in result
    assert result["title"] == "Test task"

@pytest.mark.asyncio
async def test_list_tasks_tool():
    """Test list_tasks MCP tool"""

    result = await todo_server.call_tool(
        "list_tasks",
        {"status": "all", "user_id": 1}
    )

    assert result["success"] is True
    assert "tasks" in result
    assert isinstance(result["tasks"], list)

@pytest.mark.asyncio
async def test_task_resource():
    """Test task resource"""

    # Create task first
    create_result = await todo_server.call_tool(
        "create_task",
        {"title": "Resource test", "user_id": 1}
    )
    task_id = create_result["task_id"]

    # Get resource
    resource = await todo_server.get_resource(f"task://{task_id}")

    assert resource is not None
    assert "Resource test" in resource.text
```

## Production Best Practices

### 1. Error Handling

```python
@server.tool()
async def safe_create_task(**kwargs) -> dict:
    """Create task with error handling"""
    try:
        # Validation
        if not kwargs.get("title"):
            return {"success": False, "error": "Title required"}

        if not kwargs.get("user_id"):
            return {"success": False, "error": "user_id required"}

        # Execute
        with next(get_session()) as session:
            task = Task(**kwargs)
            session.add(task)
            session.commit()

            return {"success": True, "task_id": task.id}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 2. Logging

```python
import logging

logger = logging.getLogger(__name__)

@server.tool()
async def logged_create_task(**kwargs) -> dict:
    """Create task with logging"""
    logger.info(f"MCP tool called: create_task", extra=kwargs)

    try:
        result = await create_task(**kwargs)
        logger.info(f"Tool success: {result}")
        return result
    except Exception as e:
        logger.error(f"Tool error: {e}")
        raise
```

### 3. Rate Limiting

```python
from collections import defaultdict
import time

# Simple rate limiter
request_counts = defaultdict(list)

async def rate_limited_tool(user_id: int, limit: int = 10):
    """Check rate limit"""
    current_time = time.time()

    # Clean old requests
    request_counts[user_id] = [
        t for t in request_counts[user_id]
        if current_time - t < 60
    ]

    if len(request_counts[user_id]) >= limit:
        raise Exception("Rate limit exceeded")

    request_counts[user_id].append(current_time)
```

### 4. Authentication

```python
from fastapi import Header, HTTPException

async def verify_mcp_token(x_mcp_token: str = Header(None)):
    """Verify MCP access token"""
    if not x_mcp_token:
        raise HTTPException(status_code=401, detail="Token required")

    # Verify token
    if x_mcp_token != os.getenv("MCP_ACCESS_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid token")

    return x_mcp_token
```

## Deployment

### Run MCP Server Standalone

```bash
# Run via stdio (for CLI agents)
python app/mcp/todo_server.py

# Run with logging
python app/mcp/todo_server.py --log-level=DEBUG
```

### Docker Deployment

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app/mcp/todo_server.py"]
```

### FastAPI Integration

```python
# app/main.py
from fastapi import FastAPI
from app.routers import mcp

app = FastAPI()

# Include MCP router
app.include_router(mcp.router)

# MCP server runs alongside FastAPI
```

## Security Checklist

- [ ] All tools require user_id (tenant isolation)
- [ ] Input validation on all tool parameters
- [ ] Authentication for MCP endpoints
- [ ] Rate limiting implemented
- [ ] Error messages don't leak sensitive data
- [ ] Database queries use parameterized statements
- [ ] Logging excludes sensitive information
- [ ] CORS configured for MCP endpoints

## Tools vs Resources

**Use Tools when**:
- Agent needs to perform actions (create, update, delete)
- Operation modifies data
- Function calling pattern

**Use Resources when**:
- Agent needs to read data
- Providing context/information
- Static or dynamic content retrieval

## Common Patterns

### Pattern: CRUD Tools

```python
@server.tool()
async def create(...): pass  # Create

@server.tool()
async def read(...): pass    # Read

@server.tool()
async def update(...): pass  # Update

@server.tool()
async def delete(...): pass  # Delete
```

### Pattern: Search Tools

```python
@server.tool()
async def search_by_keyword(...): pass

@server.tool()
async def filter_by_criteria(...): pass

@server.tool()
async def semantic_search(...): pass
```

### Pattern: Analytics Tools

```python
@server.tool()
async def get_statistics(...): pass

@server.tool()
async def generate_report(...): pass

@server.tool()
async def analyze_trends(...): pass
```

## Troubleshooting

**Issue**: MCP tools not appearing in agent
**Solution**: Verify tool schema format, check MCP server is running, validate tool registration

**Issue**: Database connection errors
**Solution**: Use context managers (`with`), ensure connection pooling, handle session lifecycle

**Issue**: Slow tool execution
**Solution**: Add database indexes, implement caching, optimize queries, use async operations

**Issue**: Multi-tenancy violations
**Solution**: Always require and validate `user_id`, add database constraints, audit all queries
