# FastAPI OpenAI Integration Patterns

Complete guide for integrating OpenAI API into FastAPI backends with proper patterns for chat, streaming, function calling, and error handling.

## Project Setup

### 1. Dependencies

```bash
pip install fastapi uvicorn openai python-dotenv pydantic-settings tenacity tiktoken
```

### 2. Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7
    openai_timeout: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Client Initialization

```python
# app/services/openai_service.py
from functools import lru_cache
from openai import OpenAI
from app.config import settings

@lru_cache()
def get_openai_client() -> OpenAI:
    return OpenAI(
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout
    )

client = get_openai_client()
```

## Pattern 1: Simple Chat Endpoint

### Non-Streaming Chat

```python
# app/routers/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAIError
from app.services.openai_service import client
from app.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    tokens_used: int

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get AI response"""
    try:
        # Build messages (include conversation history if available)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.message}
        ]

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            max_tokens=settings.openai_max_tokens,
            temperature=settings.openai_temperature
        )

        assistant_message = response.choices[0].message.content

        return ChatResponse(
            message=assistant_message,
            conversation_id=request.conversation_id or "new",
            tokens_used=response.usage.total_tokens
        )

    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Pattern 2: Streaming Chat

### Server-Sent Events (SSE)

```python
# app/routers/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import json

@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream AI response in real-time"""

    async def generate():
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": request.message}
            ]

            stream = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"

            yield "data: [DONE]\n\n"

        except OpenAIError as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
```

## Pattern 3: Conversation History

### Database Models

```python
# app/models/conversation.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    messages: list["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str  # "user" or "assistant"
    content: str
    tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
```

### Chat with History

```python
# app/services/chat_service.py
from sqlmodel import Session, select
from app.models.conversation import Conversation, Message
from app.services.openai_service import client
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def load_conversation_messages(
    session: Session,
    conversation_id: int,
    max_tokens: int = 6000
) -> list[dict]:
    """Load conversation history, truncating if needed"""
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at)

    messages_db = session.exec(statement).all()

    # Convert to OpenAI format
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in messages_db
    ]

    # Truncate if exceeds max tokens
    total_tokens = sum(count_tokens(m["content"]) for m in messages)
    while total_tokens > max_tokens and len(messages) > 1:
        messages.pop(0)  # Remove oldest message
        total_tokens = sum(count_tokens(m["content"]) for m in messages)

    return messages

async def chat_with_history(
    session: Session,
    conversation_id: int,
    user_message: str
) -> tuple[str, int]:
    """Send message with conversation history"""

    # Load history
    messages = load_conversation_messages(session, conversation_id)

    # Add system prompt if first message
    if not messages:
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful assistant."
        })

    # Add new user message
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
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

    return assistant_message, tokens_used
```

### Router with History

```python
# app/routers/chat.py
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
from app.services.chat_service import chat_with_history

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """Send message to conversation with full history"""
    try:
        assistant_message, tokens = await chat_with_history(
            session,
            conversation_id,
            request.message
        )

        return {
            "message": assistant_message,
            "tokens_used": tokens
        }

    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Pattern 4: Error Handling and Retries

### Retry Decorator

```python
# app/services/openai_service.py
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from openai import RateLimitError, APIError

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, APIError))
)
def call_openai_with_retry(messages: list) -> str:
    """Call OpenAI with automatic retries"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content
```

### Comprehensive Error Handling

```python
from openai import (
    OpenAIError,
    APIError,
    RateLimitError,
    APIConnectionError,
    AuthenticationError
)
import logging

logger = logging.getLogger(__name__)

async def safe_openai_call(messages: list) -> dict:
    """Call OpenAI with comprehensive error handling"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return {
            "success": True,
            "message": response.choices[0].message.content,
            "tokens": response.usage.total_tokens
        }

    except AuthenticationError:
        logger.error("Invalid OpenAI API key")
        return {
            "success": False,
            "error": "Authentication failed. Check API key."
        }

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        return {
            "success": False,
            "error": "Rate limit exceeded. Please try again later."
        }

    except APIConnectionError as e:
        logger.error(f"Network error: {e}")
        return {
            "success": False,
            "error": "Network error. Please check connection."
        }

    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        return {
            "success": False,
            "error": f"API error: {e.status_code}"
        }

    except OpenAIError as e:
        logger.error(f"Unexpected OpenAI error: {e}")
        return {
            "success": False,
            "error": "Unexpected error occurred."
        }
```

## Pattern 5: Function Calling

### Define Tools

```python
# app/services/tools.py
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Task priority level"
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
            "description": "List all tasks, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "Filter tasks by status"
                    }
                }
            }
        }
    }
]

def execute_function(name: str, arguments: dict, session: Session):
    """Execute the requested function"""
    if name == "create_task":
        from app.crud import create_task
        task = create_task(session, **arguments)
        return {"success": True, "task_id": task.id}

    elif name == "list_tasks":
        from app.crud import list_tasks
        tasks = list_tasks(session, status=arguments.get("status", "all"))
        return {
            "success": True,
            "tasks": [{"id": t.id, "title": t.title} for t in tasks]
        }

    return {"success": False, "error": "Unknown function"}
```

### Agent with Function Calling

```python
# app/services/agent_service.py
import json
from app.services.tools import TOOLS, execute_function

async def run_agent(
    session: Session,
    user_query: str,
    max_iterations: int = 5
) -> str:
    """Run AI agent with function calling"""

    messages = [
        {"role": "system", "content": "You are a helpful task management assistant."},
        {"role": "user", "content": user_query}
    ]

    for _ in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=TOOLS
        )

        message = response.choices[0].message

        # If no tool calls, return final answer
        if not message.tool_calls:
            return message.content

        # Add assistant message to history
        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # Execute each tool call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute function
            result = execute_function(function_name, function_args, session)

            # Add function result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    return "Agent exceeded maximum iterations"
```

### Agent Endpoint

```python
# app/routers/agent.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.database import get_session
from app.services.agent_service import run_agent

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/")
async def agent_query(
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """Execute agent with function calling"""
    try:
        response = await run_agent(session, request.message)
        return {"message": response}

    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Pattern 6: Embeddings and Semantic Search

### Generate Embeddings

```python
# app/services/embedding_service.py
from openai import OpenAI
import numpy as np

client = OpenAI()

def create_embedding(text: str) -> list[float]:
    """Create embedding for a single text"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def create_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Create embeddings for multiple texts (batch)"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [data.embedding for data in response.data]

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### Semantic Search Endpoint

```python
# app/routers/search.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session
from app.services.embedding_service import create_embedding, cosine_similarity
from app.database import get_session

router = APIRouter(prefix="/search", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/semantic")
async def semantic_search(
    request: SearchRequest,
    session: Session = Depends(get_session)
):
    """Search tasks using semantic similarity"""

    # Create query embedding
    query_embedding = create_embedding(request.query)

    # Get all tasks with embeddings (assume embedding column exists)
    tasks = session.exec(select(Task)).all()

    # Calculate similarities
    results = []
    for task in tasks:
        if task.embedding:
            similarity = cosine_similarity(query_embedding, task.embedding)
            results.append((task, similarity))

    # Sort by similarity and get top k
    results.sort(key=lambda x: x[1], reverse=True)
    top_results = results[:request.top_k]

    return {
        "results": [
            {
                "id": task.id,
                "title": task.title,
                "similarity": float(similarity)
            }
            for task, similarity in top_results
        ]
    }
```

## Production Best Practices

### 1. Logging

```python
# app/middleware/logging.py
import logging
import time
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_openai_calls(request: Request, call_next):
    if "/chat" in request.url.path:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            f"OpenAI call: {request.method} {request.url.path} "
            f"duration={duration:.2f}s status={response.status_code}"
        )
        return response

    return await call_next(request)
```

### 2. Rate Limiting

```python
# app/middleware/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
import time

# Simple in-memory rate limiter (use Redis in production)
request_counts = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    # Clean old requests (older than 1 minute)
    request_counts[client_ip] = [
        t for t in request_counts[client_ip]
        if current_time - t < 60
    ]

    # Check rate limit (10 requests per minute)
    if len(request_counts[client_ip]) >= 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    request_counts[client_ip].append(current_time)
    return await call_next(request)
```

### 3. Monitoring

```python
# app/services/monitoring.py
from prometheus_client import Counter, Histogram

openai_requests_total = Counter(
    'openai_requests_total',
    'Total OpenAI API requests',
    ['model', 'status']
)

openai_tokens_total = Counter(
    'openai_tokens_total',
    'Total tokens used',
    ['model']
)

openai_duration_seconds = Histogram(
    'openai_duration_seconds',
    'OpenAI API call duration',
    ['model']
)

def track_openai_call(model: str, tokens: int, duration: float, status: str):
    openai_requests_total.labels(model=model, status=status).inc()
    openai_tokens_total.labels(model=model).inc(tokens)
    openai_duration_seconds.labels(model=model).observe(duration)
```

## Testing

### Unit Tests

```python
# tests/test_chat.py
import pytest
from unittest.mock import Mock, patch

@patch('app.services.openai_service.client')
def test_chat_endpoint(mock_client, client_fixture):
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices[0].message.content = "Hello!"
    mock_response.usage.total_tokens = 20
    mock_client.chat.completions.create.return_value = mock_response

    # Test endpoint
    response = client_fixture.post(
        "/chat/",
        json={"message": "Hi"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Hello!"
    assert response.json()["tokens_used"] == 20
```

### Integration Tests

```python
# tests/test_chat_integration.py
import pytest
import os

@pytest.mark.integration
def test_openai_chat_integration(client_fixture):
    """Test with actual OpenAI API"""

    # Skip if no API key
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OpenAI API key not set")

    response = client_fixture.post(
        "/chat/",
        json={"message": "Say 'test passed'"}
    )

    assert response.status_code == 200
    assert "test passed" in response.json()["message"].lower()
```

## Complete Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, agent, search
from app.middleware.logging import log_openai_calls
from app.middleware.rate_limit import rate_limit_middleware

app = FastAPI(title="OpenAI Integration API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(log_openai_calls)
app.middleware("http")(rate_limit_middleware)

# Routers
app.include_router(chat.router)
app.include_router(agent.router)
app.include_router(search.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```
