# Quickstart Guide: OpenAI Chatkit Integration & History Persistence

**Feature**: Phase III Chat Implementation
**Branch**: `006-chatkit-history-persistence`
**Date**: 2025-12-19

## Overview

This guide provides step-by-step instructions for implementing the OpenAI Chatkit integration with database-backed conversation history. Follow these steps in order to build the feature according to the specification.

## Prerequisites

- Phase II backend and frontend already running
- Neon PostgreSQL database accessible
- OpenAI API key configured
- Local development environment set up

## Implementation Phases

### Phase 1: Database Schema (Backend)

**Time estimate**: 30 minutes

1. **Create database migration**:

```bash
cd backend
alembic revision -m "add_conversations_messages_tables"
```

2. **Edit migration file** (`backend/alembic/versions/xxxx_add_conversations_messages_tables.py`):
   - Copy schema from `data-model.md` migration section
   - Create `conversations` table with indexes
   - Create `messages` table with indexes
   - Add enum for `message_role`

3. **Run migration**:

```bash
alembic upgrade head
```

4. **Verify tables created**:

```bash
# Connect to database
psql $DATABASE_URL

# Check tables
\dt conversations messages

# Check indexes
\di conversations_*
\di messages_*
```

**Acceptance**: Tables `conversations` and `messages` exist with all indexes

---

### Phase 2: Backend Models (Backend)

**Time estimate**: 45 minutes

1. **Add SQLModel schemas** to `backend/app/models.py`:

```python
# Add to existing models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"
    # ... (copy from data-model.md)

class Message(SQLModel, table=True):
    __tablename__ = "messages"
    # ... (copy from data-model.md)
```

2. **Create Pydantic schemas** in `backend/app/schemas/conversation.py`:

```python
from pydantic import BaseModel, Field, validator
# ... (copy from data-model.md)
```

3. **Create Pydantic schemas** in `backend/app/schemas/message.py`:

```python
from pydantic import BaseModel, Field
# ... (copy from data-model.md)
```

**Acceptance**: Models import without errors, schemas validate correctly

---

### Phase 3: Chat API Endpoints (Backend)

**Time estimate**: 2 hours

1. **Create router** `backend/app/routers/chat.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.dependencies import get_current_user, get_session
from app.models import User, Conversation, Message
from app.schemas.conversation import *
from app.schemas.message import *
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
    limit: int = 20,
    cursor: Optional[str] = None
):
    """List user's conversations with cursor pagination"""
    # Implementation: Filter by user_id, apply cursor, order by updated_at DESC
    pass

@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Create new conversation"""
    # Implementation: Create conversation with user_id from JWT
    pass

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get conversation by ID (validate ownership)"""
    # Implementation: Validate user owns conversation
    pass

@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Update conversation title"""
    # Implementation: Validate ownership, update title
    pass

@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Soft delete conversation"""
    # Implementation: Set deleted_at timestamp
    pass

@router.get("/conversations/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
    limit: int = 50,
    since: Optional[str] = None
):
    """Get conversation message history"""
    # Implementation: Validate ownership, return messages
    pass

@router.post("/conversations/{conversation_id}/messages", response_model=SendMessageResponse, status_code=201)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Send user message and get AI response"""
    # Implementation:
    # 1. Validate conversation ownership
    # 2. Save user message
    # 3. Load conversation history
    # 4. Run agent (see Phase 4)
    # 5. Save assistant message
    # 6. Return both messages
    pass
```

2. **Register router** in `backend/app/main.py`:

```python
from app.routers import chat

app.include_router(chat.router)
```

3. **Add CORS configuration** for frontend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

**Acceptance**: All endpoints return 404/401/403 appropriately (agent not yet implemented)

---

### Phase 4: Stateless Agent Orchestration (Backend)

**Time estimate**: 2 hours

1. **Create context manager** `backend/app/agents/context_manager.py`:

```python
from sqlmodel import Session, select
from app.models import Message, Conversation
from typing import List
from datetime import datetime

def load_conversation_context(
    conversation_id: str,
    db: Session,
    limit: int = 50
) -> List[Message]:
    """
    Load conversation history for agent context.
    Stateless: fetches from database on every request.
    """
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.desc()
    ).limit(limit)

    messages = db.exec(statement).all()
    return list(reversed(messages))  # Chronological order

def save_message(
    conversation_id: str,
    role: str,
    content: str,
    tool_calls: dict = None,
    db: Session = None
) -> Message:
    """Save message to database"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    db.add(message)

    # Update conversation updated_at
    conversation = db.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)
    return message
```

2. **Create agent runner** `backend/app/agents/chat_agent.py`:

```python
from openai import OpenAI
from app.agents.context_manager import load_conversation_context, save_message
from app.mcp.tools import get_mcp_tools
from sqlmodel import Session

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(
    conversation_id: str,
    user_message: str,
    user_id: str,
    db: Session
) -> dict:
    """
    Run stateless AI agent.

    Constitutional compliance:
    - Loads full conversation history from database
    - No in-memory state retention
    - Uses MCP tools for task operations
    - Returns assistant response with tool call metadata
    """
    # 1. Load conversation history (stateless requirement)
    history = load_conversation_context(conversation_id, db)

    # 2. Build messages array for OpenAI
    messages = [
        {"role": "system", "content": "You are a helpful TODO list assistant."}
    ]
    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    messages.append({
        "role": "user",
        "content": user_message
    })

    # 3. Get MCP tools (existing tools from Phase II)
    tools = get_mcp_tools(user_id)

    # 4. Call OpenAI API with tools
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    # 5. Process tool calls if any
    assistant_message = response.choices[0].message
    tool_calls_metadata = None

    if assistant_message.tool_calls:
        tool_calls_metadata = {
            "tool_calls": [
                {
                    "tool_name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                    "result": execute_tool(tc, user_id),  # Execute MCP tool
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "success"
                }
                for tc in assistant_message.tool_calls
            ]
        }

    # 6. Return response
    return {
        "content": assistant_message.content or "Tool executed",
        "tool_calls": tool_calls_metadata
    }
```

3. **Integrate agent into send_message endpoint**:

```python
@router.post("/conversations/{conversation_id}/messages")
async def send_message(...):
    # ... validation code ...

    # Save user message
    user_msg = save_message(
        conversation_id=conversation_id,
        role="user",
        content=data.content,
        db=db
    )

    # Run agent (stateless)
    agent_response = await run_agent(
        conversation_id=conversation_id,
        user_message=data.content,
        user_id=current_user.id,
        db=db
    )

    # Save assistant message
    assistant_msg = save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=agent_response["content"],
        tool_calls=agent_response.get("tool_calls"),
        db=db
    )

    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg
    }
```

**Acceptance**: Send message triggers agent, agent uses MCP tools, response saved to database

---

### Phase 5: Frontend Setup (Frontend)

**Time estimate**: 1 hour

1. **Install dependencies**:

```bash
cd frontend
npm install @openai/chatkit
```

2. **Create TypeScript types** (`frontend/src/types/chat.ts`):
   - Copy from `contracts/models.ts`

3. **Create API client** (`frontend/src/lib/api/chat.ts`):

```typescript
import type {
  Conversation,
  ConversationCreate,
  ConversationUpdate,
  ConversationListResponse,
  Message,
  MessageCreate,
  MessageListResponse,
  SendMessageResponse,
  ListConversationsParams,
  ListMessagesParams
} from '@/types/chat';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('jwt_token');

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const chatApi = {
  async listConversations(params?: ListConversationsParams): Promise<ConversationListResponse> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.cursor) query.set('cursor', params.cursor);

    return fetchWithAuth(`/api/chat/conversations?${query}`);
  },

  async createConversation(data: ConversationCreate): Promise<Conversation> {
    return fetchWithAuth('/api/chat/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async getConversation(id: string): Promise<Conversation> {
    return fetchWithAuth(`/api/chat/conversations/${id}`);
  },

  async updateConversationTitle(id: string, data: ConversationUpdate): Promise<Conversation> {
    return fetchWithAuth(`/api/chat/conversations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteConversation(id: string): Promise<void> {
    return fetchWithAuth(`/api/chat/conversations/${id}`, {
      method: 'DELETE',
    });
  },

  async getMessages(conversationId: string, params?: ListMessagesParams): Promise<MessageListResponse> {
    const query = new URLSearchParams();
    if (params?.limit) query.set('limit', params.limit.toString());
    if (params?.since) query.set('since', params.since);

    return fetchWithAuth(`/api/chat/conversations/${conversationId}/messages?${query}`);
  },

  async sendMessage(conversationId: string, data: MessageCreate): Promise<SendMessageResponse> {
    return fetchWithAuth(`/api/chat/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};
```

**Acceptance**: API client can be imported and typed correctly

---

### Phase 6: Chatkit Integration (Frontend)

**Time estimate**: 2 hours

1. **Create Chatkit configuration** (`frontend/src/lib/chatkit-config.ts`):

```typescript
import { chatApi } from '@/lib/api/chat';
import type { ChatkitConfig } from '@/types/chat';

export const chatkitConfig: ChatkitConfig = {
  adapter: {
    async getConversations() {
      const response = await chatApi.listConversations();
      return response.conversations;
    },

    async getMessages(conversationId: string) {
      const response = await chatApi.getMessages(conversationId);
      return response.messages;
    },

    async sendMessage(conversationId: string, content: string) {
      return chatApi.sendMessage(conversationId, { content });
    },

    async createConversation(title?: string) {
      return chatApi.createConversation({ title });
    },

    async updateConversationTitle(conversationId: string, title: string) {
      return chatApi.updateConversationTitle(conversationId, { title });
    },

    async deleteConversation(conversationId: string) {
      await chatApi.deleteConversation(conversationId);
    },
  },
  enableMarkdown: true,
  enableSyntaxHighlighting: true,
  pollingInterval: 2000, // Poll for new messages every 2 seconds
  maxMessageLength: 10000,
};
```

2. **Create chat page** (`frontend/src/app/chat/page.tsx`):

```typescript
'use client';

import { ChatKit } from '@openai/chatkit';
import { chatkitConfig } from '@/lib/chatkit-config';

export default function ChatPage() {
  return (
    <div className="h-screen flex flex-col">
      <header className="border-b p-4">
        <h1 className="text-2xl font-bold">AI Assistant</h1>
      </header>
      <main className="flex-1 overflow-hidden">
        <ChatKit config={chatkitConfig} />
      </main>
    </div>
  );
}
```

3. **Add chat navigation** to `frontend/src/app/layout.tsx`:

```typescript
// Add to navigation menu
<Link href="/chat" className="nav-link">
  Chat
</Link>
```

**Acceptance**: Chat page loads, can create conversation, send messages, see AI responses

---

### Phase 7: Testing (Backend + Frontend)

**Time estimate**: 2 hours

1. **Backend unit tests** (`backend/tests/unit/test_conversation_crud.py`):

```python
def test_create_conversation(client, auth_headers):
    response = client.post(
        "/api/chat/conversations",
        json={"title": "Test Chat"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Chat"
    assert "id" in data

def test_list_conversations_enforces_tenant_isolation(client, auth_headers, other_user_conversation):
    response = client.get("/api/chat/conversations", headers=auth_headers)
    assert response.status_code == 200
    conversations = response.json()["conversations"]
    # Should only see own conversations
    assert all(c["user_id"] == current_user.id for c in conversations)
```

2. **Backend integration tests** (`backend/tests/integration/test_chat_api.py`):

```python
def test_send_message_triggers_agent(client, auth_headers, conversation):
    response = client.post(
        f"/api/chat/conversations/{conversation.id}/messages",
        json={"content": "List my tasks"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert "user_message" in data
    assert "assistant_message" in data
    assert data["assistant_message"]["role"] == "assistant"
```

3. **Frontend component tests** (`frontend/tests/components/ChatInterface.test.tsx`):

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatPage from '@/app/chat/page';

test('sends message and displays response', async () => {
  render(<ChatPage />);

  const input = screen.getByPlaceholderText('Type a message...');
  await userEvent.type(input, 'Hello AI');
  await userEvent.click(screen.getByText('Send'));

  await waitFor(() => {
    expect(screen.getByText('Hello AI')).toBeInTheDocument();
    expect(screen.getByText(/AI response/i)).toBeInTheDocument();
  });
});
```

**Acceptance**: All tests pass (pytest backend, Jest frontend)

---

## Deployment Checklist

- [ ] Database migration applied to production Neon database
- [ ] Environment variables set (OPENAI_API_KEY)
- [ ] CORS origins configured for production frontend URL
- [ ] Frontend deployed to Vercel with updated dependencies
- [ ] Backend deployed to Vercel with new routes
- [ ] Smoke test: Create conversation, send message, verify persistence
- [ ] Monitor logs for errors on first production use

## Troubleshooting

**Issue**: "Conversation not found" error
**Solution**: Ensure user_id from JWT matches conversation owner

**Issue**: Agent not responding
**Solution**: Check OpenAI API key, verify MCP tools are registered

**Issue**: Messages not appearing in real-time
**Solution**: Verify polling interval, check for JavaScript console errors

**Issue**: CORS errors in browser
**Solution**: Verify frontend URL in backend CORS allow_origins list

## Next Steps

After implementation complete:
1. Run `/sp.tasks` to generate detailed task breakdown
2. Execute tasks in priority order
3. Create PHR documenting implementation progress
4. Update ADR if architectural decisions made during implementation

## Resources

- Spec: `specs/006-chatkit-history-persistence/spec.md`
- Data Model: `specs/006-chatkit-history-persistence/data-model.md`
- API Contracts: `specs/006-chatkit-history-persistence/contracts/chat-api.yaml`
- Research: `specs/006-chatkit-history-persistence/research.md`
- OpenAI Chatkit Docs: https://platform.openai.com/docs/chatkit
- MCP Python SDK: https://modelcontextprotocol.io/docs/python
