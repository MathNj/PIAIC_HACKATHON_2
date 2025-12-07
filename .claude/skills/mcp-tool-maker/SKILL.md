---
name: "mcp-tool-maker"
description: "Creates MCP (Model Context Protocol) tools to expose backend functionality to AI agents. Essential for Phase III OpenAI ChatKit integration and AI-driven task management."
version: "2.0.0"
---

# MCP Tool Maker Skill

## When to Use
- User asks to "expose this function to AI" or "make this AI-accessible"
- User says "Create an MCP tool for..." or "Enable AI agent access"
- Phase III: OpenAI ChatKit integration
- Building AI-powered features (smart task suggestions, natural language task creation)
- Creating tools for autonomous task management

## Context
MCP (Model Context Protocol) enables AI agents to interact with your application:
- **Purpose**: Expose backend functionality as AI-callable tools
- **Use Cases**: Task creation, rescheduling, smart suggestions, analytics
- **Integration**: OpenAI ChatKit (Phase III) or custom AI agents
- **Architecture**: FastAPI endpoints wrapped with MCP decorators
- **Security**: JWT authentication required for all MCP tools

## Workflow
1. **Analyze Function**: Identify backend logic to expose
2. **Define Tool Contract**: Specify inputs, outputs, and behavior
3. **Add MCP Decorator**: Apply `@mcp.tool()` with descriptive docstring
4. **Type Annotations**: Ensure strict Python typing for schema generation
5. **Error Handling**: Wrap logic in try/except with user-friendly errors
6. **Authentication**: Integrate JWT token validation
7. **Testing**: Test tool with sample AI prompts
8. **Documentation**: Create usage examples for AI agents

## Output Format

### 1. MCP Server Setup: `backend/mcp/server.py`
```python
"""
MCP (Model Context Protocol) server for TODO application.

Exposes backend functionality as AI-callable tools for OpenAI ChatKit integration.
"""

from mcp import MCPServer
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import HTTPException

from app.database import get_session
from app.models.task import Task
from app.models.user import User
from app.auth.dependencies import verify_token
from sqlmodel import Session, select

# Initialize MCP server
mcp = MCPServer(name="todo-app-mcp")


@mcp.tool()
def create_task_from_natural_language(
    user_token: str,
    description: str,
    context: Optional[str] = None
) -> Dict[str, any]:
    """
    Create a task from natural language description.

    The AI will parse the description to extract:
    - Title (concise task name)
    - Priority (low, normal, high) based on urgency keywords
    - Due date (if mentioned: "tomorrow", "next week", specific date)
    - Additional context in description field

    Args:
        user_token: JWT authentication token
        description: Natural language task description
        context: Optional additional context or notes

    Returns:
        Created task with all fields populated

    Examples:
        - "Buy groceries tomorrow" → Title: "Buy groceries", Due: tomorrow, Priority: normal
        - "URGENT: Fix production bug" → Title: "Fix production bug", Priority: high
        - "Schedule dentist appointment next Monday at 2pm" → Extracts date and time
    """
    try:
        # Verify authentication
        user_id = verify_token(user_token)

        # AI-powered parsing (integrate with OpenAI)
        # For now, basic implementation
        title = description[:100]  # First 100 chars as title
        priority = "high" if any(word in description.lower() for word in ["urgent", "asap", "critical"]) else "normal"

        # Extract due date from common phrases
        due_date = None
        if "tomorrow" in description.lower():
            due_date = datetime.utcnow() + timedelta(days=1)
        elif "next week" in description.lower():
            due_date = datetime.utcnow() + timedelta(weeks=1)

        # Create task
        with Session(engine) as session:
            new_task = Task(
                user_id=user_id,
                title=title,
                description=context or description,
                priority=priority,
                due_date=due_date,
            )
            session.add(new_task)
            session.commit()
            session.refresh(new_task)

            return {
                "id": new_task.id,
                "title": new_task.title,
                "priority": new_task.priority,
                "due_date": new_task.due_date.isoformat() if new_task.due_date else None,
                "created": True
            }

    except Exception as e:
        return {"error": str(e), "created": False}


@mcp.tool()
def reschedule_task(
    user_token: str,
    task_id: int,
    new_date: str,
    reason: Optional[str] = None
) -> Dict[str, any]:
    """
    Reschedule a task to a new date.

    Args:
        user_token: JWT authentication token
        task_id: ID of the task to reschedule
        new_date: New due date (ISO format YYYY-MM-DD or natural language)
        reason: Optional reason for rescheduling

    Returns:
        Updated task with new due date

    Examples:
        - reschedule_task(token, 5, "2025-12-15", "Waiting for client approval")
        - reschedule_task(token, 3, "next Monday")
    """
    try:
        user_id = verify_token(user_token)

        # Parse date (handle both ISO and natural language)
        try:
            due_date = datetime.fromisoformat(new_date)
        except:
            # Parse natural language dates (simple implementation)
            if "tomorrow" in new_date.lower():
                due_date = datetime.utcnow() + timedelta(days=1)
            elif "next week" in new_date.lower():
                due_date = datetime.utcnow() + timedelta(weeks=1)
            else:
                raise ValueError(f"Unable to parse date: {new_date}")

        with Session(engine) as session:
            task = session.exec(
                select(Task).where(Task.id == task_id, Task.user_id == user_id)
            ).first()

            if not task:
                return {"error": "Task not found", "rescheduled": False}

            old_date = task.due_date
            task.due_date = due_date
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "id": task.id,
                "title": task.title,
                "old_due_date": old_date.isoformat() if old_date else None,
                "new_due_date": task.due_date.isoformat(),
                "reason": reason,
                "rescheduled": True
            }

    except Exception as e:
        return {"error": str(e), "rescheduled": False}


@mcp.tool()
def get_task_summary(
    user_token: str,
    timeframe: str = "today"
) -> Dict[str, any]:
    """
    Get a summary of tasks for AI analysis.

    Args:
        user_token: JWT authentication token
        timeframe: Time period ("today", "this_week", "overdue", "all")

    Returns:
        Task summary with counts, priorities, and upcoming deadlines

    Example:
        - get_task_summary(token, "today") → Today's tasks and priorities
        - get_task_summary(token, "overdue") → Overdue tasks requiring attention
    """
    try:
        user_id = verify_token(user_token)

        with Session(engine) as session:
            # Base query
            query = select(Task).where(Task.user_id == user_id)

            # Filter by timeframe
            now = datetime.utcnow()
            if timeframe == "today":
                query = query.where(
                    Task.due_date >= now.date(),
                    Task.due_date < now.date() + timedelta(days=1)
                )
            elif timeframe == "this_week":
                query = query.where(
                    Task.due_date >= now.date(),
                    Task.due_date < now.date() + timedelta(weeks=1)
                )
            elif timeframe == "overdue":
                query = query.where(
                    Task.due_date < now,
                    Task.completed == False
                )

            tasks = session.exec(query).all()

            # Calculate summary statistics
            total = len(tasks)
            completed = sum(1 for t in tasks if t.completed)
            pending = total - completed
            high_priority = sum(1 for t in tasks if t.priority == "high" and not t.completed)

            return {
                "timeframe": timeframe,
                "total_tasks": total,
                "completed": completed,
                "pending": pending,
                "high_priority": high_priority,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "priority": t.priority,
                        "due_date": t.due_date.isoformat() if t.due_date else None,
                        "completed": t.completed
                    }
                    for t in tasks[:10]  # Limit to 10 for brevity
                ]
            }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def suggest_task_prioritization(
    user_token: str
) -> List[Dict[str, any]]:
    """
    AI-powered task prioritization suggestions.

    Analyzes all pending tasks and suggests an optimal order based on:
    - Due dates (urgency)
    - Priority levels
    - Task dependencies (if implemented)
    - User's completion patterns

    Args:
        user_token: JWT authentication token

    Returns:
        Ordered list of tasks with prioritization reasoning

    Example:
        AI might suggest: "Focus on 'Fix production bug' first (high priority, due today),
        then 'Review pull request' (due tomorrow), then 'Update documentation' (low priority)"
    """
    try:
        user_id = verify_token(user_token)

        with Session(engine) as session:
            tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.completed == False
                )
            ).all()

            # Score each task
            scored_tasks = []
            now = datetime.utcnow()

            for task in tasks:
                score = 0
                reasons = []

                # Priority weighting
                if task.priority == "high":
                    score += 10
                    reasons.append("High priority")
                elif task.priority == "normal":
                    score += 5

                # Due date urgency
                if task.due_date:
                    days_until_due = (task.due_date - now).days
                    if days_until_due < 0:
                        score += 20
                        reasons.append(f"Overdue by {abs(days_until_due)} days")
                    elif days_until_due == 0:
                        score += 15
                        reasons.append("Due today")
                    elif days_until_due <= 3:
                        score += 10
                        reasons.append(f"Due in {days_until_due} days")

                scored_tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "score": score,
                    "reasons": reasons
                })

            # Sort by score descending
            scored_tasks.sort(key=lambda x: x["score"], reverse=True)

            return scored_tasks

    except Exception as e:
        return [{"error": str(e)}]


# Export MCP server for FastAPI integration
def get_mcp_server():
    """Get the MCP server instance."""
    return mcp
```

### 2. FastAPI Integration: `backend/app/routers/mcp.py`
```python
"""
MCP router for integrating MCP tools with FastAPI.

Exposes MCP tools as REST endpoints for OpenAI ChatKit.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from mcp.server import get_mcp_server

router = APIRouter(prefix="/api/mcp", tags=["MCP Tools"])
mcp_server = get_mcp_server()


class MCPToolRequest(BaseModel):
    """Request body for MCP tool execution."""
    tool_name: str
    arguments: Dict[str, Any]


@router.post("/execute")
async def execute_mcp_tool(request: MCPToolRequest) -> Dict[str, Any]:
    """
    Execute an MCP tool by name with provided arguments.

    Used by OpenAI ChatKit or other AI agents to invoke backend functions.
    """
    try:
        result = await mcp_server.call_tool(request.tool_name, **request.arguments)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tools")
async def list_mcp_tools() -> Dict[str, Any]:
    """
    List all available MCP tools with their signatures.

    Helps AI agents discover available functionality.
    """
    tools = mcp_server.list_tools()
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in tools
        ]
    }
```

### 3. OpenAI ChatKit Integration: `frontend/lib/chatkit-config.ts`
```typescript
/**
 * OpenAI ChatKit configuration for MCP tool integration.
 */

import { ChatKitProvider } from '@openai/chatkit-react';

const MCP_TOOLS = [
  {
    name: "create_task_from_natural_language",
    description: "Create a task from natural language description",
    parameters: {
      type: "object",
      properties: {
        description: {
          type: "string",
          description: "Natural language task description"
        },
        context: {
          type: "string",
          description: "Optional additional context"
        }
      },
      required: ["description"]
    }
  },
  {
    name: "reschedule_task",
    description: "Reschedule a task to a new date",
    parameters: {
      type: "object",
      properties: {
        task_id: {
          type: "number",
          description: "ID of task to reschedule"
        },
        new_date: {
          type: "string",
          description: "New due date (ISO or natural language)"
        },
        reason: {
          type: "string",
          description: "Optional reason for rescheduling"
        }
      },
      required: ["task_id", "new_date"]
    }
  },
  // ... other tools
];

export { MCP_TOOLS };
```

## MCP Tool Best Practices

### 1. Descriptive Docstrings
```python
@mcp.tool()
def tool_name(arg: str) -> Dict:
    """
    First line: Brief description (AI reads this first)

    Detailed explanation of what the tool does, when to use it,
    and what results to expect.

    Args:
        arg: Detailed parameter description with examples

    Returns:
        Detailed return value description

    Examples:
        - Example usage 1
        - Example usage 2
    """
```

### 2. Strong Type Hints
```python
from typing import Dict, List, Optional, Literal

@mcp.tool()
def typed_tool(
    required_str: str,
    optional_int: Optional[int] = None,
    priority: Literal["low", "normal", "high"] = "normal"
) -> Dict[str, any]:
    """Type hints enable automatic schema generation."""
```

### 3. Error Handling
```python
@mcp.tool()
def safe_tool(arg: str) -> Dict:
    """Always return structured responses."""
    try:
        # Tool logic
        return {"success": True, "data": result}
    except ValueError as e:
        return {"success": False, "error": f"Invalid input: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": "Unexpected error occurred"}
```

### 4. Authentication
```python
@mcp.tool()
def authenticated_tool(user_token: str, data: str) -> Dict:
    """All tools should verify JWT tokens."""
    try:
        user_id = verify_token(user_token)
        # Proceed with authorized operation
    except:
        return {"error": "Unauthorized", "success": False}
```

## Post-Creation Steps
1. **Register MCP Router**: Add to `main.py`
   ```python
   from app.routers import mcp
   app.include_router(mcp.router)
   ```

2. **Test MCP Tools**: Use Swagger UI at `/docs`

3. **Document for AI**: Create usage guide for AI agents

4. **OpenAI Integration**: Connect ChatKit with MCP endpoints

5. **Create PHR**: Document MCP tool creation
   - Title: "MCP Tool - [Tool Name]"
   - Stage: `green`
   - Feature: `ai-integration`

## Example
**Input**: "Create an MCP tool to suggest the next task to work on based on AI analysis"

**Output**:
```python
@mcp.tool()
def suggest_next_task(user_token: str, context: Optional[str] = None) -> Dict:
    """
    AI-powered suggestion for the next task to work on.

    Analyzes all pending tasks considering:
    - Due dates and urgency
    - Priority levels
    - Current context or user's current focus
    - Historical completion patterns

    Returns the recommended task with reasoning.
    """
    # Implementation with AI-powered analysis
```

## Quality Checklist
Before finalizing:
- [ ] Descriptive docstring (AI will read this)
- [ ] Strong type hints for all parameters
- [ ] Error handling with user-friendly messages
- [ ] JWT authentication integrated
- [ ] Return type is JSON-serializable (Dict, List, str, int, bool)
- [ ] Examples provided in docstring
- [ ] Tool registered in MCP server
- [ ] Tested with sample AI prompts
- [ ] Documented in frontend ChatKit config
- [ ] No sensitive data in responses
