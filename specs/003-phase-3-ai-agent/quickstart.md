# Quickstart: AI Chat Agent with MCP Integration

**Feature**: AI Chat Agent with MCP Integration
**Phase**: III (Agent-Augmented System)
**Prerequisites**: Phase II completed (backend API, frontend UI, authentication)

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Migration](#database-migration)
4. [Backend Setup (MCP Tools)](#backend-setup-mcp-tools)
5. [Agent Orchestration](#agent-orchestration)
6. [Frontend Integration (ChatKit)](#frontend-integration-chatkit)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Phase II Completed**: Backend API running on port 8000, Frontend on port 3000
- **Database**: Neon PostgreSQL instance with Phase II schema
- **Node.js**: v20+ (for frontend)
- **Python**: 3.13+ (for backend)
- **OpenAI API Key**: Required for agent execution

### Verify Phase II Status

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend running
curl http://localhost:3000

# Database connection
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

---

## Environment Setup

### 1. Install Backend Dependencies

```bash
cd backend

# Add new Phase III dependencies
pip install openai>=1.0.0
pip install mcp>=0.1.0
pip install python-dateutil>=2.8.2

# Or add to requirements.txt and install all
echo "openai>=1.0.0" >> requirements.txt
echo "mcp>=0.1.0" >> requirements.txt
echo "python-dateutil>=2.8.2" >> requirements.txt

pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend

# Add OpenAI ChatKit
npm install @openai/chatkit-react@latest

# Verify installation
npm list @openai/chatkit-react
```

### 3. Configure Environment Variables

**Backend (`backend/.env.local`)**:
```bash
# Phase II (existing)
DATABASE_URL=postgresql://user:pass@neon-host/todoapp?sslmode=require
BETTER_AUTH_SECRET=your-secret-at-least-32-characters-long
FRONTEND_URL=http://localhost:3000

# Phase III (new)
OPENAI_API_KEY=sk-proj-...your-openai-api-key...
MCP_SERVER_PORT=8001  # Optional, defaults to 8001
CONVERSATION_HISTORY_LIMIT=20  # Optional, defaults to 20
```

**Frontend (`frontend/.env.local`)**:
```bash
# Phase II (existing)
NEXT_PUBLIC_API_URL=http://localhost:8000

# No new environment variables needed for Phase III
```

### 4. Get OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create new secret key
3. Copy key and add to `backend/.env.local`
4. **Security**: Never commit `.env.local` to git

---

## Database Migration

### 1. Generate Migration

```bash
cd backend

# Auto-generate migration from SQLModel changes
alembic revision --autogenerate -m "Add conversation and message tables for AI chat"

# Review generated migration
# File: alembic/versions/{hash}_add_conversation_and_message_tables.py
```

### 2. Apply Migration

```bash
# Apply migration to database
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt conversations"
psql $DATABASE_URL -c "\dt messages"
```

### 3. Verify Indexes

```bash
# Check indexes were created
psql $DATABASE_URL -c "
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('conversations', 'messages')
ORDER BY tablename, indexname;
"
```

**Expected Output**:
```
conversations_pkey
idx_conversations_user_id
idx_conversations_updated_at
messages_pkey
idx_messages_conversation_id
idx_messages_conversation_created
```

---

## Backend Setup (MCP Tools)

### 1. Create MCP Directory Structure

```bash
cd backend

# Create MCP module
mkdir -p mcp
touch mcp/__init__.py
touch mcp/server.py
touch mcp/tools.py
```

### 2. Implement MCP Server (`backend/mcp/server.py`)

```python
"""
MCP (Model Context Protocol) server for TODO application.

Exposes task management functionality as AI-callable tools.
"""

from mcp import MCPServer

# Initialize MCP server
mcp = MCPServer(name="todo-mcp-server")

# Import tools to register them (do this AFTER mcp initialization)
from .tools import (
    add_task,
    list_tasks,
    complete_task,
    delete_task,
    update_task,
    get_task_summary,
    suggest_task_prioritization
)

def get_mcp_server():
    """Get the initialized MCP server instance."""
    return mcp
```

### 3. Implement MCP Tools (`backend/mcp/tools.py`)

See `/specs/003-phase-3-ai-agent/mcp-tools-spec.md` for complete implementation details.

**Example Tool Implementation**:
```python
from mcp.server import mcp
from app.auth.dependencies import verify_token
from app.models.task import Task
from app.database import get_session
from sqlmodel import Session, select
from typing import Optional, Literal
from fastapi import HTTPException

@mcp.tool()
def add_task(
    user_token: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None
) -> str:
    """
    Create a new task for the user.

    Args:
        user_token: JWT authentication token
        title: Task title (1-200 characters)
        description: Optional description
        priority: Task priority (low/normal/high)
        due_date: Optional due date (ISO format)

    Returns:
        Success message with task ID or error message
    """
    try:
        # Validate JWT and extract user_id
        user_id = verify_token(user_token)

        # Validate inputs
        if not title or len(title) > 200:
            return "Error: Title must be 1-200 characters"

        # Create task
        with Session(engine) as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority or "normal",
                due_date=due_date
            )
            session.add(task)
            session.commit()
            session.refresh(task)

        return f"Task {task.id} created: {task.title}"

    except HTTPException as e:
        return f"Authentication error: {e.detail}"
    except Exception as e:
        return f"Error creating task: {str(e)}"
```

### 4. Test MCP Tools

```bash
# Run Python REPL
python

>>> from mcp.server import get_mcp_server
>>> mcp = get_mcp_server()
>>> tools = mcp.list_tools()
>>> len(tools)
7  # Should show 7 tools

>>> [tool.name for tool in tools]
['add_task', 'list_tasks', 'complete_task', 'delete_task', 'update_task', 'get_task_summary', 'suggest_task_prioritization']
```

---

## Agent Orchestration

### 1. Create Agent Module

```bash
cd backend
mkdir -p agents
touch agents/__init__.py
touch agents/chat_agent.py
```

### 2. Implement Agent Runner (`backend/agents/chat_agent.py`)

```python
"""
AI Chat Agent orchestration using OpenAI Agents SDK and MCP tools.
"""

import os
from openai import OpenAI
from mcp.server import get_mcp_server
from typing import List, Dict, Any

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
mcp_server = get_mcp_server()

SYSTEM_PROMPT = """
You are a helpful AI assistant managing the user's TODO list.

You can create, update, list, and delete tasks using the available tools.
When the user asks to create a task, extract the title, priority, and due date
from their natural language description.

Priority keywords:
- High: urgent, asap, critical, emergency, important
- Low: maybe, sometime, eventually, nice to have
- Normal: default

Temporal expressions:
- "tomorrow" → next calendar day
- "next week" → 7 days from now
- "Monday" → next occurrence of Monday
- ISO dates (YYYY-MM-DD) → exact date

Always confirm task operations and provide helpful summaries.
"""

def execute_agent(
    conversation_history: List[Dict[str, str]],
    user_token: str
) -> Dict[str, Any]:
    """
    Execute AI agent with conversation history and MCP tools.

    Args:
        conversation_history: List of {role, content} messages
        user_token: JWT token for MCP tool authentication

    Returns:
        Dict with agent_response and tool_calls
    """
    # Prepare messages with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)

    # Get MCP tools in OpenAI format
    tools = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
        }
        for tool in mcp_server.list_tools()
    ]

    # Execute agent
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # Process tool calls if any
    tool_calls_log = []
    message = response.choices[0].message

    if message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # Add user_token to tool arguments
            tool_args["user_token"] = user_token

            # Execute MCP tool
            tool_result = mcp_server.call_tool(tool_name, **tool_args)

            # Log tool execution
            tool_calls_log.append({
                "tool": tool_name,
                "arguments": tool_args,
                "result": tool_result
            })

    return {
        "agent_response": message.content,
        "tool_calls": tool_calls_log
    }
```

### 3. Create Chat API Endpoint (`backend/app/routers/chat.py`)

```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.models.conversation import Conversation
from app.models.message import Message
from agents.chat_agent import execute_agent
from typing import Annotated
from uuid import UUID

router = APIRouter(prefix="/api/{user_id}", tags=["Chat"])

@router.post("/chat")
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
    token: str = Depends(get_jwt_token)
):
    """Send message to AI agent."""
    # Verify user_id matches token
    if user_id != current_user:
        raise HTTPException(status_code=403)

    # Load or create conversation
    if request.conversation_id:
        conversation = get_conversation(request.conversation_id, user_id)
    else:
        conversation = create_conversation(user_id)

    # Load history
    history = load_conversation_history(conversation.id, limit=20)

    # Save user message
    user_message = save_message(conversation.id, "user", request.message)

    # Execute agent
    result = execute_agent(history + [{"role": "user", "content": request.message}], token)

    # Save assistant response
    assistant_message = save_message(
        conversation.id,
        "assistant",
        result["agent_response"],
        tool_calls=json.dumps(result["tool_calls"])
    )

    return {
        "conversation_id": conversation.id,
        "message": assistant_message,
        "tool_calls": result["tool_calls"]
    }
```

### 4. Register Router in Main App

```python
# backend/app/main.py

from app.routers import chat

app.include_router(chat.router)
```

---

## Frontend Integration (ChatKit)

### 1. Create Agent Page (`frontend/app/agent/page.tsx`)

```typescript
'use client';

import { ChatInterface } from '@openai/chatkit-react';
import { useAuth } from '@/lib/auth-context';

export default function AgentPage() {
  const { user, token } = useAuth();

  if (!user || !token) {
    return <div>Please log in to use the AI assistant</div>;
  }

  return (
    <div className="h-screen">
      <ChatInterface
        apiEndpoint={`${process.env.NEXT_PUBLIC_API_URL}/api/${user.id}/chat`}
        authToken={token}
        onToolCall={(tool, args) => {
          console.log(`Tool executed: ${tool}`, args);
        }}
        theme="custom"
        className="h-full"
      />
    </div>
  );
}
```

### 2. Add Navigation Link

```typescript
// frontend/app/layout.tsx or components/nav.tsx

<Link href="/agent">
  <Button>AI Assistant</Button>
</Link>
```

---

## Testing

### 1. Backend Unit Tests

```bash
cd backend

# Test MCP tools
pytest tests/test_mcp_tools.py -v

# Test agent execution
pytest tests/test_chat_agent.py -v

# Test chat API endpoint
pytest tests/test_chat_api.py -v
```

### 2. Integration Tests

```bash
# Full conversation flow test
pytest tests/integration/test_conversation_flow.py -v
```

### 3. Frontend Testing

```bash
cd frontend

# Start development server
npm run dev

# Navigate to http://localhost:3000/agent
# Test conversation:
# 1. "Create a task to buy groceries tomorrow"
# 2. "Show me my tasks"
# 3. "Mark task 1 as complete"
```

---

## Deployment

### 1. Vercel Deployment (Production)

```bash
# Set OpenAI API key
vercel env add OPENAI_API_KEY production

# Deploy backend
cd backend
vercel --prod

# Deploy frontend
cd frontend
vercel --prod
```

### 2. Database Migration (Production)

```bash
# Run migration on production database
DATABASE_URL=<production-url> alembic upgrade head
```

---

## Troubleshooting

### Common Issues

**1. "OpenAI API key not found"**
```bash
# Verify environment variable
echo $OPENAI_API_KEY

# Reload .env.local
source backend/.env.local
```

**2. "MCP tools not found"**
```bash
# Verify MCP server initialization
python -c "from mcp.server import get_mcp_server; print(len(get_mcp_server().list_tools()))"

# Expected output: 7
```

**3. "Agent response timeout"**
```bash
# Check OpenAI API status
curl https://status.openai.com/api/v2/status.json

# Increase timeout in agent code
response = client.chat.completions.create(..., timeout=30)
```

**4. "Conversation history not loading"**
```bash
# Verify database indexes
psql $DATABASE_URL -c "SELECT * FROM pg_stat_user_indexes WHERE relname IN ('conversations', 'messages');"

# Check query performance
psql $DATABASE_URL -c "EXPLAIN ANALYZE SELECT * FROM messages WHERE conversation_id = 1 ORDER BY created_at DESC LIMIT 20;"
```

**5. "ChatKit component not rendering"**
```bash
# Verify package installation
npm list @openai/chatkit-react

# Check browser console for errors
# Ensure API endpoint URL is correct
```

---

## Verification Checklist

- [ ] Backend dependencies installed (openai, mcp, python-dateutil)
- [ ] Frontend dependencies installed (@openai/chatkit-react)
- [ ] Environment variables configured (OPENAI_API_KEY)
- [ ] Database migration applied (conversations and messages tables)
- [ ] MCP tools registered (7 tools available)
- [ ] Agent can create tasks via natural language
- [ ] Conversation history persists across requests
- [ ] ChatKit UI renders correctly
- [ ] Multi-user isolation enforced (JWT validation)
- [ ] Tool calls logged in messages.tool_calls

---

## Next Steps

1. **Create Tasks via Agent**: Test natural language task creation
2. **Explore MCP Tools**: Try all 7 tools through conversation
3. **Review Conversation History**: Verify persistence
4. **Test Multi-User Isolation**: Create second user, verify separation
5. **Deploy to Production**: Follow deployment guide above

For detailed implementation references:
- **MCP Tools Spec**: `/specs/003-phase-3-ai-agent/mcp-tools-spec.md`
- **Data Model**: `/specs/003-phase-3-ai-agent/data-model.md`
- **API Contract**: `/specs/003-phase-3-ai-agent/contracts/chat-api.openapi.yaml`
- **Research**: `/specs/003-phase-3-ai-agent/research.md`
