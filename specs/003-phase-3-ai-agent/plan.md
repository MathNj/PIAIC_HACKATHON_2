# Implementation Plan: AI Chat Agent with MCP Integration

**Branch**: `003-phase-3-ai-agent` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-phase-3-ai-agent/spec.md`

## Summary

Implement Phase III AI Chat Agent that enables users to manage TODO tasks through natural language conversation. The agent uses OpenAI Agents SDK with Model Context Protocol (MCP) tools to interact with the existing Phase II Task API. All conversation history is persisted in PostgreSQL (`conversations` and `messages` tables), ensuring the agent remains completely stateless per constitution requirements.

**Core Technical Approach**:
- Stateless AI agent with database-backed conversation history
- MCP tools as exclusive interface between agent and backend (7 tools total)
- OpenAI ChatKit for frontend chat UI
- JWT authentication propagated to all MCP tools for multi-user isolation
- Natural language processing for temporal expressions and priority inference

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**: OpenAI Agents SDK (`openai>=1.0.0`), MCP Python SDK (`mcp>=0.1.0`), OpenAI ChatKit (`@openai/chatkit-react`)
**Storage**: PostgreSQL (Neon) with 2 new tables (conversations, messages), Phase II tables unchanged
**Testing**: pytest (backend unit/integration), Jest + React Testing Library (frontend), mock LLM responses
**Target Platform**: Web application (Vercel deployment for both backend and frontend)
**Project Type**: Web (backend + frontend)
**Performance Goals**: <5s agent response (simple queries), <10s (multi-tool operations), <500ms DB queries
**Constraints**: Stateless agent (no in-memory state), JWT validation in all MCP tools, multi-user isolation, Phase II backward compatibility
**Scale/Scope**: Support 100+ concurrent users, 1000+ conversations, 10k+ messages, 7 MCP tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase III Governance Requirements

**✅ PASS: Architecture Pattern**
- ✅ Stateless AI Agent implemented (database-backed conversation history)
- ✅ Model Context Protocol (MCP) used for all task operations
- ✅ OpenAI Agents SDK + Official MCP Python SDK + OpenAI ChatKit (approved stack)
- ✅ Agent layer sits above Phase II backend (no direct database access)

**✅ PASS: State Management (CRITICAL CONSTRAINT)**
- ✅ NO in-memory conversation state in agent runtime
- ✅ ALL messages stored in `conversations` and `messages` tables
- ✅ Conversation history fetched from database on every request
- ✅ Conversation state saved to database before request completion
- ✅ Agent runtime can restart without losing context
- ✅ Multiple agent instances can serve same user (load balancing compatible)

**✅ PASS: MCP Compliance (NON-NEGOTIABLE)**
- ✅ ALL Task operations implemented as strict MCP Tools
- ✅ 7 required tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`, `get_task_summary`, `suggest_task_prioritization`
- ✅ Agent CANNOT access backend directly (only via MCP tools)
- ✅ Tools return structured strings/JSON (LLM-interpretable)
- ✅ Each tool validates JWT token independently

**✅ PASS: Security Constraints (CRITICAL)**
- ✅ Agent extracts user_id from JWT token on every request
- ✅ All MCP tools validate token-derived user_id
- ✅ Failed user_id validation returns 403 Forbidden
- ✅ Database queries filter by user_id (multi-user isolation)
- ✅ No tool can access data belonging to different users

**✅ PASS: Natural Language Processing**
- ✅ Agent extracts task title, priority, due_date from natural language
- ✅ Temporal expressions parsed ("tomorrow", "next week", ISO dates)
- ✅ Priority inference from urgency keywords ("urgent" → high, "maybe" → low)
- ✅ Hybrid approach: rule-based parsing + LLM understanding

**✅ PASS: Frontend Integration**
- ✅ OpenAI ChatKit React component for chat UI
- ✅ JWT token included in all API requests
- ✅ Tool call results displayed to user
- ✅ Conversation list and history accessible

**✅ PASS: Code Quality Standards**
- ✅ Strict type hints for all MCP tools (Python typing)
- ✅ Comprehensive docstrings (LLM-readable format)
- ✅ Error handling returns user-friendly messages (never raises exceptions)
- ✅ Unit tests for all 7 MCP tools
- ✅ Integration tests for conversation flow
- ✅ Mock LLM responses for deterministic testing

**✅ PASS: Database Schema Requirements**
- ✅ `conversations` table: id, user_id (FK), title, created_at, updated_at
- ✅ `messages` table: id, conversation_id (FK), role, content, tool_calls, created_at
- ✅ Indexes on user_id, conversation_id, (conversation_id, created_at)
- ✅ Cascade deletes maintain referential integrity

**✅ PASS: File Structure Requirements**
- ✅ `backend/mcp/` for MCP tool definitions
- ✅ `backend/mcp/server.py` for MCP server initialization
- ✅ `backend/mcp/tools.py` for tool implementations
- ✅ `backend/agents/` for agent orchestration logic
- ✅ `backend/app/models/conversation.py` and `message.py` for SQLModels
- ✅ `frontend/app/agent/page.tsx` for ChatKit UI

### Phase Transition Compliance

**✅ PASS: Phase II Complete**
- Phase II features fully implemented (Task CRUD API, Authentication, Frontend UI)
- No Phase II features require completion before Phase III

**✅ PASS: Technology Stack Governance**
- Only Phase III approved technologies: OpenAI Agents SDK, MCP Python SDK, OpenAI ChatKit
- No future-phase technologies introduced (Kubernetes, Kafka, Dapr reserved for Phase IV/V)

**✅ PASS: Backward Compatibility**
- Phase II Task API unchanged (no breaking changes)
- Phase II Authentication system reused (JWT validation)
- Phase II Frontend UI unchanged (agent UI added as `/agent` route)
- Phase II Database schema preserved (only additive changes: conversations, messages tables)

### Violations (None)

No constitution violations detected. All Phase III governance requirements satisfied.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-phase-3-ai-agent/
├── plan.md              # This file (/sp.plan output)
├── spec.md              # Feature specification (completed)
├── mcp-tools-spec.md    # MCP tools detailed specification (completed)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (API contracts)
│   └── chat-api.openapi.yaml  # OpenAPI 3.1 specification for chat endpoints
└── tasks.md             # Phase 2 output (/sp.tasks - NOT YET CREATED)
```

### Source Code (repository root)

```text
backend/
├── mcp/                     # NEW: MCP server and tools
│   ├── __init__.py
│   ├── server.py            # MCP server initialization, tool registration
│   └── tools.py             # 7 MCP tool implementations
├── agents/                  # NEW: Agent orchestration
│   ├── __init__.py
│   └── chat_agent.py        # OpenAI agent execution with MCP tools
├── app/
│   ├── models/
│   │   ├── conversation.py  # NEW: Conversation SQLModel
│   │   ├── message.py       # NEW: Message SQLModel
│   │   ├── task.py          # EXISTING (no changes)
│   │   └── user.py          # EXISTING (no changes)
│   ├── routers/
│   │   ├── chat.py          # NEW: Chat API endpoints
│   │   ├── conversations.py # NEW: Conversation management endpoints
│   │   └── tasks.py         # EXISTING (no changes)
│   ├── auth/
│   │   └── dependencies.py  # EXISTING (reused for JWT validation)
│   └── database.py          # EXISTING (session management reused)
├── alembic/
│   └── versions/
│       └── {hash}_add_conversation_tables.py  # NEW: Database migration
└── tests/
    ├── test_mcp_tools.py            # NEW: Unit tests for MCP tools
    ├── test_chat_agent.py           # NEW: Unit tests for agent orchestration
    ├── test_chat_api.py             # NEW: Integration tests for chat API
    └── integration/
        └── test_conversation_flow.py  # NEW: End-to-end conversation tests

frontend/
├── app/
│   ├── agent/
│   │   └── page.tsx         # NEW: AI Chat Agent page (ChatKit UI)
│   ├── conversations/
│   │   └── page.tsx         # NEW: Conversation history page
│   └── layout.tsx           # MODIFIED: Add agent navigation link
├── lib/
│   ├── chat-api.ts          # NEW: Chat API client functions
│   └── auth-context.tsx     # EXISTING (reused for JWT token)
└── components/
    └── chat/
        └── ConversationSidebar.tsx  # NEW: Conversation list component
```

**Structure Decision**:
Web application structure selected based on existing Phase II layout. Backend adds new `mcp/` and `agents/` modules without modifying Phase II code. Frontend adds new `/agent` and `/conversations` routes without breaking existing UI. All new code follows Phase II patterns (SQLModel, FastAPI routers, Next.js App Router).

---

## Complexity Tracking

**No violations requiring justification.** Constitution Check passed without complexity concerns.

---

## Phase 0: Research & Technology Decisions

**Status**: ✅ Completed

**Output**: [research.md](./research.md) - 10 technology decisions documented with rationales

**Key Decisions**:
1. **AI Agent Framework**: OpenAI Agents SDK (official SDK, native tool calling, stateless model)
2. **MCP SDK**: Official MCP Python SDK (protocol-based, type-safe, auto schema generation)
3. **Frontend Chat UI**: OpenAI ChatKit (production-ready, OpenAI-optimized, Tailwind styling)
4. **Database Schema**: PostgreSQL with conversations/messages tables (relational integrity, indexes)
5. **Authentication**: JWT token propagation to MCP tools (Phase II compatibility, multi-user isolation)
6. **NLP Strategy**: Hybrid rule-based + LLM extraction (reliable temporal parsing, intelligent priority inference)
7. **Error Handling**: Structured error strings from tools (never exceptions, LLM-parseable)
8. **Performance**: 20-message history limit (cost optimization, adequate context)
9. **Testing**: Mock LLM responses (deterministic, fast, CI/CD compatible)
10. **Deployment**: Environment variable API key storage (security, rotation-friendly)

**All NEEDS CLARIFICATION Resolved**: Technical context fully defined, no unknowns remaining.

---

## Phase 1: Design & Contracts

**Status**: ✅ Completed

**Outputs**:
1. [data-model.md](./data-model.md) - Complete database schema with ERD, indexes, validation
2. [contracts/chat-api.openapi.yaml](./contracts/chat-api.openapi.yaml) - OpenAPI 3.1 specification for 4 endpoints
3. [quickstart.md](./quickstart.md) - Step-by-step setup guide with troubleshooting

### Data Model Summary

**New Entities**:
- **Conversation**: Parent container for messages (id, user_id FK, title, created_at, updated_at)
- **Message**: Individual conversation messages (id, conversation_id FK, role enum, content, tool_calls JSON, created_at)

**Relationships**:
- Conversation → User (Many-to-One, CASCADE delete)
- Message → Conversation (Many-to-One, CASCADE delete)
- Implicit: Message → User (via conversation)

**Indexes** (for performance):
- `idx_conversations_user_id` - List user's conversations
- `idx_conversations_updated_at` - Recent conversations first
- `idx_messages_conversation_id` - All messages in conversation
- `idx_messages_conversation_created` - **Composite index** for ordered retrieval (most efficient query pattern)

**Validation**:
- Database-level: CHECK constraints (role enum, content length, timestamps)
- Application-level: SQLModel validators (title length, JSON format, updated_at >= created_at)

### API Contracts Summary

**Endpoints** (4 total):
1. `POST /api/{user_id}/chat` - Send message to agent (creates/continues conversation)
2. `GET /api/{user_id}/conversations` - List user's conversations (pagination support)
3. `GET /api/{user_id}/conversations/{id}/messages` - Get conversation history
4. `DELETE /api/{user_id}/conversations/{id}` - Delete conversation (cascade to messages)

**Authentication**: All endpoints require JWT Bearer token, user_id must match token

**Error Codes**: 400 (validation), 401 (auth), 403 (forbidden), 404 (not found), 500 (server error)

---

## Phase 2: Implementation Tasks

**Status**: ⏭️ Next Step - Run `/sp.tasks` to generate actionable task list

**Scope**: Implementation will be broken into 6 phases:

### Phase 2.1: Database Models & Migrations
- Create `Conversation` and `Message` SQLModel classes
- Generate Alembic migration with indexes and constraints
- Apply migration to development database
- Verify cascading deletes work correctly

### Phase 2.2: MCP Tools Implementation
- Implement 7 MCP tools in `backend/mcp/tools.py`:
  1. `add_task` - Create task with NLP extraction
  2. `list_tasks` - Retrieve tasks with filtering
  3. `complete_task` - Toggle task completion
  4. `delete_task` - Remove task
  5. `update_task` - Partial task updates
  6. `get_task_summary` - Task analytics
  7. `suggest_task_prioritization` - AI-powered ordering
- Add JWT validation to each tool
- Write unit tests for each tool (mock database)
- Register tools with MCP server

### Phase 2.3: Agent Orchestration
- Create `backend/agents/chat_agent.py` with `execute_agent()` function
- Implement conversation history loading from database
- Integrate OpenAI Agents SDK with MCP tools
- Handle tool call execution and result logging
- Test agent with mock conversations

### Phase 2.4: Chat API Endpoints
- Implement `POST /api/{user_id}/chat` endpoint
- Add conversation creation/retrieval logic
- Save user message before agent execution
- Save assistant response and tool_calls after execution
- Update conversation.updated_at timestamp
- Write integration tests for chat flow

### Phase 2.5: Conversation Management API
- Implement `GET /api/{user_id}/conversations` with pagination
- Implement `GET /api/{user_id}/conversations/{id}/messages` with pagination
- Implement `DELETE /api/{user_id}/conversations/{id}` with cascade
- Add query optimization (use composite indexes)
- Write API tests

### Phase 2.6: Frontend Integration
- Install `@openai/chatkit-react` package
- Create `frontend/app/agent/page.tsx` with ChatInterface component
- Create `frontend/app/conversations/page.tsx` for conversation list
- Create `frontend/lib/chat-api.ts` with API client functions
- Add JWT token to all requests
- Style consistently with Phase II design (Tailwind CSS)
- Write end-to-end tests for chat UI

---

## Architecture Decision Records (ADRs)

**Recommended ADRs** for significant architectural decisions:

### ADR-001: Stateless Agent with Database-Backed Conversation History

**Context**: Need to ensure agent can scale horizontally and handle failures

**Decision**: Implement fully stateless agent that fetches all conversation history from database on every request

**Consequences**:
- ✅ Horizontal scaling without sticky sessions
- ✅ Fault tolerance (agent restart doesn't lose context)
- ✅ Conversation history becomes valuable data asset
- ⚠️ Database query on every request (mitigated by indexes and 20-message limit)
- ⚠️ Slightly higher latency (mitigated by composite index optimization)

### ADR-002: Model Context Protocol for Task Operations

**Context**: Need standardized interface between AI agent and backend

**Decision**: Use MCP as exclusive protocol for all task operations (no direct database access)

**Consequences**:
- ✅ Clean separation between AI layer and business logic
- ✅ Type-safe tool definitions with auto schema generation
- ✅ Testable in isolation (mock MCP tools for agent tests)
- ✅ Future-proof (protocol-level abstraction)
- ⚠️ Additional abstraction layer (acceptable trade-off for maintainability)

### ADR-003: JWT Token Propagation to MCP Tools

**Context**: Need to enforce multi-user isolation at tool layer

**Decision**: Pass JWT token from chat API to every MCP tool; each tool validates independently

**Consequences**:
- ✅ Defense in depth (multi-user isolation enforced at multiple layers)
- ✅ Tool calls auditable with user context
- ✅ Cannot bypass isolation even if agent misbehaves
- ⚠️ Token validation overhead (negligible, <10ms per call)

---

## Testing Strategy

### Unit Tests (Backend)

**MCP Tools** (`tests/test_mcp_tools.py`):
- Test each of 7 tools with valid inputs
- Test JWT validation failure scenarios
- Test multi-user isolation (user A cannot access user B's tasks)
- Test error handling (invalid inputs, database failures)
- Mock database with pytest fixtures

**Agent Orchestration** (`tests/test_chat_agent.py`):
- Mock OpenAI API responses
- Test tool call execution
- Test conversation history formatting
- Test error recovery

### Integration Tests (Backend)

**Chat API** (`tests/test_chat_api.py`):
- Test full conversation creation flow
- Test conversation continuation
- Test multi-tool agent execution
- Test conversation persistence
- Use real database (test fixtures)

**End-to-End** (`tests/integration/test_conversation_flow.py`):
- Simulate user conversation with multiple messages
- Verify conversation history persists
- Verify tool calls logged correctly
- Test conversation deletion cascade

### Frontend Tests

**Component Tests**:
- ChatInterface renders correctly
- Conversation list displays conversations
- Message bubbles styled by role
- Tool call display component

**Integration Tests**:
- Full chat flow (user sends message → agent responds)
- Conversation selection and resumption
- Error handling (API failures, network errors)

---

## Performance Optimization

### Database Query Optimization

**Composite Index**: `idx_messages_conversation_created (conversation_id, created_at)`
- Covers WHERE and ORDER BY clauses
- Eliminates full table scan
- Estimated query time: <10ms for 1000 messages, <100ms for 100k messages

**History Limit**: Load last 20 messages by default
- Reduces LLM token usage (cost optimization)
- Adequate context for most conversations
- Pagination available for "remind me" queries

### Agent Response Time

**Target**: <5 seconds for simple queries, <10 seconds for multi-tool operations

**Optimizations**:
- Parallel tool calls where possible (not implemented in Phase III, future enhancement)
- Cached tool schemas (MCP server caches tool definitions)
- Database connection pooling (Phase II existing configuration)

### Cost Optimization

**OpenAI API Cost**: Estimated $0.01-0.05 per conversation
- 20-message history limit reduces token usage
- Tool calls use structured outputs (efficient encoding)
- Monitoring via tool_calls logging

---

## Security Considerations

### Multi-User Isolation (Defense in Depth)

**Layer 1**: API endpoint validates JWT and user_id match
**Layer 2**: Database queries filter by user_id
**Layer 3**: MCP tools re-validate JWT and extract user_id independently

**Query Pattern** (safe):
```sql
SELECT * FROM messages m
INNER JOIN conversations c ON m.conversation_id = c.id
WHERE c.user_id = :authenticated_user_id;
```

### PII and Data Sensitivity

**Personal Information in Conversations**:
- messages.content may contain PII (task details, names, dates)
- tool_calls may log sensitive task information
- conversations.title auto-generated from first message (may contain PII)

**Protection Measures**:
- Database encryption at rest (Neon default)
- TLS for all database connections
- Never log message content in application logs
- Mask user_id in error messages
- Conversation export requires authentication

### API Key Security

- OpenAI API key stored in environment variable (never in code/database)
- `.env.local` in `.gitignore` (never committed)
- Vercel deployment uses environment variable secrets
- Key rotation possible without code changes

---

## Deployment Strategy

### Development Environment

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev  # Port 3000
```

### Production Deployment (Vercel)

**Backend**:
1. Set environment variables: `OPENAI_API_KEY`, `DATABASE_URL`, `BETTER_AUTH_SECRET`
2. Run database migration: `alembic upgrade head`
3. Deploy: `vercel --prod`

**Frontend**:
1. Set environment variable: `NEXT_PUBLIC_API_URL`
2. Deploy: `vercel --prod`

**Database Migration**:
- Run Alembic migration on production database before deploying backend
- Test migration on staging environment first (recommended)

---

## Monitoring and Observability

### Logging

**Agent Execution**:
- Log conversation_id, user_id, message count on each request
- Log tool calls with tool name and execution time
- Never log message content or JWT tokens

**Error Logging**:
- Log OpenAI API errors with context (user_id, conversation_id)
- Log database query errors
- Log authentication failures (user_id mismatch)

### Metrics

**Performance Metrics**:
- Agent response time (p50, p95, p99)
- Database query time for conversation history
- MCP tool execution time per tool

**Business Metrics**:
- Conversations created per day
- Messages sent per conversation
- Tool calls by type (which tools used most)
- User engagement (conversations per user)

### Alerting

**Critical Alerts**:
- OpenAI API failures (> 5% error rate)
- Database connection failures
- Authentication bypass attempts (user_id mismatch)

**Warning Alerts**:
- Slow agent responses (> 10s)
- High OpenAI API cost (> $100/day)
- Database query performance degradation

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OpenAI API cost escalation | Medium | High | 20-message history limit, rate limiting, cost monitoring alerts |
| LLM hallucinations (wrong task data) | Medium | Medium | Validate all tool inputs, confirmation UI for destructive actions |
| JWT token leakage to LLM logs | Low | Critical | Never log tokens, mask in error messages, OpenAI doesn't log tool args |
| Database performance (large conversations) | Low | Medium | Composite indexes, pagination, conversation archival (future) |
| MCP tool failures crashing agent | Low | Medium | Structured error returns (never raise exceptions), error recovery |
| Cross-user data access via agent | Very Low | Critical | Multi-layer isolation (API + DB + Tools), audit trail, testing |

---

## Success Criteria

**Functional** (from Acceptance Criteria in spec.md):
- ✅ Conversation and Message database tables created with proper relationships
- ✅ Users can start new conversation or continue existing conversation
- ✅ All conversation history persisted in database (no in-memory state)
- ✅ Agent can create tasks using natural language via MCP tools
- ✅ Agent can list, update, and delete tasks via MCP tools
- ✅ Agent correctly infers task priority from urgency keywords
- ✅ Agent correctly parses temporal expressions
- ✅ Agent provides task prioritization suggestions
- ✅ All MCP tools validate JWT and enforce user_id isolation
- ✅ Agent responses saved to database before returning to user
- ✅ API supports both new and continued conversations
- ✅ Tool calls logged in messages.tool_calls for auditability
- ✅ Agent handles tool failures gracefully
- ✅ Conversation history loaded from database on every request (stateless)
- ✅ Frontend ChatKit UI integrated

**Performance**:
- Agent response time < 5s for simple queries (measured)
- Agent response time < 10s for multi-tool operations (measured)
- Database query time < 500ms for conversation loading (measured)
- API cost per conversation < $0.10 (monitored)

**Security**:
- Zero cross-user data access incidents (tested)
- All MCP tools validate JWT on every call (100% coverage)
- Tool call audit trail complete (tested)
- No PII or tokens leaked in logs (audited)

**Code Quality**:
- Unit test coverage > 90% for MCP tools (measured)
- Integration test coverage for all API endpoints (measured)
- End-to-end test for full conversation flow (tested)
- All code passes linting and type checking (CI/CD enforced)

---

## Out of Scope (Phase III)

- Multi-user collaborative conversations (single-user conversations only)
- Real-time streaming responses (future enhancement)
- Voice input/output (future enhancement)
- Conversation sharing or export (future enhancement)
- Agent training or fine-tuning (use base OpenAI models)
- Custom agent personalities or system prompts (future enhancement)
- Conversation branching or forking (linear conversation only)
- Batch task operations (create multiple tasks at once)
- Advanced search or filtering beyond status (future enhancement)

---

## Next Steps

1. **Run `/sp.tasks`** to generate actionable task list from this plan
2. **Allocate tasks to implementation batches** (6 phases defined above)
3. **Begin Phase 2.1**: Database models and migrations
4. **Iterate through phases 2.2-2.6**: Incremental delivery
5. **Create ADRs** for the 3 significant architectural decisions documented above
6. **Deploy to staging** for testing before production release

---

## References

- **Spec**: [specs/003-phase-3-ai-agent/spec.md](./spec.md)
- **MCP Tools Spec**: [specs/003-phase-3-ai-agent/mcp-tools-spec.md](./mcp-tools-spec.md)
- **Research**: [specs/003-phase-3-ai-agent/research.md](./research.md)
- **Data Model**: [specs/003-phase-3-ai-agent/data-model.md](./data-model.md)
- **API Contract**: [specs/003-phase-3-ai-agent/contracts/chat-api.openapi.yaml](./contracts/chat-api.openapi.yaml)
- **Quickstart**: [specs/003-phase-3-ai-agent/quickstart.md](./quickstart.md)
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- **MCP Tool Maker Skill**: [.claude/skills/mcp-tool-maker/SKILL.md](../../.claude/skills/mcp-tool-maker/SKILL.md)
- **Phase II Task Model**: [backend/app/models/task.py](../../backend/app/models/task.py)
- **Phase II Authentication**: [backend/app/auth/dependencies.py](../../backend/app/auth/dependencies.py)

---

**Plan Status**: ✅ Complete - Ready for `/sp.tasks` command to generate actionable task list
