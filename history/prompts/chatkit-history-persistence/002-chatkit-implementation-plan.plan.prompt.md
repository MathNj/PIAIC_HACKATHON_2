---
id: 002
title: OpenAI Chatkit Implementation Plan Created
stage: plan
date: 2025-12-19
surface: agent
model: claude-sonnet-4-5-20250929
feature: chatkit-history-persistence
branch: 006-chatkit-history-persistence
user: MathNj
command: /sp.plan
labels: ["phase-iii", "chatkit", "planning", "architecture", "database-design", "api-design"]
links:
  spec: "specs/006-chatkit-history-persistence/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-chatkit-history-persistence/plan.md
  - specs/006-chatkit-history-persistence/research.md
  - specs/006-chatkit-history-persistence/data-model.md
  - specs/006-chatkit-history-persistence/contracts/chat-api.yaml
  - specs/006-chatkit-history-persistence/contracts/models.ts
  - specs/006-chatkit-history-persistence/quickstart.md
tests:
  - Constitutional gates validation (6/6 passed)
  - Phase III compliance check
---

## Prompt

The `/sp.plan` command was executed to generate the implementation plan for the OpenAI Chatkit Integration & History Persistence feature (spec created in PHR 001).

**Context**: Feature specification completed and validated. All requirements clear with zero ambiguities. Ready to proceed with architectural planning and design.

**Expected output**: Complete implementation plan including:
- Technical context and dependencies
- Constitution compliance check
- Phase 0: Research and technical decisions
- Phase 1: Data model, API contracts, and quick start guide

## Response snapshot

Created comprehensive implementation plan with all Phase 0 and Phase 1 deliverables.

### Plan Structure (plan.md)

**Summary**: Three-layer architecture
1. OpenAI Chatkit React components (frontend chat UI)
2. FastAPI REST endpoints (conversation/message CRUD)
3. Stateless agent runtime (fetches history, executes MCP tools)

**Technical Context**:
- Languages: Python 3.13+ (backend), TypeScript 5.x (frontend)
- Dependencies: FastAPI, SQLModel, OpenAI Agents SDK, MCP Python SDK, Next.js, Chatkit, Tailwind
- Storage: Neon PostgreSQL with `conversations` and `messages` tables
- Testing: pytest (backend), Jest/Vitest (frontend), Playwright (E2E)
- Performance: <5s message delivery, <2s history load for 100 messages, 95% success rate

**Constitution Check**: ✅ ALL GATES PASS (6/6)
- Phase III stack compliance ✓
- Stateless agent architecture ✓
- MCP tool integration ✓
- Security (tenant isolation) ✓
- Spec-first discipline ✓
- No premature complexity ✓

**Project Structure**: Defined backend and frontend file organization with NEW markers for all additions

### Phase 0: Research (research.md)

Made 10 critical technical decisions with research and alternatives analysis:

1. **Real-time delivery**: HTTP Polling (2-3s) - Simplicity over WebSockets complexity
2. **Conversation titles**: Auto-generate from first message - UX over manual input friction
3. **Markdown rendering**: Chatkit built-in - Zero config over custom implementation
4. **Tool metadata storage**: JSONB column - Flexibility and queryability
5. **Chatkit integration**: Custom adapter - Control and existing auth integration
6. **Agent context loading**: Full history query (LIMIT 50) - Stateless compliance
7. **Conversation pagination**: Cursor-based (created_at) - Performance and consistency
8. **Message size limit**: 10,000 characters - Industry standard balance
9. **Conversation deletion**: Soft delete (deleted_at) - Auditability and recovery
10. **CORS config**: Explicit origins with credentials - Security and JWT support

**Dependencies confirmed**:
- `openai-agents-sdk==0.2.0`
- `mcp-python==0.1.5`
- `@openai/chatkit==1.0.0`

### Phase 1: Data Model (data-model.md)

**Database Schema**:
- **conversations table**: id (UUID PK), user_id (FK), title, created_at, updated_at, deleted_at
- **messages table**: id (UUID PK), conversation_id (FK), role (enum), content (TEXT), tool_calls (JSONB), created_at

**Indexes** (8 total for query optimization):
- `(user_id, updated_at DESC)` - Conversation list
- `(conversation_id, created_at ASC)` - Message history
- `tool_calls USING GIN` - Tool usage analytics

**Pydantic Schemas**:
- Request: ConversationCreate, ConversationUpdate, MessageCreate
- Response: ConversationResponse, ConversationListResponse, MessageResponse, MessageListResponse, SendMessageResponse

**Alembic Migration**: Complete migration script with all tables, indexes, and constraints

**Tenant Isolation Pattern**: Demonstrated with validation functions enforcing user_id filtering

**Performance Planning**: Expected query patterns with index usage and sub-20ms targets

### Phase 1: API Contracts (contracts/)

**chat-api.yaml** (OpenAPI 3.1.0):
- 6 endpoints defined with full request/response schemas
- Security: BearerAuth (JWT) required on all endpoints
- Error responses: 400, 401, 403, 404, 500 with detailed descriptions
- Query parameters: Pagination (cursor-based), polling (since timestamp)

**models.ts** (TypeScript):
- 20+ TypeScript interfaces matching backend schemas exactly
- Type guards: isUserMessage, isAssistantMessage, hasToolCalls
- Validation utilities: validateMessageContent, validateConversationTitle
- Formatting utilities: formatTimestamp, truncateTitle, getConversationPreview
- ChatkitAdapter interface for backend integration
- Example usage patterns in comments

### Phase 1: Quickstart Guide (quickstart.md)

**7 implementation phases** with time estimates:
1. Database Schema (30 min) - Alembic migration
2. Backend Models (45 min) - SQLModel and Pydantic schemas
3. Chat API Endpoints (2 hours) - FastAPI routers with tenant isolation
4. Stateless Agent Orchestration (2 hours) - Context manager and agent runner
5. Frontend Setup (1 hour) - Dependencies and API client
6. Chatkit Integration (2 hours) - Configuration and chat page
7. Testing (2 hours) - Unit, integration, and component tests

**Code examples** for each phase with acceptance criteria

**Deployment checklist** and troubleshooting guide included

**Total estimated time**: 10 hours of implementation work

### Agent Context Updated

Ran `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to update CLAUDE.md with new Phase III technologies.

## Outcome

- ✅ Impact: Created complete implementation plan ready for task breakdown. All architectural decisions documented with rationale. Zero technical unknowns remaining. Clear path from current state to working Chatkit integration.
- 🧪 Tests: Constitutional gates validation (6/6 passed), Phase III compliance verified, stateless architecture validated
- 📁 Files: plan.md (technical context + gates), research.md (10 decisions), data-model.md (schema + migration), chat-api.yaml (OpenAPI spec), models.ts (TypeScript types), quickstart.md (7-phase guide)
- 🔁 Next prompts: Run `/sp.tasks` to generate task breakdown with story points, dependencies, and acceptance criteria. Implementation can begin immediately with quickstart guide.
- 🧠 Reflection: Research phase critical - made informed decisions on polling vs WebSockets, cursor pagination, tool metadata storage, soft deletes. Stateless architecture enforced at every layer (no in-memory state, full DB fetches). Strong tenant isolation patterns documented. Three-layer separation (Chatkit UI → REST API → Agent runtime) maintains Phase II/III boundaries.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning completed successfully with all deliverables.
- Graders run and results (PASS/FAIL): PASS - Constitutional gates all passed (6/6). Research resolved all technical unknowns. Data model supports stateless architecture. API contracts enforce tenant isolation.
- Prompt variant (if applicable): Standard /sp.plan workflow as defined in plan template
- Next experiment (smallest change to try): Consider adding caching layer for conversation history (after validating stateless requirement in practice). May reduce database load for high-frequency conversations but must maintain constitutional compliance (cache invalidation strategy required).
