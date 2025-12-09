# Research: AI Chat Agent with MCP Integration

**Feature**: AI Chat Agent with MCP Integration
**Date**: 2025-12-07
**Phase**: III (Agent-Augmented System)

## Overview

This research document addresses all technology decisions, integration patterns, and best practices for implementing Phase III AI Chat Agent with Model Context Protocol (MCP) integration.

## Technology Decisions

### 1. AI Agent Framework: OpenAI Agents SDK

**Decision**: Use OpenAI Agents SDK for agent orchestration

**Rationale**:
- Official SDK with best-in-class LLM integration
- Native support for tool calling (MCP tools)
- Stateless execution model aligns with constitution requirements
- Conversation history management built-in
- Production-ready with comprehensive error handling

**Alternatives Considered**:
- LangChain: More complex, unnecessary abstraction for our use case
- Custom OpenAI API integration: Reinventing the wheel, more maintenance burden
- Anthropic Claude: Constitution specifies OpenAI for Phase III

**Implementation Pattern**:
```python
from openai import OpenAI
from mcp import MCPServer

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Stateless agent execution
response = client.chat.completions.create(
    model="gpt-4",
    messages=conversation_history,  # Loaded from database
    tools=mcp_server.list_tools(),  # MCP tools available
)
```

**Dependencies**:
- `openai>=1.0.0` (Python SDK)
- Environment variable: `OPENAI_API_KEY`

---

### 2. Model Context Protocol: Official MCP Python SDK

**Decision**: Use official MCP Python SDK from ModelContextProtocol organization

**Rationale**:
- Standardized protocol for AI-application communication
- Type-safe tool definitions with Python decorators
- Automatic schema generation from function signatures
- Separates AI layer from business logic (clean architecture)
- Future-proof (protocol-level abstraction)

**Alternatives Considered**:
- Custom tool calling implementation: No standardization, manual schema management
- LangChain Tools: Tied to LangChain ecosystem, not protocol-based
- Direct function calling: No type safety, no schema generation

**Implementation Pattern**:
```python
from mcp import MCPServer

mcp = MCPServer(name="todo-mcp-server")

@mcp.tool()
def create_task(
    user_token: str,
    title: str,
    description: Optional[str] = None,
    priority: Optional[Literal["low", "normal", "high"]] = None,
    due_date: Optional[str] = None
) -> str:
    """
    Create a new task for the user.

    This tool creates a task with specified title and optional details.
    Priority defaults to "normal" if not specified.
    """
    # Implementation with JWT validation and database access
    pass
```

**Dependencies**:
- `mcp>=0.1.0` (Official MCP Python SDK)
- Integrates with existing FastAPI backend

---

### 3. Frontend Chat UI: OpenAI ChatKit

**Decision**: Use OpenAI ChatKit React component library

**Rationale**:
- Production-ready chat interface components
- Designed for OpenAI agent integration
- Handles message rendering, streaming, tool call display
- Customizable styling with Tailwind CSS
- Active maintenance and documentation

**Alternatives Considered**:
- Custom React components: Significant development time, potential UX issues
- Vercel AI SDK UI: Good alternative, but ChatKit more specialized for OpenAI
- Chatbot UI libraries: Generic, not optimized for AI agent patterns

**Implementation Pattern**:
```typescript
import { ChatInterface } from '@openai/chatkit-react';

function AgentPage() {
  return (
    <ChatInterface
      apiEndpoint="/api/{userId}/chat"
      authToken={jwt Token}
      onToolCall={(tool, args) => console.log('Tool called:', tool)}
      theme="custom"
    />
  );
}
```

**Dependencies**:
- `@openai/chatkit-react@latest` (npm package)
- Requires Next.js 16+ and React 18+

---

### 4. Database Schema: Conversation Persistence

**Decision**: Add `conversations` and `messages` tables with foreign keys to existing `users` table

**Rationale**:
- Stateless agent requirement mandates database-backed history
- Relational model ensures data integrity with foreign keys
- Indexes optimize conversation retrieval performance
- Cascading deletes maintain referential integrity
- Tool call audit trail stored in `messages.tool_calls` JSON field

**Schema Design**:
```sql
-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tool_calls TEXT,  -- JSON string of tool executions
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

**Migration Strategy**:
- Alembic migration adds tables without breaking existing schema
- Indexes created after table creation for performance
- No data migration needed (new feature, no existing data)

---

### 5. Authentication Pattern: JWT Token Propagation

**Decision**: Pass JWT token from chat API to all MCP tools for user_id validation

**Rationale**:
- Maintains Phase II authentication architecture (no changes to auth system)
- MCP tools validate token and extract user_id independently
- Enforces multi-user isolation at tool level (defense in depth)
- Prevents cross-user data access even if agent misbehaves
- Audit trail includes user_id for all tool calls

**Implementation Pattern**:
```python
# Chat API receives JWT
@router.post("/api/{user_id}/chat")
async def chat(
    user_id: UUID,
    request: ChatRequest,
    current_user: Annotated[UUID, Depends(get_current_user)],
):
    # Verify user_id matches token
    if user_id != current_user:
        raise HTTPException(status_code=403)

    # Get JWT token from Authorization header
    token = request.headers.get("Authorization").split(" ")[1]

    # Execute agent with tools receiving token
    response = agent.execute(
        conversation_history,
        tools_context={"user_token": token}
    )
```

**Each MCP tool validates independently**:
```python
@mcp.tool()
def create_task(user_token: str, title: str, ...) -> str:
    try:
        user_id = verify_token(user_token)  # Existing auth function
        # Create task for validated user
    except HTTPException:
        return "Authentication error: Invalid token"
```

---

### 6. Natural Language Processing: Temporal and Priority Parsing

**Decision**: Use combination of rule-based parsing and LLM-powered extraction

**Rationale**:
- Temporal expressions ("tomorrow", "next week") require consistent parsing
- Priority inference benefits from LLM understanding of urgency keywords
- Hybrid approach balances reliability and intelligence
- Falls back to defaults if parsing fails (graceful degradation)

**Temporal Parsing Strategy**:
```python
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from datetime import datetime

def parse_due_date(natural_language: str) -> Optional[datetime]:
    """Parse natural language due dates to datetime."""
    text = natural_language.lower()
    now = datetime.utcnow()

    # Rule-based common expressions
    if "tomorrow" in text:
        return now + timedelta(days=1)
    elif "next week" in text:
        return now + timedelta(weeks=1)
    elif "monday" in text or "tuesday" in text:  # etc
        # Use dateutil to find next occurrence
        return parse(text, fuzzy=True)

    # ISO format fallback
    try:
        return parse(natural_language)
    except:
        return None  # Let agent decide or ask user
```

**Priority Inference Strategy**:
```python
def infer_priority(description: str) -> Literal["low", "normal", "high"]:
    """Infer task priority from description keywords."""
    text = description.lower()

    # High priority keywords
    if any(word in text for word in ["urgent", "asap", "critical", "emergency", "now"]):
        return "high"

    # Low priority keywords
    if any(word in text for word in ["maybe", "sometime", "eventually", "nice to have"]):
        return "low"

    # Default
    return "normal"
```

**LLM Integration** (for complex cases):
- Agent itself can be instructed to extract structured data
- System prompt includes examples of task extraction
- LLM handles edge cases and ambiguity

---

### 7. Error Handling: Tool Failures and Agent Recovery

**Decision**: MCP tools return structured error strings, never raise exceptions

**Rationale**:
- Agent must handle tool failures gracefully
- Structured error messages parseable by LLM
- User sees friendly error messages, not stack traces
- Failed tools don't crash agent execution
- Audit trail includes error details in tool_calls log

**Error Handling Pattern**:
```python
@mcp.tool()
def create_task(user_token: str, title: str, ...) -> str:
    try:
        user_id = verify_token(user_token)

        # Validate input
        if not title or len(title) > 200:
            return "Error: Task title must be 1-200 characters"

        # Database operation
        with Session(engine) as session:
            task = Task(user_id=user_id, title=title, ...)
            session.add(task)
            session.commit()
            session.refresh(task)

        return f"Task {task.id} created: {task.title}"

    except HTTPException as e:
        return f"Authentication error: {e.detail}"
    except SQLAlchemyError as e:
        return f"Database error: Unable to create task"
    except Exception as e:
        logger.error(f"Unexpected error in create_task: {str(e)}")
        return "Error: Unable to create task. Please try again."
```

**Agent Response to Errors**:
- LLM receives error string in tool result
- Agent can retry with corrected parameters
- Agent explains error to user in natural language
- User never sees technical error details

---

### 8. Performance Optimization: Conversation History Limit

**Decision**: Load last 20 messages by default, with pagination for longer conversations

**Rationale**:
- Full conversation history increases LLM token usage and cost
- Most conversations need only recent context
- 20 messages typically covers 10 exchanges (sufficient context)
- Pagination available for "remind me what we discussed earlier" queries
- Database query performance optimized with indexed limit/offset

**Implementation**:
```python
def load_conversation_history(
    conversation_id: int,
    limit: int = 20,
    offset: int = 0
) -> List[Message]:
    """Load recent conversation history with pagination."""
    with Session(engine) as session:
        messages = session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()

        # Return in chronological order (oldest first)
        return list(reversed(messages))
```

**Cost Optimization**:
- Fewer messages = fewer tokens = lower OpenAI API cost
- Estimated cost per chat: ~$0.01-0.05 depending on conversation length
- Tool calls add minimal cost (structured outputs are efficient)

---

### 9. Testing Strategy: Mock LLM Responses

**Decision**: Use deterministic mock responses for unit and integration tests

**Rationale**:
- Real LLM calls are non-deterministic and expensive
- Tests must be fast and reliable (CI/CD)
- Mock tool calls with predefined responses
- Test error handling without real failures
- End-to-end tests can use real LLM (optional, manual)

**Testing Pattern**:
```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client with deterministic responses."""
    with patch('openai.OpenAI') as mock:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="I've created the task for you.",
                    tool_calls=[
                        MagicMock(
                            function=MagicMock(
                                name="create_task",
                                arguments='{"title": "Test Task"}'
                            )
                        )
                    ]
                )
            )
        ]
        mock.return_value.chat.completions.create.return_value = mock_response
        yield mock

def test_create_task_via_agent(mock_openai_client, auth_token):
    """Test agent creates task when user requests it."""
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Create a task to test the feature"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    assert "created" in response.json()["message"]["content"].lower()
```

---

### 10. Deployment Considerations: API Key Management

**Decision**: Store OpenAI API key in environment variables, never in code or database

**Rationale**:
- Security best practice (no secrets in version control)
- Same pattern as Phase II database credentials
- Vercel deployment supports environment variables
- Local development uses `.env.local`
- Rotation possible without code changes

**Environment Variables Required**:
```bash
# Phase II (existing)
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
FRONTEND_URL=https://...

# Phase III (new)
OPENAI_API_KEY=sk-...
MCP_SERVER_PORT=8001  # Optional, defaults to 8001
CONVERSATION_HISTORY_LIMIT=20  # Optional, defaults to 20
```

**Vercel Deployment**:
```bash
vercel env add OPENAI_API_KEY production
```

---

## Integration Patterns

### Pattern 1: Stateless Agent Execution Flow

```
1. User sends message → POST /api/{user_id}/chat
2. API validates JWT token → extract user_id
3. Load or create conversation → database query
4. Load last 20 messages → database query
5. Save user message → database insert
6. Build conversation context → [system prompt + history + new message]
7. Execute OpenAI agent → agent.execute(context, tools=mcp_tools)
8. Agent may call multiple MCP tools → each validates JWT independently
9. Save assistant response → database insert
10. Save tool calls to audit trail → messages.tool_calls JSON
11. Return response → JSON with conversation_id, message, tool_calls
```

### Pattern 2: MCP Tool Security Validation

```
1. Agent calls MCP tool → tool(user_token="Bearer xyz", task_id=123, ...)
2. Tool validates JWT → verify_token(user_token) → user_id
3. Tool queries database → WHERE user_id = {extracted_user_id}
4. Multi-user isolation enforced → 403 if task.user_id != token_user_id
5. Tool executes operation → CREATE/UPDATE/DELETE
6. Tool returns structured response → "Task 123 created: Buy groceries"
7. Agent receives tool result → interprets and responds to user
```

### Pattern 3: Frontend Chat Integration

```
1. User navigates to /agent → ChatInterface component loads
2. ChatInterface fetches conversations → GET /api/{user_id}/conversations
3. User selects conversation or starts new → state management
4. User types message → local state update
5. User presses Send → POST /api/{user_id}/chat with JWT header
6. Loading indicator → "Agent is typing..."
7. Response received → message added to conversation
8. Tool calls displayed → optional UI component showing what agent did
9. Conversation persisted → database handles state
```

---

## Dependencies Summary

**Backend (Python)**:
- `openai>=1.0.0` - OpenAI Agents SDK
- `mcp>=0.1.0` - Model Context Protocol SDK
- `python-dateutil>=2.8.2` - Temporal expression parsing
- All Phase II dependencies (FastAPI, SQLModel, Alembic, etc.)

**Frontend (TypeScript)**:
- `@openai/chatkit-react@latest` - Chat UI components
- All Phase II dependencies (Next.js, React, Tailwind, etc.)

**Environment Variables**:
- `OPENAI_API_KEY` - Required for agent execution
- `MCP_SERVER_PORT` - Optional, defaults to 8001
- `CONVERSATION_HISTORY_LIMIT` - Optional, defaults to 20

**Database**:
- PostgreSQL (existing Neon instance)
- 2 new tables: `conversations`, `messages`
- 4 new indexes for query optimization

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API cost escalation | High | Limit conversation history to 20 messages, implement rate limiting |
| LLM hallucinations (creating wrong tasks) | Medium | Validate all tool inputs, confirmation UI for destructive actions |
| JWT token leakage to LLM logs | High | Never log full tokens, mask in error messages |
| Database performance (large conversations) | Medium | Indexes on conversation_id, pagination for history |
| MCP tool failures crashing agent | Medium | Structured error returns, never raise exceptions in tools |
| Cross-user data access via agent | Critical | Multi-user isolation in every MCP tool, audit trail for access |

---

## Success Metrics

**Functional**:
- ✅ Agent creates tasks from natural language with 95% accuracy
- ✅ Temporal expressions parsed correctly ("tomorrow" → due_date)
- ✅ Priority inference matches user intent in 90% of cases
- ✅ Conversation history persists across sessions
- ✅ All 7 MCP tools implemented and validated

**Performance**:
- ✅ Agent response time < 5 seconds for simple queries
- ✅ Agent response time < 10 seconds for multi-tool operations
- ✅ Database query time < 500ms for conversation loading
- ✅ API cost per conversation < $0.10

**Security**:
- ✅ Zero cross-user data access incidents
- ✅ All MCP tools validate JWT on every call
- ✅ Tool call audit trail complete (100% coverage)
- ✅ No PII or tokens leaked in logs

---

## Next Steps

This research resolves all NEEDS CLARIFICATION items from Technical Context:

1. ✅ Language/Version: Python 3.13+ (existing)
2. ✅ Primary Dependencies: OpenAI Agents SDK, MCP Python SDK, OpenAI ChatKit
3. ✅ Storage: PostgreSQL with conversations/messages tables
4. ✅ Testing: pytest with mocked LLM responses
5. ✅ Performance Goals: < 5s agent response, < 500ms DB queries
6. ✅ Constraints: Stateless agent, JWT validation, multi-user isolation
7. ✅ Scale/Scope: Support 100+ concurrent users, 1000+ conversations

Proceed to **Phase 1: Design & Contracts** to generate data models and API contracts.
