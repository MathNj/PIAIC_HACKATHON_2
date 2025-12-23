# Tasks: OpenAI Chatkit Integration & History Persistence

**Input**: Design documents from `/specs/006-chatkit-history-persistence/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: Tests are NOT explicitly requested in the specification, therefore test tasks are excluded. Testing will be performed manually during implementation based on acceptance criteria.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## User Story Mapping

| Story | Priority | Title | Goal |
|-------|----------|-------|------|
| US1 | P1 (MVP) | Start New AI Conversation | Enable basic chat with AI agent, send/receive messages |
| US2 | P2 | Resume Previous Conversation | Persist and reload conversation history |
| US3 | P3 | Manage Multiple Conversations | Create, list, switch between conversations |
| US4 | P3 | AI Tool Execution Visibility | Show MCP tool calls in chat interface |

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure

- [x] T001 Install backend dependencies: openai-agents-sdk==0.2.0, mcp-python==0.1.5 in backend/requirements.txt
- [x] T002 Install frontend dependency: @openai/chatkit@1.0.0 in frontend/package.json
- [x] T003 [P] Create TypeScript types file from contracts at frontend/src/types/chat.ts
- [x] T004 [P] Create backend Pydantic schemas directory: backend/app/schemas/conversation.py and backend/app/schemas/message.py
- [x] T005 Configure CORS middleware in backend/app/main.py to allow frontend origin with credentials

**Checkpoint**: ✅ COMPLETE - Dependencies installed, type definitions ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema, models, and core infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

**Agent Delegation**:
- Use **database-migration-specialist** agent with **db-migration-wizard** skill for T006-T007
- Use **backend-specialist** agent with **backend-scaffolder** skill for T008-T014
- Use **frontend-specialist** agent for T015

- [x] T006 Create Alembic migration for conversations and messages tables in backend/alembic/versions/xxxx_add_conversations_messages.py
  - **Agent**: database-migration-specialist
  - **Skill**: db-migration-wizard
  - **Command**: Invoke skill with conversation and message model definitions
- [x] T007 Run Alembic migration to create tables: `alembic upgrade head`
  - **Agent**: database-migration-specialist
  - **Skill**: db-migration-wizard
- [x] T008 [P] Add Conversation SQLModel to backend/app/models.py with user_id foreign key, title, timestamps, deleted_at
  - **Agent**: backend-specialist
  - **Skill**: backend-scaffolder
- [x] T009 [P] Add Message SQLModel to backend/app/models.py with conversation_id foreign key, role enum, content, tool_calls JSONB
  - **Agent**: backend-specialist
  - **Skill**: backend-scaffolder
- [x] T010 [P] Create ConversationCreate, ConversationUpdate, ConversationResponse schemas in backend/app/schemas/conversation.py
  - **Agent**: backend-specialist
  - **Skill**: crud-builder
- [x] T011 [P] Create MessageCreate, MessageResponse, SendMessageResponse schemas in backend/app/schemas/message.py
  - **Agent**: backend-specialist
  - **Skill**: crud-builder
- [x] T012 Create chat router file at backend/app/routers/chat.py with APIRouter setup
  - **Agent**: backend-specialist
  - **Skill**: fastapi-endpoint-generator
- [x] T013 Register chat router in backend/app/main.py with app.include_router(chat.router)
  - **Agent**: backend-specialist
- [x] T014 [P] Create agents directory structure: backend/app/agents/__init__.py
  - **Agent**: backend-specialist
- [x] T015 [P] Create frontend API client at frontend/src/lib/api/chat.ts with fetchWithAuth helper
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component

**Checkpoint**: ✅ COMPLETE - Foundation ready - database tables exist, models defined, router registered

---

## Phase 3: User Story 1 - Start New AI Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable users to send a message and receive an AI assistant response in real-time

**Independent Test**: User can click "Chat with AI", type "Help me organize my tasks", send message, and receive AI response with task information displayed properly

**Agent Delegation**:
- Use **backend-specialist** agent with **chatkit-integrator** and **openai-agents-sdk** skills for backend tasks
- Use **frontend-specialist** agent with **chatkit-integrator** skill for frontend tasks
- Use **backend-specialist** agent with **stateless-agent-enforcer** skill for stateless validation

### Implementation for User Story 1

**Backend: Chat API Endpoints**

- [x] T016 [P] [US1] Implement POST /api/chat/conversations endpoint in backend/app/routers/chat.py to create new conversation
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Generate conversation CRUD endpoints with JWT auth
- [x] T017 [P] [US1] Implement POST /api/chat/conversations/{id}/messages endpoint in backend/app/routers/chat.py (stub - returns user message only, no agent)
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Generate message persistence endpoint
- [x] T018 [US1] Add conversation ownership validation helper in backend/app/routers/chat.py: validate_conversation_ownership()
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Add tenant isolation validation
- [x] T019 [US1] Update POST messages endpoint to save user message to database with role='user'
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator

**Backend: Stateless Agent Integration**

- [x] T020 [P] [US1] Create context_manager.py at backend/app/agents/context_manager.py with load_conversation_context() function
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Implement context loading from database
- [x] T021 [P] [US1] Create chat_agent.py at backend/app/agents/chat_agent.py with run_agent() async function
  - **Agent**: backend-specialist
  - **Skill**: openai-agents-sdk
  - **Command**: Create stateless agent with database context loading
- [x] T022 [US1] Implement load_conversation_context() to fetch last 50 messages from database ordered chronologically
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Add cursor-based pagination for context loading
- [x] T023 [US1] Implement run_agent() to build OpenAI messages array from history and call OpenAI API with existing MCP tools
  - **Agent**: backend-specialist
  - **Skill**: openai-agents-sdk
  - **Command**: Integrate MCP tools with agent runtime
- [x] T024 [US1] Add tool execution logic in run_agent() to execute MCP tools and collect results
  - **Agent**: backend-specialist
  - **Skill**: openai-agents-sdk
  - **Command**: Add tool calling support with error handling
- [x] T025 [US1] Integrate run_agent() into POST messages endpoint: call agent after saving user message
  - **Agent**: backend-specialist
  - **Skill**: agent-orchestrator
  - **Command**: Wire up agent with JWT auth and session management
- [x] T026 [US1] Save assistant response to database with role='assistant' and tool_calls metadata
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Persist assistant messages with tool metadata
- [x] T026b [US1] Validate stateless agent implementation with compliance tests
  - **Agent**: backend-specialist
  - **Skill**: stateless-agent-enforcer
  - **Command**: Run stateless validation tests (state isolation, concurrency, restart)

**Frontend: Chat UI with Chatkit**

- [x] T027 [P] [US1] Implement chatApi.createConversation() in frontend/src/lib/api/chat.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Create API client with JWT authentication
- [x] T028 [P] [US1] Implement chatApi.sendMessage() in frontend/src/lib/api/chat.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
- [x] T029 [US1] Create Chatkit configuration file at frontend/src/lib/chatkit-config.ts with custom adapter
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Configure Chatkit with custom backend adapter
- [x] T030 [US1] Implement adapter.createConversation() and adapter.sendMessage() in chatkit-config.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Connect Chatkit to FastAPI backend
- [x] T031 [US1] Create chat page at frontend/src/app/chat/page.tsx with ChatKit component integration
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Create chat UI with ChatKit React components
- [x] T032 [US1] Configure ChatKit with enableMarkdown: true and enableSyntaxHighlighting: true
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
- [x] T033 [US1] Add "Chat" navigation link in frontend/src/app/layout.tsx
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component

**Acceptance Criteria Verification**

- [x] T034 [US1] Verify: Chat interface opens with empty conversation when "Chat with AI" clicked
- [x] T035 [US1] Verify: User message appears in chat immediately after send
- [x] T036 [US1] Verify: AI response appears within 5 seconds with proper formatting
- [x] T037 [US1] Verify: Typing indicator shows while AI is processing

**Checkpoint**: ✅ COMPLETE - MVP functional - users can chat with AI agent, messages persist to database, agent uses MCP tools

---

## Phase 4: User Story 2 - Resume Previous Conversation (Priority: P2)

**Goal**: Enable users to return after logout and continue previous conversation with full history intact

**Independent Test**: Create conversation, send messages, logout, login, verify conversation loads with all messages in chronological order

**Agent Delegation**:
- Use **backend-specialist** agent with **conversation-history-manager** skill for backend tasks
- Use **frontend-specialist** agent with **chatkit-integrator** skill for frontend tasks

### Implementation for User Story 2

**Backend: Conversation Persistence**

- [ ] T038 [P] [US2] Implement GET /api/chat/conversations/{id}/messages endpoint in backend/app/routers/chat.py
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Implement history retrieval endpoint with pagination
- [ ] T039 [P] [US2] Add pagination support with limit and since parameters to GET messages endpoint
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Add cursor-based pagination for message history
- [ ] T040 [US2] Implement messages query: filter by conversation_id, order by created_at ASC, apply limit
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Optimize query with proper indexes
- [ ] T041 [US2] Return MessageListResponse with messages array and total_count
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager

**Frontend: Load Conversation History**

- [ ] T042 [P] [US2] Implement chatApi.getMessages() in frontend/src/lib/api/chat.ts with limit and since params
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Create API client method for message history
- [ ] T043 [US2] Implement adapter.getMessages() in chatkit-config.ts to call chatApi.getMessages()
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Connect Chatkit to history endpoint
- [ ] T044 [US2] Configure Chatkit to load history on conversation open
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Enable automatic history loading
- [ ] T045 [US2] Add message polling logic: poll GET messages?since={last_timestamp} every 2 seconds when chat is active
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Implement polling for real-time updates

**Acceptance Criteria Verification**

- [ ] T046 [US2] Verify: Previous conversation loads with all messages when user returns
- [ ] T047 [US2] Verify: Messages display in chronological order
- [ ] T048 [US2] Verify: New messages can be sent to existing conversation
- [ ] T049 [US2] Verify: AI context includes previous conversation history in responses

**Checkpoint**: Conversation persistence works - users can resume chats across sessions

---

## Phase 5: User Story 3 - Manage Multiple Conversations (Priority: P3)

**Goal**: Enable users to organize different topics into separate conversations and switch between them

**Independent Test**: Create 3 conversations on different topics, navigate between them using sidebar, verify each maintains own context

**Agent Delegation**:
- Use **backend-specialist** agent with **conversation-history-manager** skill for backend conversation CRUD
- Use **backend-specialist** agent with **crud-builder** skill for standard CRUD operations
- Use **frontend-specialist** agent with **chatkit-integrator** skill for conversation list UI
- Use **frontend-specialist** agent with **frontend-component** skill for custom UI components

### Implementation for User Story 3

**Backend: Conversation Management**

- [ ] T050 [P] [US3] Implement GET /api/chat/conversations endpoint with cursor pagination in backend/app/routers/chat.py
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Implement conversation list endpoint with cursor pagination and user filtering
- [ ] T051 [P] [US3] Implement PUT /api/chat/conversations/{id} endpoint to update conversation title
  - **Agent**: backend-specialist
  - **Skill**: crud-builder
  - **Command**: Generate update endpoint with ownership validation
- [ ] T052 [P] [US3] Implement DELETE /api/chat/conversations/{id} endpoint for soft delete (set deleted_at)
  - **Agent**: backend-specialist
  - **Skill**: crud-builder
  - **Command**: Implement soft delete with audit trail
- [ ] T053 [US3] Add query logic for GET conversations: filter by user_id and deleted_at IS NULL, order by updated_at DESC
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Add tenant isolation and soft delete filtering
- [ ] T054 [US3] Add cursor pagination: if cursor provided, filter updated_at < cursor
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Implement cursor-based pagination for scalability
- [ ] T055 [US3] Calculate message_count and last_message_preview for each conversation in response
  - **Agent**: backend-specialist
  - **Skill**: conversation-history-manager
  - **Command**: Add metadata aggregation with efficient queries
- [ ] T056 [US3] Auto-generate conversation title from first message (first 50 chars) when creating conversation
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Add title auto-generation logic to conversation creation

**Frontend: Conversation List UI**

- [ ] T057 [P] [US3] Implement chatApi.listConversations() with limit and cursor params in frontend/src/lib/api/chat.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Create API client method for conversation listing
- [ ] T058 [P] [US3] Implement chatApi.updateConversationTitle() in frontend/src/lib/api/chat.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Create API client method for title updates
- [ ] T059 [P] [US3] Implement chatApi.deleteConversation() in frontend/src/lib/api/chat.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Create API client method for conversation deletion
- [ ] T060 [US3] Implement adapter.getConversations() in chatkit-config.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Connect Chatkit to conversation list endpoint
- [ ] T061 [US3] Implement adapter.updateConversationTitle() in chatkit-config.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Connect Chatkit to title update endpoint
- [ ] T062 [US3] Implement adapter.deleteConversation() in chatkit-config.ts
  - **Agent**: frontend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Connect Chatkit to deletion endpoint
- [ ] T063 [US3] Create ConversationList component at frontend/src/components/chat/ConversationList.tsx
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Create conversation sidebar component with list rendering
- [ ] T064 [US3] Display conversation title, timestamp, and message preview in ConversationList
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add metadata display with proper formatting
- [ ] T065 [US3] Add "New Conversation" button that calls createConversation
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add conversation creation button with click handler
- [ ] T066 [US3] Add delete icon for each conversation with confirmation dialog
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add delete action with user confirmation

**Acceptance Criteria Verification**

- [ ] T067 [US3] Verify: Conversations listed with titles, timestamps, and previews
- [ ] T068 [US3] Verify: "New Conversation" creates fresh conversation and switches to it
- [ ] T069 [US3] Verify: Clicking conversation in list loads its history
- [ ] T070 [US3] Verify: Each conversation maintains separate context
- [ ] T071 [US3] Verify: Delete removes conversation from list

**Checkpoint**: Multi-conversation management works - users can organize chats by topic

---

## Phase 6: User Story 4 - AI Tool Execution Visibility (Priority: P3)

**Goal**: Display which MCP tools the AI is calling and their results for transparency

**Independent Test**: Send "Create a task called 'Review Q4 report'", verify chat shows "AI is using: create_task" and result message

**Agent Delegation**:
- Use **backend-specialist** agent with **openai-agents-sdk** skill for tool call metadata capture
- Use **backend-specialist** agent with **mcp-tool-maker** skill for MCP tool integration
- Use **frontend-specialist** agent with **frontend-component** skill for tool visualization UI

### Implementation for User Story 4

**Backend: Tool Call Metadata**

- [ ] T072 [US4] Enhance run_agent() to capture tool call metadata: tool_name, arguments, result, timestamp, duration_ms, status
  - **Agent**: backend-specialist
  - **Skill**: openai-agents-sdk
  - **Command**: Add tool execution instrumentation and metadata capture
- [ ] T073 [US4] Store tool_calls metadata in tool_calls JSONB column when saving assistant message
  - **Agent**: backend-specialist
  - **Skill**: chatkit-integrator
  - **Command**: Persist tool metadata with assistant messages
- [ ] T074 [US4] Ensure tool_calls is included in MessageResponse schema
  - **Agent**: backend-specialist
  - **Skill**: crud-builder
  - **Command**: Update schema to expose tool_calls field

**Frontend: Tool Call Display**

- [ ] T075 [P] [US4] Create MessageBubble component at frontend/src/components/chat/MessageBubble.tsx
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Create message component with role-based rendering
- [ ] T076 [US4] Add tool call rendering logic: if message.tool_calls exists, show "AI is using: {tool_name}" indicator
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add tool call indicator display with conditional rendering
- [ ] T077 [US4] Display tool results in structured format (e.g., "Created task: Review Q4 report")
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Format tool results with structured display
- [ ] T078 [US4] Add user-friendly error messages when tool execution fails
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add error state handling for tool failures
- [ ] T079 [US4] Style tool call indicators with distinct visual treatment (icon, background color)
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Apply Tailwind CSS styling for tool indicators

**Acceptance Criteria Verification**

- [ ] T080 [US4] Verify: Tool indicator appears when AI calls MCP tool
- [ ] T081 [US4] Verify: Tool result displays in structured format
- [ ] T082 [US4] Verify: Error messages show when tool fails
- [ ] T083 [US4] Verify: Multiple tool calls in sequence all appear in conversation log

**Checkpoint**: Tool execution transparency complete - users see what actions AI is taking

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final touches, error handling, performance optimization, and deployment readiness

**Agent Delegation**:
- Use **backend-specialist** agent with **fastapi-endpoint-generator** skill for validation and rate limiting
- Use **database-migration-specialist** agent with **db-migration-wizard** skill for index optimization
- Use **frontend-specialist** agent with **frontend-component** skill for UX improvements
- Use **api-integration-specialist** agent with **cors-fixer** skill for CORS configuration
- Use **lead-engineer** agent for deployment preparation and testing standards

**Security & Error Handling**

- [ ] T084 [P] Add input validation for message content length (max 10,000 chars) in backend
  - **Agent**: backend-specialist
  - **Skill**: fastapi-endpoint-generator
  - **Command**: Add Pydantic field validation with max_length constraint
- [ ] T085 [P] Add input validation for conversation title length (max 200 chars) in backend
  - **Agent**: backend-specialist
  - **Skill**: fastapi-endpoint-generator
  - **Command**: Add Pydantic field validation for title field
- [ ] T086 [P] Implement rate limiting for chat endpoints (prevent abuse)
  - **Agent**: backend-specialist
  - **Skill**: fastapi-endpoint-generator
  - **Command**: Add rate limiting middleware with slowapi or custom decorator
- [ ] T087 [P] Add comprehensive error messages for all failure scenarios (network, auth, validation)
  - **Agent**: api-integration-specialist
  - **Skill**: api-schema-sync
  - **Command**: Standardize error response format across frontend and backend

**Performance Optimization**

- [ ] T088 [P] Add database indexes verification: (user_id, updated_at DESC), (conversation_id, created_at ASC)
  - **Agent**: database-migration-specialist
  - **Skill**: db-migration-wizard
  - **Command**: Create migration with composite indexes for query optimization
- [ ] T089 [P] Test conversation history load performance with 100 messages (target: <2 seconds)
  - **Agent**: backend-specialist
  - **Skill**: integration-tester
  - **Command**: Create performance test suite for history loading
- [ ] T090 [P] Test message send latency (target: <5 seconds including AI response)
  - **Agent**: backend-specialist
  - **Skill**: integration-tester
  - **Command**: Create performance test for end-to-end message flow
- [ ] T091 [P] Optimize polling interval based on conversation activity
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Implement adaptive polling (2s active, 10s idle)

**User Experience**

- [ ] T092 [P] Add loading states for all async operations (creating conversation, sending message)
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add loading skeletons and spinners with Tailwind CSS
- [ ] T093 [P] Add character counter when message approaches 10,000 limit
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add character count display with warning threshold
- [ ] T094 [P] Add responsive design testing for mobile browsers
  - **Agent**: frontend-specialist
  - **Skill**: integration-tester
  - **Command**: Test responsive breakpoints and mobile interactions
- [ ] T095 [P] Add keyboard shortcuts (Enter to send, Ctrl+N for new conversation)
  - **Agent**: frontend-specialist
  - **Skill**: frontend-component
  - **Command**: Add keyboard event handlers with modifier key support

**Deployment Preparation**

- [ ] T096 Update backend .env.example with OPENAI_API_KEY, DATABASE_URL
  - **Agent**: backend-specialist
  - **Skill**: None (direct file edit)
  - **Command**: Add environment variable documentation
- [ ] T097 Update frontend .env.example with NEXT_PUBLIC_API_URL
  - **Agent**: frontend-specialist
  - **Skill**: None (direct file edit)
  - **Command**: Add frontend environment variable documentation
- [ ] T098 [P] Verify CORS configuration includes production frontend URL
  - **Agent**: api-integration-specialist
  - **Skill**: cors-fixer
  - **Command**: Update CORS middleware with production origins
- [ ] T099 [P] Create deployment checklist in quickstart.md
  - **Agent**: lead-engineer
  - **Skill**: doc-generator
  - **Command**: Generate deployment checklist with verification steps
- [ ] T100 Run smoke test: create conversation, send message, verify persistence, check tool execution
  - **Agent**: lead-engineer
  - **Skill**: integration-tester
  - **Command**: Create smoke test suite for critical user flows

**Checkpoint**: Feature complete and production-ready

---

## Dependencies & Execution Strategy

### Story Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← MUST complete before any user story
    ↓
    ├─→ Phase 3 (US1 - P1) ← MVP, implement FIRST
    │       ↓
    ├─→ Phase 4 (US2 - P2) ← Depends on US1 (needs conversation creation)
    │       ↓
    ├─→ Phase 5 (US3 - P3) ← Depends on US1 and US2 (needs conversation CRUD)
    │       ↓
    └─→ Phase 6 (US4 - P3) ← Depends on US1 (needs agent integration)
            ↓
        Phase 7 (Polish) ← Cross-cutting, can run in parallel with stories
```

### Critical Path

**Sequential (must complete in order)**:
1. Phase 1 (Setup) → Phase 2 (Foundational)
2. Phase 2 → US1 (MVP)
3. US1 → US2 (Resume conversation needs conversation creation)
4. US2 → US3 (Multi-conversation needs persistence)

**Parallel Opportunities**:
- After US1: US4 can run in parallel with US2 (different components)
- Phase 7 polish tasks can run alongside US3/US4 implementation

### MVP Delivery Strategy

**MVP Scope (Minimum Viable Product)**: Phase 1 + Phase 2 + Phase 3 (US1 only)

**Incremental Delivery**:
1. **Release 1 (MVP)**: US1 only - Basic chat with AI, message persistence
2. **Release 2**: US1 + US2 - Add conversation resume capability
3. **Release 3**: US1 + US2 + US3 - Add multi-conversation management
4. **Release 4 (Complete)**: All stories + Polish

### Parallel Execution Examples

**During Phase 2 (Foundational)**:
```bash
# Run these tasks concurrently (different files, no dependencies):
T008 (Add Conversation model) || T009 (Add Message model)
T010 (Conversation schemas) || T011 (Message schemas)
T014 (Create agents dir) || T015 (Create API client)
```

**During Phase 3 (US1 Implementation)**:
```bash
# Backend and Frontend can work in parallel:
T016-T019 (Backend endpoints) || T027-T033 (Frontend UI)
T020-T021 (Create agent files) || T029-T032 (Chatkit config)
```

**During Phase 5 (US3 Implementation)**:
```bash
# Backend and Frontend work in parallel:
T050-T056 (Backend conversation mgmt) || T057-T066 (Frontend UI)
```

**During Phase 7 (Polish)**:
```bash
# All polish tasks can run in parallel:
T084-T087 (Validation) || T088-T091 (Performance) || T092-T095 (UX) || T096-T099 (Deployment)
```

---

## Task Summary

**Total Tasks**: 100

**Tasks per User Story**:
- Setup (Phase 1): 5 tasks
- Foundational (Phase 2): 10 tasks
- US1 - Start New AI Conversation (P1): 22 tasks (MVP)
- US2 - Resume Previous Conversation (P2): 12 tasks
- US3 - Manage Multiple Conversations (P3): 22 tasks
- US4 - AI Tool Execution Visibility (P3): 12 tasks
- Polish (Phase 7): 17 tasks

**Parallel Execution Opportunities**: 48 tasks marked with [P] can run in parallel

**MVP Scope**: Phases 1-3 (37 tasks total, ~6 hours estimated)

**Full Feature**: All 100 tasks (~16 hours estimated)

**Independent Test Criteria**:
- US1: User can send message and get AI response
- US2: User can reload page and continue conversation
- US3: User can manage multiple conversation threads
- US4: User can see which tools AI is calling

---

## Implementation Notes

1. **Start with MVP**: Implement Phases 1-3 first for fastest time-to-value
2. **Test incrementally**: Verify each user story independently before moving to next
3. **Use quickstart.md**: Detailed code examples provided for each phase
4. **Stateless requirement**: CRITICAL - always load conversation history from database, never cache in memory
5. **Tenant isolation**: ALWAYS filter by user_id from JWT token on all queries
6. **Error handling**: Implement graceful degradation for network failures, agent timeouts
7. **Performance**: Monitor database query performance, add indexes if needed
8. **Security**: Validate all user inputs, enforce content length limits, use parameterized queries

---

## Success Criteria (from spec.md)

- [ ] SC-001: Message delivery <5 seconds
- [ ] SC-002: 100% message persistence (zero loss)
- [ ] SC-003: History load <2 seconds for 100 messages
- [ ] SC-004: Resume conversation after logout works
- [ ] SC-005: Responsive design on desktop and mobile
- [ ] SC-006: 95% operation success rate
- [ ] SC-007: 50 concurrent conversations without degradation
- [ ] SC-008: Tool call information visible in history
- [ ] SC-009: User_id filtering prevents unauthorized access
- [ ] SC-010: Zero cross-tenant data leakage
