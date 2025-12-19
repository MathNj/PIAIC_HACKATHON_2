# OpenAI Chatkit Integration - Implementation Guide

## Overview

This guide provides step-by-step instructions for integrating OpenAI Chatkit with database-backed conversation persistence in a Next.js + FastAPI stack.

## Architecture Pattern

**Three-layer architecture**:
1. **Frontend**: OpenAI Chatkit React components (chat UI)
2. **Backend API**: FastAPI REST endpoints (conversation/message CRUD)
3. **Database**: PostgreSQL with conversations and messages tables

**Critical Requirement**: Stateless design - all conversation history must be fetched from database on every request.

## Implementation Steps

### Phase 1: Backend Setup

#### 1.1 Install Dependencies

```bash
# Backend
cd backend
pip install openai-agents-sdk==0.2.0 mcp-python==0.1.5
```

#### 1.2 Create Database Models

Add to `backend/app/models.py`:

```python
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

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    role: MessageRole
    content: str = Field(max_length=10000)
    tool_calls: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
```

#### 1.3 Create Database Migration

```bash
cd backend
alembic revision -m "add_conversations_messages"
```

Edit migration file to create tables with indexes (see data-model.md for full schema).

Run migration:
```bash
alembic upgrade head
```

#### 1.4 Create Pydantic Schemas

Create `backend/app/schemas/conversation.py`:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConversationCreate(BaseModel):
    title: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
```

Create `backend/app/schemas/message.py`:
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    tool_calls: Optional[Dict[str, Any]] = None
    created_at: datetime
```

#### 1.5 Create Chat Router

Create `backend/app/routers/chat.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.dependencies import get_current_user, get_session
from app.models import Conversation, Message
from app.schemas.conversation import *
from app.schemas.message import *

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/conversations", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    conversation = Conversation(
        user_id=current_user.id,
        title=data.title or "New Conversation"
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Validate ownership
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404)

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=data.content
    )
    db.add(user_msg)
    db.commit()

    # Run agent (see agent integration below)
    agent_response = await run_agent(conversation_id, data.content, current_user.id, db)

    # Save assistant message
    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=agent_response["content"],
        tool_calls=agent_response.get("tool_calls")
    )
    db.add(assistant_msg)
    db.commit()

    return {
        "user_message": user_msg,
        "assistant_message": assistant_msg
    }

@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Validate ownership
    conversation = db.get(Conversation, conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        raise HTTPException(status_code=404)

    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    return {"messages": messages, "conversation_id": conversation_id}
```

Register router in `backend/app/main.py`:
```python
from app.routers import chat
app.include_router(chat.router)
```

#### 1.6 Implement Stateless Agent

Create `backend/app/agents/context_manager.py`:
```python
from sqlmodel import Session, select
from app.models import Message
from typing import List

def load_conversation_context(conversation_id: str, db: Session, limit: int = 50) -> List[Message]:
    """Load last 50 messages for agent context (stateless requirement)"""
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    ).all()
    return list(reversed(messages))  # Chronological order
```

Create `backend/app/agents/chat_agent.py`:
```python
from openai import OpenAI
from app.agents.context_manager import load_conversation_context
from sqlmodel import Session

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(conversation_id: str, user_message: str, user_id: str, db: Session) -> dict:
    # Load conversation history (stateless - fetch from DB every time)
    history = load_conversation_context(conversation_id, db)

    # Build messages for OpenAI
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return {
        "content": response.choices[0].message.content,
        "tool_calls": None  # Add tool execution logic as needed
    }
```

### Phase 2: Frontend Setup

#### 2.1 Install Dependencies

```bash
cd frontend
npm install @openai/chatkit
```

#### 2.2 Create TypeScript Types

Copy `assets/chat-types.ts` to `frontend/src/types/chat.ts` (see template).

#### 2.3 Create API Client

Copy `assets/chat-api-client.ts` to `frontend/src/lib/api/chat.ts` (see template).

#### 2.4 Create Chatkit Configuration

Copy `assets/chatkit-config.ts` to `frontend/src/lib/chatkit-config.ts` and customize:

```typescript
import { chatApi } from '@/lib/api/chat';

export const chatkitConfig = {
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
    }
  },
  enableMarkdown: true,
  enableSyntaxHighlighting: true,
  pollingInterval: 2000  // Poll every 2 seconds
};
```

#### 2.5 Create Chat Page

Create `frontend/src/app/chat/page.tsx`:
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

### Phase 3: Configuration

#### 3.1 CORS Configuration

Update `backend/app/main.py`:
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

#### 3.2 Environment Variables

Backend `.env`:
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://...
```

Frontend `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

1. **Create conversation**: Click "Chat", should create empty conversation
2. **Send message**: Type "Hello", should get AI response
3. **Reload page**: Should load conversation history
4. **Multiple conversations**: Create new conversation, switch between them

## Common Issues

**Issue**: CORS errors
**Solution**: Verify frontend URL in backend CORS allow_origins

**Issue**: Messages not persisting
**Solution**: Check database connection, verify models are imported

**Issue**: Agent not responding
**Solution**: Verify OPENAI_API_KEY is set, check logs

## Performance Optimization

- Add database indexes: `(user_id, updated_at DESC)`, `(conversation_id, created_at ASC)`
- Implement cursor-based pagination for conversation list
- Use HTTP polling (2-3s interval) for real-time updates
- Limit conversation history to last 50 messages for AI context

## Security Checklist

- ✓ All endpoints require JWT authentication
- ✓ user_id validation on all conversation access
- ✓ Input validation (10,000 char limit for messages)
- ✓ SQL injection protection (using SQLModel ORM)
- ✓ CORS configured for specific origins only
