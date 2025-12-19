---
name: chatkit-integrator
description: Integrate OpenAI Chatkit into Next.js applications with database-backed conversation persistence. Use when implementing AI chat interfaces that require: (1) OpenAI Chatkit React components for chat UI, (2) Database-backed conversation history (PostgreSQL/Neon), (3) Stateless agent architecture with message persistence, (4) Custom backend adapter for FastAPI integration, (5) JWT-authenticated chat endpoints, (6) Real-time message updates via HTTP polling, or (7) Multi-conversation management with tenant isolation. This skill provides complete backend (FastAPI + SQLModel) and frontend (Next.js + TypeScript) integration patterns.
---

# OpenAI Chatkit Integrator

This skill guides you through integrating OpenAI Chatkit with database-backed conversation persistence in a Next.js + FastAPI application stack.

## Architecture Overview

Three-layer architecture:
1. **Frontend**: OpenAI Chatkit React components (chat UI)
2. **Backend API**: FastAPI REST endpoints (conversation/message CRUD)
3. **Database**: PostgreSQL with conversations and messages tables

**Critical requirement**: Stateless design - all conversation history must be fetched from database on every request.

## Quick Start Workflow

### Step 1: Review Implementation Guide

Read the comprehensive implementation guide:
```bash
.claude/skills/chatkit-integrator/references/implementation-guide.md
```

This guide provides:
- Complete backend setup (database models, migration, schemas, router, agent)
- Complete frontend setup (dependencies, types, API client, Chatkit config)
- Configuration (CORS, environment variables)
- Testing procedures
- Common issues and troubleshooting

### Step 2: Backend Setup

**Install dependencies:**
```bash
cd backend
pip install openai-agents-sdk==0.2.0 mcp-python==0.1.5
```

**Create database models** in `backend/app/models.py`:
- Add `Conversation` model (id, user_id, title, created_at, updated_at, deleted_at)
- Add `Message` model (id, conversation_id, role, content, tool_calls, created_at)

**Create migration:**
```bash
alembic revision -m "add_conversations_messages"
# Edit migration file with schema from implementation-guide.md
alembic upgrade head
```

**Create Pydantic schemas:**
- `backend/app/schemas/conversation.py` (ConversationCreate, ConversationResponse)
- `backend/app/schemas/message.py` (MessageCreate, MessageResponse)

**Create chat router** in `backend/app/routers/chat.py`:
- POST /api/chat/conversations (create)
- GET /api/chat/conversations (list with pagination)
- GET /api/chat/conversations/{id}/messages (get history)
- POST /api/chat/conversations/{id}/messages (send message)

**Implement stateless agent:**
- Create `backend/app/agents/context_manager.py` with `load_conversation_context()`
- Create `backend/app/agents/chat_agent.py` with `run_agent()`
- Agent MUST load full conversation history from database every request (stateless requirement)

### Step 3: Frontend Setup

**Install dependencies:**
```bash
cd frontend
npm install @openai/chatkit
```

**Copy asset templates to your project:**

1. **TypeScript types** - Copy `assets/chat-types.ts` to `frontend/src/types/chat.ts`
   - Provides: Conversation, Message, ChatkitAdapter interfaces
   - Type guards and validation utilities

2. **API client** - Copy `assets/chat-api-client.ts` to `frontend/src/lib/api/chat.ts`
   - Provides: conversationApi, messageApi, chatApi
   - JWT authentication headers
   - Error handling utilities
   - Chatkit adapter implementation

3. **Chatkit config** - Copy `assets/chatkit-config.ts` to `frontend/src/lib/chatkit-config.ts`
   - Provides: Complete Chatkit configuration
   - Custom backend adapter
   - Polling interval (2s for real-time updates)
   - Theme and UI customization

**Create chat page** in `frontend/src/app/chat/page.tsx`:
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

### Step 4: Configuration

**Backend CORS** in `backend/app/main.py`:
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

**Environment variables:**
- Backend `.env`: `OPENAI_API_KEY`, `DATABASE_URL`
- Frontend `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8000`

### Step 5: Testing

1. **Create conversation**: Click "New Chat", should create empty conversation
2. **Send message**: Type "Hello", should get AI response
3. **Reload page**: Should load conversation history
4. **Multiple conversations**: Create new conversation, switch between them

## Key Implementation Details

### Stateless Agent Pattern

**Critical**: Agent runtime MUST NOT store conversation state in memory.

```python
# CORRECT: Load history from database every request
async def run_agent(conversation_id: str, user_message: str, user_id: str, db: Session):
    history = load_conversation_context(conversation_id, db)  # Fetch from DB
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    # ... call OpenAI with messages
```

**Why**: Enables horizontal scaling, load balancing, and constitutional compliance.

### Tenant Isolation

**All conversation queries MUST filter by user_id:**

```python
conversation = db.get(Conversation, conversation_id)
if not conversation or conversation.user_id != current_user.id:
    raise HTTPException(status_code=404)
```

### Performance Optimization

- Database indexes: `(user_id, updated_at DESC)`, `(conversation_id, created_at ASC)`
- Cursor-based pagination for conversation list
- HTTP polling (2-3s interval) for real-time updates
- Limit conversation history to last 50 messages for AI context

## Common Issues

**CORS errors**: Verify frontend URL in backend CORS allow_origins

**Messages not persisting**: Check database connection, verify models are imported

**Agent not responding**: Verify OPENAI_API_KEY is set, check logs

**Chatkit not loading**: Verify `@openai/chatkit` is installed, check browser console

## Reference Files

- **Implementation Guide**: `references/implementation-guide.md` - Complete step-by-step setup
- **TypeScript Types**: `assets/chat-types.ts` - Copy to `frontend/src/types/chat.ts`
- **API Client**: `assets/chat-api-client.ts` - Copy to `frontend/src/lib/api/chat.ts`
- **Chatkit Config**: `assets/chatkit-config.ts` - Copy to `frontend/src/lib/chatkit-config.ts`

## Security Checklist

- ✓ All endpoints require JWT authentication
- ✓ user_id validation on all conversation access
- ✓ Input validation (10,000 char limit for messages)
- ✓ SQL injection protection (using SQLModel ORM)
- ✓ CORS configured for specific origins only
