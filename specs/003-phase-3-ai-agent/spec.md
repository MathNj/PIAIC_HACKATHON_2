# Feature: AI Chat Agent with MCP Integration

## Overview

This feature introduces an AI-powered chat agent that enables users to manage their TODO tasks through natural language conversation. The agent uses the Model Context Protocol (MCP) to interact with the existing Task API, maintaining strict statelessness by persisting all conversation history in the database.

## User Stories

- **US-1**: As a user, I want to chat with an AI agent to manage my tasks, so that I can use natural language instead of manual forms
- **US-2**: As a user, I want my conversation history to persist, so that I can resume conversations across sessions
- **US-3**: As a user, I want the agent to create tasks from my natural language descriptions, so that I don't have to fill out structured forms
- **US-4**: As a user, I want the agent to understand temporal expressions ("tomorrow", "next week"), so that I can set due dates naturally
- **US-5**: As a user, I want the agent to infer task priority from my language, so that urgent tasks are automatically marked as high priority
- **US-6**: As a user, I want the agent to help me prioritize my task list, so that I can focus on the most important items
- **US-7**: As a user, I want the agent to only access my own tasks, so that my data remains private and secure

## Acceptance Criteria

- [ ] **AC-1**: Conversation and Message database tables are created with proper relationships and indexes
- [ ] **AC-2**: Users can start a new conversation or continue an existing conversation
- [ ] **AC-3**: All conversation history is persisted in the database (no in-memory state)
- [ ] **AC-4**: Agent can create tasks using natural language input via MCP tools
- [ ] **AC-5**: Agent can list, update, and delete tasks via MCP tools
- [ ] **AC-6**: Agent correctly infers task priority from urgency keywords ("urgent", "asap", "critical")
- [ ] **AC-7**: Agent correctly parses temporal expressions ("tomorrow", "next week", "Monday at 2pm")
- [ ] **AC-8**: Agent provides task prioritization suggestions based on due dates and priorities
- [ ] **AC-9**: All MCP tools validate JWT token and enforce user_id isolation
- [ ] **AC-10**: Agent responses are saved to database before being returned to user
- [ ] **AC-11**: API endpoint supports both creating new conversations and continuing existing ones
- [ ] **AC-12**: Tool calls and results are logged in the messages table for auditability
- [ ] **AC-13**: Agent handles tool failures gracefully with user-friendly error messages
- [ ] **AC-14**: Conversation history is loaded from database on every request (stateless agent)
- [ ] **AC-15**: Frontend ChatKit UI integrates with the chat API endpoint

## Data Model (Backend)

### New Tables/Models Required

**1. Conversation Model**
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    title: Optional[str] = Field(default=None, max_length=200, description="Auto-generated conversation title")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

**2. Message Model**
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    conversation_id: int = Field(foreign_key="conversations.id", nullable=False, index=True)
    role: str = Field(nullable=False, description="Message role: 'user', 'assistant', 'system'")
    content: str = Field(nullable=False, description="Message content text")
    tool_calls: Optional[str] = Field(default=None, description="JSON string of tool calls made")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Relationships
- **Conversation → User**: Many-to-one (Each conversation belongs to one user)
- **Message → Conversation**: Many-to-one (Each message belongs to one conversation)
- **Cascading**: Deleting a conversation deletes all associated messages

### Indexes
- Index on `conversations.user_id` for efficient user conversation lookup
- Index on `messages.conversation_id` for efficient message retrieval
- Composite index on `(conversation_id, created_at)` for ordered message queries

## API Endpoints

### 1. Create/Continue Chat Conversation

**Method**: POST
**Path**: `/api/{user_id}/chat`
**Auth**: Required (JWT Bearer token)

**Request Body**:
```json
{
  "conversation_id": 123 | null,
  "message": "Create a task to buy groceries tomorrow"
}
```

**Request Parameters**:
- `conversation_id` (optional): Integer. If provided, continues existing conversation. If null/omitted, creates new conversation.
- `message` (required): String. User's message to the agent.

**Response (200)**:
```json
{
  "conversation_id": 123,
  "message": {
    "id": 456,
    "role": "assistant",
    "content": "I've created a task 'Buy groceries' with a due date of tomorrow (2025-12-08). The task has been added to your list with normal priority.",
    "created_at": "2025-12-07T10:30:00Z"
  },
  "tool_calls": [
    {
      "tool": "create_task",
      "arguments": {
        "title": "Buy groceries",
        "due_date": "2025-12-08",
        "priority": "normal"
      },
      "result": {
        "id": 789,
        "title": "Buy groceries",
        "due_date": "2025-12-08",
        "priority": "normal"
      }
    }
  ]
}
```

**Errors**:
- `400`: Validation error (missing message, invalid conversation_id)
- `401`: Unauthorized (missing or invalid JWT token)
- `403`: Forbidden (conversation_id belongs to different user)
- `404`: Conversation not found
- `500`: Agent execution error or database failure

**Processing Logic**:
1. **Authentication**: Extract user_id from JWT token
2. **Authorization**: Verify path user_id matches JWT user_id
3. **Conversation Handling**:
   - If `conversation_id` is null: Create new conversation
   - If `conversation_id` provided: Verify it belongs to user, retrieve it
4. **History Loading**: Load last N messages (default 20) from database ordered by created_at
5. **Message Saving**: Save user message to messages table
6. **Agent Execution**:
   - Construct conversation context from loaded history + new message
   - Execute OpenAI Agent with MCP tools available
   - Agent may call multiple tools (list_tasks, create_task, etc.)
7. **Tool Execution**: Execute MCP tools with user's JWT token for authorization
8. **Response Saving**: Save assistant response and tool_calls to messages table
9. **Conversation Update**: Update conversation.updated_at timestamp
10. **Return Response**: Return conversation_id, assistant message, and tool_calls

### 2. List User Conversations

**Method**: GET
**Path**: `/api/{user_id}/conversations`
**Auth**: Required (JWT Bearer token)

**Query Parameters**:
- `limit` (optional): Integer, default 20, max 100
- `offset` (optional): Integer, default 0

**Response (200)**:
```json
{
  "conversations": [
    {
      "id": 123,
      "title": "Task Management",
      "message_count": 15,
      "created_at": "2025-12-07T10:00:00Z",
      "updated_at": "2025-12-07T11:30:00Z",
      "last_message_preview": "I've updated the task priority..."
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### 3. Get Conversation History

**Method**: GET
**Path**: `/api/{user_id}/conversations/{conversation_id}/messages`
**Auth**: Required (JWT Bearer token)

**Query Parameters**:
- `limit` (optional): Integer, default 50, max 200
- `before_id` (optional): Integer, message ID for pagination

**Response (200)**:
```json
{
  "conversation_id": 123,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Show me my tasks",
      "created_at": "2025-12-07T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "You have 5 tasks...",
      "tool_calls": "[{\"tool\":\"list_tasks\",\"result\":[...]}]",
      "created_at": "2025-12-07T10:00:01Z"
    }
  ]
}
```

### 4. Delete Conversation

**Method**: DELETE
**Path**: `/api/{user_id}/conversations/{conversation_id}`
**Auth**: Required (JWT Bearer token)

**Response (200)**:
```json
{
  "detail": "Conversation and all messages deleted"
}
```

## MCP Tools (Required)

All tools MUST be implemented as strict MCP tools accessible to the agent:

### 1. `list_tasks`
- **Purpose**: Retrieve all tasks for authenticated user
- **Input**: `user_token: str`, `status?: "all" | "pending" | "completed"`
- **Output**: List of tasks with id, title, priority, due_date, completed

### 2. `create_task`
- **Purpose**: Create new task from natural language description
- **Input**: `user_token: str`, `title: str`, `description?: str`, `priority?: str`, `due_date?: str`
- **Output**: Created task object with id

### 3. `update_task`
- **Purpose**: Modify existing task properties
- **Input**: `user_token: str`, `task_id: int`, `title?: str`, `description?: str`, `priority?: str`, `due_date?: str`, `completed?: bool`
- **Output**: Updated task object

### 4. `delete_task`
- **Purpose**: Remove task by ID
- **Input**: `user_token: str`, `task_id: int`
- **Output**: Confirmation message

### 5. `toggle_task_completion`
- **Purpose**: Mark task as complete/incomplete
- **Input**: `user_token: str`, `task_id: int`
- **Output**: Updated task object

### 6. `get_task_summary`
- **Purpose**: Get analytics and statistics
- **Input**: `user_token: str`, `timeframe?: "today" | "this_week" | "overdue" | "all"`
- **Output**: Summary with counts, priorities, upcoming deadlines

### 7. `suggest_task_prioritization`
- **Purpose**: AI-powered task ordering recommendations
- **Input**: `user_token: str`
- **Output**: Ordered list of tasks with prioritization reasoning

## UI Requirements (Technology-Agnostic)

### Key Screens

**1. Agent Chat Interface**:
- Description: Full-screen or sidebar chat interface for agent interaction
- Actions: Send messages, view conversation history, start new conversation
- Navigation: Accessible from main dashboard via "AI Assistant" button or `/agent` route

**2. Conversation List**:
- Description: List of previous conversations with previews
- Actions: Select conversation to resume, delete old conversations
- Navigation: Sidebar or dedicated `/conversations` route

### User Flows

**1. New Conversation Flow**:
1. User clicks "AI Assistant" or navigates to `/agent`
2. Chat interface opens with empty conversation
3. User types natural language message (e.g., "Create a task to buy groceries tomorrow")
4. Agent responds and creates task using MCP tools
5. Conversation persisted in database
6. User can continue conversation or start new one

**2. Resume Conversation Flow**:
1. User selects existing conversation from list
2. Chat interface loads with full conversation history
3. User sends new message
4. Agent has context of entire conversation history
5. Agent responds appropriately with access to previous context

**3. Task Creation via Agent**:
1. User: "I need to fix the production bug urgently"
2. Agent extracts: title="Fix production bug", priority="high"
3. Agent calls `create_task` MCP tool
4. Agent confirms: "I've created a high-priority task 'Fix production bug'"

### Components Needed

- **ChatInterface**: Main chat UI with message bubbles, input field, send button
- **MessageList**: Scrollable list of messages with role-based styling
- **ConversationSidebar**: List of previous conversations with selection
- **TypingIndicator**: Shows when agent is processing
- **ToolCallDisplay**: Optional visual representation of tool executions
- **ErrorDisplay**: User-friendly error messages for agent failures

## Dependencies & Integration

**Existing Features**:
- Phase II Task CRUD API (existing endpoints)
- Phase II User Authentication (JWT tokens)
- Phase II Task model with priority and due_date fields

**Database Schema**:
- New tables: `conversations`, `messages`
- Foreign key to existing `users` table
- Cascading deletes for data integrity

**Authentication**:
- Reuse existing JWT authentication
- MCP tools receive JWT token and validate user_id
- Chat API endpoint requires JWT Bearer token

**New Dependencies**:
- OpenAI Agents SDK (Python)
- MCP Python SDK (Official Model Context Protocol)
- OpenAI ChatKit (Frontend React component)

## Non-Functional Requirements

**Performance**:
- Agent response time: < 5 seconds for simple queries
- Agent response time: < 10 seconds for complex multi-tool operations
- Conversation history loading: < 500ms for 50 messages
- Database queries optimized with proper indexes

**Security**:
- All MCP tools validate JWT token
- User_id isolation enforced at tool level (403 if mismatch)
- Conversation data scoped to authenticated user
- No cross-user conversation access
- Tool calls logged for audit trail

**Accessibility**:
- Chat interface keyboard navigable (Tab, Enter to send)
- ARIA labels for screen readers
- Message roles clearly distinguished visually
- Focus management for modal/sidebar

**Testing**:
- Unit tests for each MCP tool
- Integration tests for agent conversation flow
- End-to-end tests for ChatKit UI
- Mock LLM responses for deterministic testing
- Test conversation persistence across requests
- Test multi-user isolation

**Scalability**:
- Stateless agent design enables horizontal scaling
- Database-backed conversations support multiple agent instances
- No sticky sessions required
- Conversation history pagination for large conversations

**Data Retention**:
- Conversations persist indefinitely (user can delete manually)
- Consider adding conversation auto-archive after 90 days of inactivity (future)
- Messages never deleted unless entire conversation is deleted

## Implementation Phases

### Phase 1: Database Models & Migrations
- Create Conversation and Message SQLModel classes
- Generate database migration scripts
- Add indexes for performance
- Test cascading deletes

### Phase 2: MCP Tools Implementation
- Implement all 7 MCP tools in `backend/mcp/`
- Add JWT validation to each tool
- Write unit tests for each tool
- Register tools with MCP server

### Phase 3: Agent Orchestration
- Create agent runner in `backend/agents/`
- Implement conversation history loading
- Implement stateless agent execution with OpenAI SDK
- Handle tool call execution and result logging
- Test agent with mock conversations

### Phase 4: Chat API Endpoint
- Implement POST `/api/{user_id}/chat` endpoint
- Add conversation creation/retrieval logic
- Add message persistence before and after agent execution
- Implement error handling and validation
- Write integration tests

### Phase 5: Conversation Management API
- Implement GET `/api/{user_id}/conversations`
- Implement GET `/api/{user_id}/conversations/{id}/messages`
- Implement DELETE `/api/{user_id}/conversations/{id}`
- Add pagination support
- Write API tests

### Phase 6: Frontend Integration
- Install and configure OpenAI ChatKit
- Create ChatInterface component
- Integrate with chat API endpoint
- Add JWT token to requests
- Style consistently with Phase II design
- Test end-to-end flow

## Out of Scope

- Multi-user collaborative conversations (each conversation belongs to single user)
- Real-time streaming responses (future enhancement)
- Voice input/output (future enhancement)
- Conversation sharing or export (future enhancement)
- Agent training or fine-tuning (use base OpenAI models)
- Custom agent personalities or system prompts (future enhancement)
- Conversation branching or forking (linear conversation only)

## References

- Constitution: `.specify/memory/constitution.md` (Phase III constraints)
- Phase II Task API: `specs/002-phase-2/spec.md`
- MCP Tool Skill: `.claude/skills/mcp-tool-maker/SKILL.md`
- Backend Guidelines: `backend/CLAUDE.md`
- Frontend Guidelines: `frontend/CLAUDE.md`
