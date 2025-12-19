# Implementation Plan: OpenAI Chatkit Integration & History Persistence

**Branch**: `006-chatkit-history-persistence` | **Date**: 2025-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-chatkit-history-persistence/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate OpenAI Chatkit into the Next.js frontend and implement stateless AI agent with database-backed conversation history. This Phase III enhancement adds AI-powered task assistance while maintaining the constitutional requirement for stateless agent architecture. All conversation history will be persisted in Neon PostgreSQL, fetched on every request, and managed through a clean separation of concerns between the frontend chat UI, backend API, and agent orchestration layer.

**Primary Requirement**: Enable users to interact with an AI assistant for task management through natural language chat, with full conversation persistence and multi-conversation support.

**Technical Approach**: Three-layer architecture - (1) OpenAI Chatkit React components in Next.js frontend for chat UI, (2) FastAPI REST endpoints for conversation/message CRUD operations, (3) Stateless agent runtime that fetches history from database and executes MCP tools for task operations.

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ (existing Phase II stack)
- Frontend: TypeScript 5.x with Next.js 16+ App Router

**Primary Dependencies**:
- Backend: FastAPI 0.95.2, SQLModel 0.0.14, OpenAI Agents SDK, MCP Python SDK
- Frontend: Next.js 16+, React 18+, OpenAI ChatKit, Tailwind CSS
- Database: Neon PostgreSQL (SQLite for local development)

**Storage**:
- Neon PostgreSQL with two new tables: `conversations` (id, user_id, title, created_at, updated_at, deleted_at) and `messages` (id, conversation_id, role, content, tool_calls, created_at)
- All conversation history persisted in database (NO in-memory state)

**Testing**:
- Backend: pytest with fixtures for conversation/message CRUD
- Frontend: Jest/Vitest with React Testing Library for Chatkit integration
- Integration: API contract tests for chat endpoints
- E2E: Playwright for full conversation flow

**Target Platform**:
- Web application (desktop and mobile browsers)
- Deployment: Vercel (frontend and backend), Neon (database)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Message delivery: <5 seconds (spec SC-001)
- History load: <2 seconds for 100 messages (spec SC-003)
- Operation success rate: 95% (spec SC-006)
- Support 50 concurrent conversations without degradation (spec SC-007)

**Constraints**:
- Stateless agent architecture (constitutional requirement - NO in-memory state)
- 100% message persistence (spec SC-002)
- Zero cross-tenant data leakage (spec SC-010)
- All requests require JWT authentication
- User_id validation on every operation

**Scale/Scope**:
- Multi-user support (tenant isolation via user_id)
- Unlimited conversations per user initially
- Messages limited to 10,000 characters each
- Tool call metadata stored as JSON

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Compliance

✅ **Phase III Technology Stack**:
- Using Phase II stack (Next.js, FastAPI, Neon) ✓
- Adding OpenAI Agents SDK ✓
- Adding MCP Python SDK ✓
- Adding OpenAI ChatKit (frontend) ✓
- No premature Phase IV/V technologies ✓

✅ **Stateless Agent Architecture (CRITICAL)**:
- Agent MUST be stateless (NO in-memory conversation state) ✓
- All conversation history fetched from database on every request ✓
- Agent communicates with backend exclusively through MCP tools ✓
- Agent cannot directly access database (must use MCP tools) ✓
- Multiple agent instances can serve same user (load balancing compatible) ✓

✅ **State Management Compliance**:
- conversations table: id, user_id, title, created_at, updated_at ✓
- messages table: id, conversation_id, role, content, created_at ✓
- Conversation history fetched from database at request start ✓
- Conversation state saved to database before request completion ✓
- Agent runtime can be restarted without losing context ✓

✅ **MCP Tool Integration**:
- Agent will use existing MCP tools (list_tasks, create_task, etc.) ✓
- New conversation management does NOT require new MCP tools (uses REST API) ✓
- Tool-based architecture for task operations maintained ✓

✅ **Security Constraints**:
- Agent MUST extract user_id from JWT token ✓
- All operations validate token-derived user_id matches path user_id ✓
- Agent conversations scoped to single user ✓
- All agent requests require valid JWT authentication ✓
- Failed user_id validation MUST return 403 Forbidden ✓

✅ **Spec-First Development**:
- Feature spec created and approved (spec.md) ✓
- All requirements have testable acceptance criteria ✓
- Success criteria are measurable ✓
- Technology-agnostic requirements defined ✓

### Gates Assessment

| Gate | Status | Notes |
|------|--------|-------|
| Phase III stack compliance | ✅ PASS | All dependencies approved for Phase III |
| Stateless agent requirement | ✅ PASS | Database-backed history, no in-memory state |
| MCP tool architecture | ✅ PASS | Existing MCP tools reused, agent layer separated |
| Security (tenant isolation) | ✅ PASS | user_id validation enforced at all layers |
| Spec-first discipline | ✅ PASS | Comprehensive spec with acceptance criteria |
| No premature complexity | ✅ PASS | Building on Phase II, no Phase IV features |

**Overall**: ✅ **ALL GATES PASS** - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/006-chatkit-history-persistence/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoints
│   └── models.ts        # TypeScript interfaces for frontend
├── checklists/
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models.py                    # SQLModel schemas (add Conversation, Message)
│   ├── routers/
│   │   ├── chat.py                  # NEW: Chat API endpoints
│   │   └── tasks.py                 # Existing task endpoints
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── chat_agent.py            # NEW: Stateless AI agent orchestration
│   │   └── context_manager.py       # NEW: Fetch/save conversation history
│   ├── mcp/
│   │   ├── server.py                # Existing MCP server (no changes needed)
│   │   └── tools/                   # Existing MCP tools (list_tasks, create_task, etc.)
│   └── schemas/
│       ├── conversation.py          # NEW: Pydantic schemas for conversations
│       └── message.py               # NEW: Pydantic schemas for messages
├── tests/
│   ├── unit/
│   │   ├── test_conversation_crud.py    # NEW: Unit tests for conversation operations
│   │   └── test_message_crud.py         # NEW: Unit tests for message operations
│   ├── integration/
│   │   ├── test_chat_api.py             # NEW: Integration tests for chat endpoints
│   │   └── test_agent_stateless.py      # NEW: Verify stateless agent behavior
│   └── fixtures/
│       └── conversation_fixtures.py     # NEW: Test data for conversations/messages
└── alembic/
    └── versions/
        └── xxxx_add_conversations_messages.py  # NEW: Database migration

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   └── page.tsx             # NEW: Main chat page with Chatkit integration
│   │   └── layout.tsx               # Update: Add chat navigation
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx        # NEW: OpenAI Chatkit wrapper component
│   │   │   ├── ConversationList.tsx     # NEW: Sidebar with conversation history
│   │   │   └── MessageBubble.tsx        # NEW: Custom message rendering
│   │   └── layout/
│   │       └── Sidebar.tsx              # Update: Add "Chat" menu item
│   ├── lib/
│   │   ├── api/
│   │   │   └── chat.ts                  # NEW: API client for chat endpoints
│   │   └── chatkit-config.ts            # NEW: Chatkit configuration
│   └── types/
│       └── chat.ts                      # NEW: TypeScript interfaces (Conversation, Message)
├── tests/
│   ├── components/
│   │   └── ChatInterface.test.tsx       # NEW: Component tests for Chatkit integration
│   └── integration/
│       └── chat-flow.test.ts            # NEW: E2E tests for conversation flow
└── package.json                         # Update: Add @openai/chatkit dependency
```

**Structure Decision**: Web application structure (Option 2) selected. This feature builds upon the existing Phase II backend (FastAPI + Neon) and frontend (Next.js + App Router) by adding:

1. **Backend additions**: New `chat.py` router for conversation/message CRUD, `agents/` directory for stateless agent orchestration, new schemas for conversations/messages, database migration for new tables.

2. **Frontend additions**: New `/chat` page with OpenAI Chatkit integration, reusable chat components, API client for chat endpoints, TypeScript types matching backend schemas.

3. **Integration point**: Agent orchestration layer (`agents/chat_agent.py`) sits between frontend chat requests and existing MCP tools, maintaining stateless architecture by fetching conversation history from database on every request.

## Complexity Tracking

> **No constitutional violations** - All gates pass. This section intentionally left empty.
