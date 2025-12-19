---
name: openai-agents-sdk
description: Build production-ready AI agents using OpenAI Agents SDK with stateless architecture, tool use, and database integration. Use when: (1) Implementing AI agents that interact with backend services, (2) Creating stateless agents with conversation context loading, (3) Integrating tools and function calling with agents, (4) Building agents with streaming responses, (5) Implementing agent orchestration and workflows, (6) Adding agent capabilities to FastAPI endpoints, or (7) Ensuring constitutional compliance for stateless agent patterns. This skill provides production patterns for Phase III AI agent implementation.
---

# OpenAI Agents SDK

This skill provides production-ready patterns for building AI agents using the OpenAI Agents SDK with stateless architecture as required by the project constitution.

## Core Principle: Stateless Agents

**CONSTITUTIONAL REQUIREMENT**: All agents MUST be stateless with database-backed conversation persistence. NO in-memory conversation state allowed.

### Stateless Pattern

```python
# ❌ WRONG: Stateful agent with in-memory state
class Agent:
    def __init__(self):
        self.conversation_history = []  # Anti-pattern!

    def chat(self, message):
        self.conversation_history.append(message)
        # Process with history...

# ✅ CORRECT: Stateless agent loading from database
class Agent:
    def chat(self, conversation_id: int, message: str, session: Session):
        # Load history from database
        history = load_conversation_history(session, conversation_id)

        # Process with loaded history
        response = self.process(history + [message])

        # Save to database
        save_message(session, conversation_id, message, response)

        return response
```

## Quick Start

### 1. Install Dependencies

```bash
pip install openai sqlmodel alembic
```

### 2. Agent Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4"
    agent_max_tokens: int = 2000
    agent_temperature: float = 0.7

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Database Models

```python
# app/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    agent_id: str  # Agent identifier
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: list["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[str] = None  # JSON string of tool calls
    tool_call_id: Optional[str] = None
    tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
```

## Pattern 1: Basic Stateless Agent

### Agent Service

```python
# app/services/agent_service.py
from openai import OpenAI
from sqlmodel import Session, select
from app.models.conversation import Conversation, Message
from app.config import settings
import tiktoken

client = OpenAI(api_key=settings.openai_api_key)

def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model(settings.openai_model)
    return len(encoding.encode(text))

def load_conversation_context(
    session: Session,
    conversation_id: int,
    max_tokens: int = 6000
) -> list[dict]:
    """Load conversation history from database (stateless pattern)"""

    # Get messages ordered by creation time
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    messages_db = session.exec(statement).all()

    # Convert to OpenAI format
    messages = []
    for msg in messages_db:
        message_dict = {"role": msg.role, "content": msg.content}

        # Include tool calls if present
        if msg.tool_calls:
            import json
            message_dict["tool_calls"] = json.loads(msg.tool_calls)

        if msg.tool_call_id:
            message_dict["tool_call_id"] = msg.tool_call_id

        messages.append(message_dict)

    # Truncate if exceeds max tokens
    total_tokens = sum(count_tokens(m["content"]) for m in messages)
    while total_tokens > max_tokens and len(messages) > 1:
        messages.pop(0)  # Remove oldest
        total_tokens = sum(count_tokens(m["content"]) for m in messages)

    return messages

async def agent_chat(
    session: Session,
    conversation_id: int,
    user_message: str,
    system_prompt: str = "You are a helpful assistant."
) -> dict:
    """Stateless agent chat with database-backed context"""

    # Load context from database
    messages = load_conversation_context(session, conversation_id)

    # Add system prompt if first message
    if not messages:
        messages.insert(0, {"role": "system", "content": system_prompt})

    # Add new user message
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        max_tokens=settings.agent_max_tokens,
        temperature=settings.agent_temperature
    )

    assistant_message = response.choices[0].message.content
    tokens_used = response.usage.total_tokens

    # Save messages to database
    session.add(Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
        tokens=count_tokens(user_message)
    ))
    session.add(Message(
        conversation_id=conversation_id,
        role="assistant",
        content=assistant_message,
        tokens=count_tokens(assistant_message)
    ))
    session.commit()

    return {
        "message": assistant_message,
        "tokens_used": tokens_used
    }
```

### FastAPI Endpoint

```python
# app/routers/agent.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from app.database import get_session
from app.services.agent_service import agent_chat

router = APIRouter(prefix="/agent", tags=["agent"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    tokens_used: int

@router.post("/conversations/{conversation_id}/chat", response_model=ChatResponse)
async def chat(
    conversation_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """Chat with stateless agent"""
    try:
        result = await agent_chat(
            session,
            conversation_id,
            request.message
        )
        return ChatResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Pattern 2: Agent with Tool Use

### Define Tools

```python
# app/services/tools.py
from sqlmodel import Session, select
from app.models.task import Task

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List tasks filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "Filter by status"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "status": {"type": "string", "enum": ["pending", "completed"]},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["task_id"]
            }
        }
    }
]

def execute_tool(
    name: str,
    arguments: dict,
    session: Session,
    user_id: int
) -> dict:
    """Execute agent tool with database session"""

    if name == "create_task":
        task = Task(
            user_id=user_id,
            title=arguments["title"],
            description=arguments.get("description", ""),
            priority=arguments.get("priority", "medium")
        )
        session.add(task)
        session.commit()
        return {"success": True, "task_id": task.id}

    elif name == "list_tasks":
        status = arguments.get("status", "all")
        statement = select(Task).where(Task.user_id == user_id)

        if status != "all":
            statement = statement.where(Task.status == status)

        tasks = session.exec(statement).all()
        return {
            "success": True,
            "tasks": [
                {"id": t.id, "title": t.title, "status": t.status}
                for t in tasks
            ]
        }

    elif name == "update_task":
        task = session.get(Task, arguments["task_id"])
        if not task or task.user_id != user_id:
            return {"success": False, "error": "Task not found"}

        if "status" in arguments:
            task.status = arguments["status"]
        if "priority" in arguments:
            task.priority = arguments["priority"]

        session.commit()
        return {"success": True}

    return {"success": False, "error": "Unknown tool"}
```

### Agent with Tool Execution

```python
# app/services/agent_service.py (continued)
import json

async def agent_with_tools(
    session: Session,
    conversation_id: int,
    user_id: int,
    user_message: str,
    max_iterations: int = 5
) -> dict:
    """Stateless agent with tool execution"""

    # Load context
    messages = load_conversation_context(session, conversation_id)

    if not messages:
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful task management assistant with access to tools."
        })

    messages.append({"role": "user", "content": user_message})

    # Save user message
    session.add(Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
        tokens=count_tokens(user_message)
    ))

    tool_calls_made = []

    for iteration in range(max_iterations):
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=AGENT_TOOLS
        )

        message = response.choices[0].message

        # No tool calls - return final response
        if not message.tool_calls:
            # Save assistant message
            session.add(Message(
                conversation_id=conversation_id,
                role="assistant",
                content=message.content,
                tokens=count_tokens(message.content)
            ))
            session.commit()

            return {
                "message": message.content,
                "tool_calls": tool_calls_made,
                "tokens_used": response.usage.total_tokens
            }

        # Add assistant message with tool calls
        messages.append(message)

        # Save assistant message with tool calls
        session.add(Message(
            conversation_id=conversation_id,
            role="assistant",
            content=message.content or "",
            tool_calls=json.dumps([
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]),
            tokens=count_tokens(message.content or "")
        ))

        # Execute tool calls
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            tool_calls_made.append({
                "name": function_name,
                "arguments": function_args
            })

            # Execute tool
            result = execute_tool(
                function_name,
                function_args,
                session,
                user_id
            )

            # Add tool result to messages
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            }
            messages.append(tool_message)

            # Save tool result
            session.add(Message(
                conversation_id=conversation_id,
                role="tool",
                content=json.dumps(result),
                tool_call_id=tool_call.id,
                tokens=count_tokens(json.dumps(result))
            ))

        session.commit()

    raise Exception("Agent exceeded maximum iterations")
```

## Pattern 3: Streaming Agent Responses

### Streaming Service

```python
# app/services/agent_service.py (continued)
async def agent_chat_stream(
    session: Session,
    conversation_id: int,
    user_message: str
):
    """Stateless agent with streaming responses"""

    # Load context
    messages = load_conversation_context(session, conversation_id)

    if not messages:
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful assistant."
        })

    messages.append({"role": "user", "content": user_message})

    # Save user message
    session.add(Message(
        conversation_id=conversation_id,
        role="user",
        content=user_message,
        tokens=count_tokens(user_message)
    ))
    session.commit()

    # Stream response
    stream = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        stream=True
    )

    collected_content = []

    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            collected_content.append(content)
            yield content

    # Save complete assistant message
    full_response = "".join(collected_content)
    session.add(Message(
        conversation_id=conversation_id,
        role="assistant",
        content=full_response,
        tokens=count_tokens(full_response)
    ))
    session.commit()
```

### Streaming Endpoint

```python
# app/routers/agent.py (continued)
from fastapi.responses import StreamingResponse

@router.post("/conversations/{conversation_id}/stream")
async def chat_stream(
    conversation_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """Stream agent responses"""

    async def generate():
        try:
            async for chunk in agent_chat_stream(
                session,
                conversation_id,
                request.message
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )
```

## Pattern 4: Multi-Agent Orchestration

### Agent Registry

```python
# app/services/agent_registry.py
from typing import Dict, Callable

class AgentRegistry:
    """Registry of specialized agents"""

    def __init__(self):
        self.agents: Dict[str, Callable] = {}

    def register(self, name: str, system_prompt: str, tools: list = None):
        """Register an agent"""
        self.agents[name] = {
            "system_prompt": system_prompt,
            "tools": tools or []
        }

    def get(self, name: str) -> dict:
        """Get agent configuration"""
        return self.agents.get(name)

# Global registry
registry = AgentRegistry()

# Register specialized agents
registry.register(
    "task_assistant",
    system_prompt="You are a helpful task management assistant. Help users create, update, and organize their tasks.",
    tools=AGENT_TOOLS
)

registry.register(
    "code_reviewer",
    system_prompt="You are a senior code reviewer. Analyze code for bugs, performance issues, and best practices.",
    tools=[]
)

registry.register(
    "data_analyst",
    system_prompt="You are a data analyst. Help users understand and analyze their data.",
    tools=[]
)
```

### Agent Selection Endpoint

```python
# app/routers/agent.py (continued)
from app.services.agent_registry import registry

@router.post("/conversations/{conversation_id}/chat/{agent_name}")
async def chat_with_agent(
    conversation_id: int,
    agent_name: str,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """Chat with a specific agent"""

    agent_config = registry.get(agent_name)
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Load context
    messages = load_conversation_context(session, conversation_id)
    messages.insert(0, {
        "role": "system",
        "content": agent_config["system_prompt"]
    })
    messages.append({"role": "user", "content": request.message})

    # Call with agent-specific tools
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        tools=agent_config["tools"] if agent_config["tools"] else None
    )

    # Save and return...
```

## Production Best Practices

### 1. Stateless Validation

```python
# tests/test_agent_stateless.py
import pytest
from app.services.agent_service import agent_chat

def test_agent_is_stateless(session):
    """Verify agent has no in-memory state"""

    # Create conversation
    conv_id = 1

    # First message
    result1 = agent_chat(session, conv_id, "My name is Alice")

    # Second message (agent must load history from DB)
    result2 = agent_chat(session, conv_id, "What's my name?")

    assert "Alice" in result2["message"]

    # Verify NO in-memory state by checking agent service has no instance variables
    from app.services import agent_service
    assert not hasattr(agent_service, 'conversation_history')
    assert not hasattr(agent_service, 'messages')
```

### 2. Tenant Isolation

```python
def load_conversation_context(
    session: Session,
    conversation_id: int,
    user_id: int  # Add user_id for isolation
) -> list[dict]:
    """Load context with tenant isolation"""

    # Verify conversation belongs to user
    conversation = session.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != user_id:
        raise ValueError("Conversation not found or unauthorized")

    # Rest of implementation...
```

### 3. Error Handling

```python
async def agent_chat_safe(
    session: Session,
    conversation_id: int,
    user_message: str
) -> dict:
    """Agent chat with comprehensive error handling"""

    try:
        return await agent_chat(session, conversation_id, user_message)

    except ValueError as e:
        return {"success": False, "error": str(e)}

    except Exception as e:
        logger.error(f"Agent error: {e}")
        return {
            "success": False,
            "error": "An unexpected error occurred"
        }
```

### 4. Logging and Monitoring

```python
import logging
import time

logger = logging.getLogger(__name__)

async def agent_chat_with_logging(
    session: Session,
    conversation_id: int,
    user_message: str
) -> dict:
    """Agent chat with logging"""

    start_time = time.time()

    logger.info(
        f"Agent chat started",
        extra={
            "conversation_id": conversation_id,
            "message_length": len(user_message)
        }
    )

    try:
        result = await agent_chat(session, conversation_id, user_message)

        duration = time.time() - start_time
        logger.info(
            f"Agent chat completed",
            extra={
                "conversation_id": conversation_id,
                "duration": duration,
                "tokens_used": result.get("tokens_used", 0)
            }
        )

        return result

    except Exception as e:
        logger.error(
            f"Agent chat failed: {e}",
            extra={"conversation_id": conversation_id}
        )
        raise
```

## Testing

### Unit Tests

```python
# tests/test_agent.py
import pytest
from unittest.mock import Mock, patch

@patch('app.services.agent_service.client')
def test_agent_chat(mock_client, session):
    """Test agent chat functionality"""

    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices[0].message.content = "Hello!"
    mock_response.usage.total_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response

    # Test
    result = agent_chat(session, conversation_id=1, user_message="Hi")

    assert result["message"] == "Hello!"
    assert result["tokens_used"] == 20
```

### Integration Tests

```python
@pytest.mark.integration
def test_agent_with_real_openai(session):
    """Test with actual OpenAI API"""

    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not set")

    result = agent_chat(
        session,
        conversation_id=1,
        user_message="Say 'test passed'"
    )

    assert "test passed" in result["message"].lower()
```

## Constitutional Compliance Checklist

- [ ] Agent has NO instance variables storing conversation state
- [ ] All conversation context loaded from database on every request
- [ ] Messages saved to database after every agent response
- [ ] User ID (tenant isolation) enforced on all database queries
- [ ] No shared global state between requests
- [ ] Agent can be restarted without losing conversation data
- [ ] Concurrent requests to same conversation don't interfere
- [ ] All tests verify stateless behavior

## Reference Files

- **Tool Integration**: `references/agent-tools-patterns.md` - Advanced tool use patterns
- **Streaming Guide**: `references/agent-streaming-guide.md` - Streaming implementation details
- **Testing Guide**: `references/agent-testing-guide.md` - Comprehensive testing strategies
