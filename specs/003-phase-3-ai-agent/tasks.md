# Tasks: AI Chat Agent with MCP Integration

**Feature**: AI Chat Agent with MCP Integration
**Branch**: 003-phase-3-ai-agent (to be created)
**Date**: 2025-12-07
**Status**: Ready for Implementation

## Overview

This task list implements Phase III AI Chat Agent that enables users to manage TODO tasks through natural language conversation. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 54 tasks
**Parallel Opportunities**: 18 parallelizable tasks
**Estimated MVP**: User Stories 1-3 (Chat + Conversation Persistence + Task Creation)

---

## Task Summary by User Story

| User Story | Tasks | Focus |
|------------|-------|-------|
| Setup (Phase 1) | 5 | Environment, dependencies, project structure |
| Foundational (Phase 2) | 8 | Database models, MCP infrastructure, agent core |
| US-1: Basic Chat | 6 | Chat API endpoint, conversation management |
| US-2: Conversation Persistence | 4 | History loading, state management |
| US-3: Task Creation via NLP | 5 | MCP tools (add_task), natural language extraction |
| US-4: Temporal Expressions | 3 | Due date parsing ("tomorrow", "next week") |
| US-5: Priority Inference | 3 | Priority extraction from urgency keywords |
| US-6: Task Prioritization | 4 | MCP tools (list_tasks, suggest_prioritization) |
| US-7: Security & Isolation | 6 | JWT validation, multi-user isolation |
| Frontend Integration | 7 | ChatKit UI, conversation list, navigation |
| Polish & Testing | 3 | Integration tests, documentation |

---

## Dependencies and Execution Order

### Critical Path (Sequential)

```
Phase 1: Setup
  ↓
Phase 2: Foundational (Database + MCP Infrastructure)
  ↓
User Stories 1-7 (Can be implemented in parallel after foundational phase)
  ↓
Frontend Integration (Depends on US-1, US-2, US-3)
  ↓
Polish & Testing
```

### User Story Dependencies

- **US-1** (Basic Chat): Requires Foundational phase complete
- **US-2** (Persistence): Requires US-1 chat endpoint
- **US-3** (Task Creation): Requires US-1, can be parallel with US-4, US-5
- **US-4** (Temporal): Can be parallel with US-3, US-5
- **US-5** (Priority): Can be parallel with US-3, US-4
- **US-6** (Prioritization): Requires US-3 complete
- **US-7** (Security): Cross-cutting, implemented throughout
- **Frontend**: Requires US-1, US-2, US-3

### Parallel Execution Opportunities

**After Foundational Phase Complete**:
- US-3 (Task Creation) + US-4 (Temporal) + US-5 (Priority) can run in parallel
- Frontend components can be built in parallel with backend US-4, US-5, US-6

---

## Phase 1: Setup (5 tasks)

**Goal**: Prepare development environment and install dependencies

**Independent Test Criteria**:
- ✅ Backend dependencies installed (verify with `pip list`)
- ✅ Frontend dependencies installed (verify with `npm list`)
- ✅ Environment variables configured (verify with `echo $OPENAI_API_KEY`)
- ✅ MCP and agents directories created

### Tasks

- [ ] T001 Create feature branch `003-phase-3-ai-agent` from main
- [ ] T002 [P] Install backend dependencies: `openai>=1.0.0`, `mcp>=0.1.0`, `python-dateutil>=2.8.2` in `backend/requirements.txt`
- [ ] T003 [P] Install frontend dependencies: `@openai/chatkit-react@latest` in `frontend/package.json`
- [ ] T004 Configure environment variables: Add `OPENAI_API_KEY` to `backend/.env.local`
- [ ] T005 [P] Create directory structure: `backend/mcp/`, `backend/agents/`, `frontend/app/agent/`, `frontend/lib/chat-api.ts`

---

## Phase 2: Foundational (8 tasks)

**Goal**: Implement core database schema and MCP infrastructure that ALL user stories depend on

**Independent Test Criteria**:
- ✅ Database migration applied (verify tables exist: `psql -c "\dt conversations messages"`)
- ✅ MCP server initializes (verify with `python -c "from mcp.server import get_mcp_server; print(len(get_mcp_server().list_tools()))"`)
- ✅ Agent can execute with empty conversation (unit test)

### Tasks

#### Database Models (T006-T008)

- [X] T006 Create `Conversation` SQLModel in `backend/app/models/conversation.py` with fields: id, user_id (FK), title, created_at, updated_at
- [X] T007 Create `Message` SQLModel in `backend/app/models/message.py` with fields: id, conversation_id (FK), role (enum: user/assistant/system), content, tool_calls (JSON), created_at
- [X] T008 Generate Alembic migration: `alembic revision --autogenerate -m "Add conversation and message tables"` and verify indexes: idx_conversations_user_id, idx_conversations_updated_at, idx_messages_conversation_id, idx_messages_conversation_created

#### MCP Infrastructure (T009-T011)

- [X] T009 Create MCP server initialization in `backend/mcp/server.py` with `MCPServer(name="todo-mcp-server")` and `get_mcp_server()` function
- [X] T010 [P] Create `backend/mcp/__init__.py` empty file for module import
- [X] T011 Create `backend/mcp/tools.py` skeleton with 5 MCP tools (list_tasks, create_task, update_task, delete_task, toggle_task_completion) fully implemented

#### Agent Core (T012-T013)

- [X] T012 Create `backend/agents/__init__.py` empty file for module import
- [X] T013 Create `backend/agents/chat_agent.py` with `execute_agent(conversation_history, user_token)` function stub (returns mock response, to be integrated with OpenAI Agent SDK in US-1)

---

## Phase 3: User Story 1 - Basic Chat (6 tasks)

**User Story**: As a user, I want to chat with an AI agent to manage my tasks, so that I can use natural language instead of manual forms

**Goal**: Implement POST /api/{user_id}/chat endpoint that accepts messages and returns agent responses

**Independent Test Criteria**:
- ✅ POST /api/{user_id}/chat with valid JWT returns 200 with conversation_id and message
- ✅ Invalid JWT returns 401
- ✅ User_id mismatch returns 403
- ✅ Conversation is created in database with first message

### Tasks

- [X] T014 [US1] Create `ChatRequest` and `ChatResponse` Pydantic schemas in `backend/app/routers/chat.py`
- [X] T015 [US1] Implement `POST /api/{user_id}/chat` endpoint in `backend/app/routers/chat.py` with JWT authentication via `get_current_user` dependency
- [X] T016 [US1] Implement conversation creation logic: If conversation_id is null, create new Conversation record
- [X] T017 [US1] Implement conversation retrieval logic: If conversation_id provided, verify it belongs to user (403 if not)
- [X] T018 [US1] Integrate `run_chat_turn()` call in chat endpoint with conversation history loaded from database
- [X] T019 [US1] Register chat router in `backend/app/main.py`: `app.include_router(chat_router)`

---

## Phase 4: User Story 2 - Conversation Persistence (4 tasks)

**User Story**: As a user, I want my conversation history to persist, so that I can resume conversations across sessions

**Goal**: Load conversation history from database before agent execution, save messages after execution

**Independent Test Criteria**:
- ✅ User message saved to database before agent execution
- ✅ Assistant response saved to database after agent execution
- ✅ Conversation history (last 20 messages) loaded from database on every request
- ✅ Conversation.updated_at timestamp updated on each message

### Tasks

- [X] T020 [US2] Implement `load_conversation_history(conversation_id, limit=20)` function in `backend/app/routers/chat.py` that queries messages ordered by created_at DESC
- [X] T021 [US2] Implement `save_message(conversation_id, role, content, tool_calls=None)` function in `backend/app/routers/chat.py` that creates Message record
- [X] T022 [US2] Update chat endpoint: Save user message before agent execution using `save_message()`
- [X] T023 [US2] Update chat endpoint: Save assistant response after agent execution, update conversation.updated_at timestamp

---

## Phase 5: User Story 3 - Task Creation via NLP (5 tasks)

**User Story**: As a user, I want the agent to create tasks from my natural language descriptions, so that I don't have to fill out structured forms

**Goal**: Implement MCP tools for task operations, integrate with agent

**Independent Test Criteria**:
- ✅ Agent can call `add_task` MCP tool with title
- ✅ Task is created in database with correct user_id
- ✅ Tool call logged in messages.tool_calls JSON field
- ✅ Agent responds with confirmation message

### Tasks

- [X] T024 [P] [US3] Implement `add_task(user_token, title, description, priority, due_date)` MCP tool in `backend/mcp/tools.py` with @mcp.tool() decorator, JWT validation via verify_token(), and structured error handling
- [X] T025 [P] [US3] Implement `update_task(user_token, task_id, title, description, priority, due_date)` MCP tool in `backend/mcp/tools.py` with partial update support (only update provided fields)
- [X] T026 [P] [US3] Implement `delete_task(user_token, task_id)` MCP tool in `backend/mcp/tools.py` with user ownership validation
- [X] T027 [US3] Integrate MCP tools with agent in `backend/agent_runner/runner.py`: Get tool list from tool wrappers, pass to OpenAI agent completion (Gemini API)
- [X] T028 [US3] Implement tool call execution loop in `backend/agent_runner/runner.py`: Execute tools, collect results, log to tool_calls array, return with agent response

---

## Phase 6: User Story 4 - Temporal Expressions (3 tasks)

**User Story**: As a user, I want the agent to understand temporal expressions ("tomorrow", "next week"), so that I can set due dates naturally

**Goal**: Parse natural language due dates and pass to add_task tool

**Independent Test Criteria**:
- ✅ "tomorrow" parsed to next calendar day (ISO format)
- ✅ "next week" parsed to 7 days from now
- ✅ ISO format dates (YYYY-MM-DD) accepted directly
- ✅ Invalid dates handled gracefully (return None or error)

### Tasks

- [X] T029 [P] [US4] Implement `parse_due_date(natural_language)` helper function in `backend/mcp/tools.py` using python-dateutil parser with fuzzy=True
- [X] T030 [US4] Add temporal expression handling to `add_task` tool: Call `parse_due_date()` if due_date contains non-ISO characters
- [X] T031 [US4] Update system prompt in `backend/agent_runner/runner.py` to include temporal expression examples (tomorrow, next week, Monday) with multi-language support (Urdu, Arabic)

---

## Phase 7: User Story 5 - Priority Inference (3 tasks)

**User Story**: As a user, I want the agent to infer task priority from my language, so that urgent tasks are automatically marked as high priority

**Goal**: Extract priority from urgency keywords in natural language

**Independent Test Criteria**:
- ✅ Keywords "urgent", "asap", "critical" → priority="high"
- ✅ Keywords "maybe", "sometime", "eventually" → priority="low"
- ✅ Default priority="normal" if no keywords
- ✅ Agent correctly sets priority when creating tasks

### Tasks

- [X] T032 [P] [US5] Implement `infer_priority(description)` helper function in `backend/mcp/tools.py` that scans for urgency keywords
- [X] T033 [US5] Update `add_task` tool to call `infer_priority()` if priority not explicitly provided
- [X] T034 [US5] Update system prompt in `backend/agent_runner/runner.py` to include priority inference examples (urgent, asap, critical) with multi-language keywords (Urdu: فوری, Arabic: عاجل)

---

## Phase 8: User Story 6 - Task Prioritization (4 tasks)

**User Story**: As a user, I want the agent to help me prioritize my task list, so that I can focus on the most important items

**Goal**: Implement MCP tools for listing tasks and suggesting prioritization

**Independent Test Criteria**:
- ✅ `list_tasks` returns all user's tasks with filtering by status (all, pending, completed)
- ✅ `suggest_task_prioritization` returns tasks ordered by score (due date urgency + priority weight)
- ✅ Overdue tasks scored highest
- ✅ Agent can recommend which task to work on next

### Tasks

- [X] T035 [P] [US6] Implement `list_tasks(user_token, status="all", sort="created")` MCP tool in `backend/mcp/tools.py` with filtering and sorting support
- [X] T036 [P] [US6] Implement `toggle_task_completion(user_token, task_id)` MCP tool in `backend/mcp/tools.py` that toggles task.completed status
- [X] T037 [P] [US6] Implement `get_task_summary(user_token, timeframe="all")` MCP tool in `backend/mcp/tools.py` that returns counts and statistics
- [X] T038 [US6] Implement `suggest_task_prioritization(user_token)` MCP tool in `backend/mcp/tools.py` that scores tasks (priority weight + due date urgency) and returns ordered list with reasoning

---

## Phase 9: User Story 7 - Security & Isolation (6 tasks)

**User Story**: As a user, I want the agent to only access my own tasks, so that my data remains private and secure

**Goal**: Enforce JWT validation and multi-user isolation in all MCP tools and API endpoints

**Independent Test Criteria**:
- ✅ All 7 MCP tools validate JWT token before any operation
- ✅ Invalid JWT returns structured error string (not exception)
- ✅ MCP tools query tasks filtered by user_id from JWT
- ✅ Cross-user access attempt returns 403 or "Task not found" error
- ✅ Tool calls logged with user_id for audit trail

### Tasks

- [X] T039 [US7] Add JWT validation to all 7 MCP tools: Extract user_id via `validate_jwt_token(user_token)` at start of each function
- [X] T040 [US7] Add multi-user isolation to `list_tasks`: Filter query by `WHERE user_id = :user_id`
- [X] T041 [US7] Add multi-user isolation to `toggle_task_completion`, `delete_task`, `update_task`: Query with `WHERE task_id = :task_id AND user_id = :user_id`
- [X] T042 [US7] Add error handling to all MCP tools: Catch MCPToolError (auth errors) and return structured error responses
- [X] T043 [US7] Update chat endpoint to verify path user_id matches JWT user_id (raise HTTPException 403 if mismatch)
- [X] T044 [US7] Verify tool calls logged in messages.tool_calls with user_id context (implemented in agent runner)

---

## Phase 10: Frontend Integration (7 tasks)

**Goal**: Build ChatKit UI for agent interaction and conversation management

**Independent Test Criteria**:
- ✅ Chat interface renders at `/agent` route
- ✅ User can send message and receive agent response
- ✅ Conversation list displays at `/conversations` route
- ✅ User can resume existing conversation
- ✅ Tool calls displayed in message (optional visual component)
- ✅ JWT token included in all API requests

### Tasks

- [X] T045 [P] Create `frontend/app/agent/page.tsx` with ChatInterface component from `@openai/chatkit-react` - ✅ Implemented as frontend/app/chat/page.tsx with custom React chat UI (Vercel AI SDK not needed, using api.post directly)
- [X] T046 [P] Create `frontend/lib/chat-api.ts` with `sendMessage(userId, conversationId, message, token)` API client function - ✅ Integrated directly into chat page component using existing lib/api.ts
- [ ] T047 [P] Create `frontend/app/conversations/page.tsx` with conversation list component
- [ ] T048 [P] Create `frontend/lib/conversations-api.ts` with `listConversations(userId, token)` and `getConversationMessages(userId, conversationId, token)` functions
- [X] T049 Configure ChatInterface to use `chat-api.ts` and pass JWT token from auth context - ✅ JWT token automatically attached via lib/api.ts request interceptor
- [X] T050 Add "AI Assistant" navigation link in `frontend/app/layout.tsx` or navigation component pointing to `/agent` route - ✅ Added navigation links in both dashboard and chat pages
- [X] T051 [P] Style ChatInterface with Tailwind CSS to match Phase II design (consistent color scheme, spacing, typography) - ✅ Styled with gradient theme matching Phase II (blue-to-purple gradients, consistent spacing, rounded corners)

---

## Phase 11: Polish & Testing (3 tasks)

**Goal**: End-to-end testing, documentation, and final validation

**Independent Test Criteria**:
- ✅ Full conversation flow works end-to-end (create task via chat, list tasks, mark complete)
- ✅ Multi-user isolation verified (user A cannot see user B's conversations or tasks)
- ✅ All acceptance criteria from spec.md verified

### Tasks

- [ ] T052 Write integration test in `backend/tests/integration/test_conversation_flow.py`: Full conversation (user sends message → agent creates task → user lists tasks → user completes task)
- [ ] T053 Test multi-user isolation: Create 2 test users, verify each can only access own conversations and tasks
- [ ] T054 Update README.md with Phase III setup instructions (reference quickstart.md)

---

## Checklist Format Validation

**✅ All tasks follow required format**: `- [ ] [TaskID] [P?] [Story?] Description with file path`

**Format Breakdown**:
- Checkbox: ✅ All tasks start with `- [ ]`
- Task ID: ✅ Sequential T001-T054
- [P] marker: ✅ 18 tasks marked as parallelizable
- [Story] label: ✅ All user story tasks labeled [US1]-[US7]
- File paths: ✅ All tasks include specific file paths

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: User Stories 1-3 (18 tasks)
- US-1: Basic Chat (can send messages, get responses)
- US-2: Conversation Persistence (history persists across sessions)
- US-3: Task Creation (agent can create tasks via natural language)

**Justification**: This provides core value (chat with agent to create tasks) and validates the stateless architecture with database-backed conversation history.

### Incremental Delivery Plan

**Sprint 1** (Setup + Foundational):
- Phase 1: Setup (5 tasks)
- Phase 2: Foundational (8 tasks)
- **Deliverable**: Database schema, MCP infrastructure, agent core

**Sprint 2** (MVP):
- Phase 3: US-1 Basic Chat (6 tasks)
- Phase 4: US-2 Persistence (4 tasks)
- Phase 5: US-3 Task Creation (5 tasks)
- **Deliverable**: Working chat agent that can create tasks

**Sprint 3** (Enhanced NLP):
- Phase 6: US-4 Temporal Expressions (3 tasks)
- Phase 7: US-5 Priority Inference (3 tasks)
- **Deliverable**: Agent understands "tomorrow" and "urgent"

**Sprint 4** (Advanced Features):
- Phase 8: US-6 Task Prioritization (4 tasks)
- Phase 9: US-7 Security (6 tasks)
- **Deliverable**: Agent can suggest priorities, full security audit

**Sprint 5** (Frontend + Polish):
- Phase 10: Frontend Integration (7 tasks)
- Phase 11: Polish & Testing (3 tasks)
- **Deliverable**: Production-ready Phase III

### Parallel Execution Examples

**After Foundational Phase (T013) Complete**:

```
Parallel Track 1 (Backend - Task Creation):
T024, T025, T026 → T027 → T028

Parallel Track 2 (Backend - NLP):
T029 → T030 → T031 (Temporal)
T032 → T033 → T034 (Priority)

Parallel Track 3 (Backend - List/Prioritization):
T035, T036, T037 → T038

Parallel Track 4 (Frontend):
T045 → T049 → T050
T046 (can run parallel with T045)
T047, T048 (can run parallel with T045-T050)
T051 (styling, can run at any time)
```

**Estimated Parallelization Benefit**: 30-40% time reduction if 3-4 developers work concurrently

---

## Task Execution Notes

### Before Starting

1. ✅ Verify Phase II complete (backend API on :8000, frontend on :3000)
2. ✅ Obtain OpenAI API key from https://platform.openai.com/api-keys
3. ✅ Create feature branch: `git checkout -b 003-phase-3-ai-agent`
4. ✅ Review plan.md, data-model.md, and mcp-tools-spec.md

### During Implementation

- Run database migration (T008) before any database-dependent tasks
- Test MCP tools individually before integrating with agent (T024-T038)
- Mock OpenAI API in tests to avoid costs and non-determinism
- Verify JWT validation in every MCP tool (critical for security)
- Check conversation history loads correctly (stateless agent requirement)

### After Implementation

- Run full integration test (T052) to verify end-to-end flow
- Test multi-user isolation (T053) before deploying to production
- Create PHR documenting Phase III implementation
- Consider creating ADRs for significant architectural decisions

---

## References

- **Spec**: [specs/003-phase-3-ai-agent/spec.md](./spec.md)
- **Plan**: [specs/003-phase-3-ai-agent/plan.md](./plan.md)
- **MCP Tools**: [specs/003-phase-3-ai-agent/mcp-tools-spec.md](./mcp-tools-spec.md)
- **Data Model**: [specs/003-phase-3-ai-agent/data-model.md](./data-model.md)
- **API Contract**: [specs/003-phase-3-ai-agent/contracts/chat-api.openapi.yaml](./contracts/chat-api.openapi.yaml)
- **Quickstart**: [specs/003-phase-3-ai-agent/quickstart.md](./quickstart.md)

---

**Generated**: 2025-12-07
**Status**: ✅ Ready for Implementation
**Next Step**: Begin Phase 1 (Setup) with task T001
