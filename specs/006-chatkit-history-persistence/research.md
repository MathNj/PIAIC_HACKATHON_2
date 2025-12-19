# Research: OpenAI Chatkit Integration & History Persistence

**Phase**: 0 (Research & Technical Decisions)
**Date**: 2025-12-19
**Status**: Complete

## Purpose

This document resolves all technical unknowns identified in the Technical Context of `plan.md` by researching best practices, evaluating alternatives, and documenting architectural decisions for Phase III Chatkit integration with stateless agent architecture.

## Research Areas

### 1. Real-Time Message Delivery Mechanism

**Decision**: HTTP Polling with fallback to Server-Sent Events (SSE)

**Rationale**:
- **Simplicity**: HTTP polling is easiest to implement and works with existing Vercel deployment
- **Compatibility**: Works with all browsers and requires no infrastructure changes
- **Performance**: For <5 second response time requirement, polling every 2-3 seconds is acceptable
- **Future upgrade path**: Can migrate to SSE or WebSockets in Phase IV without frontend changes

**Alternatives Considered**:
1. **WebSockets**: Rejected - Requires long-lived connections, complex with Vercel serverless functions, overkill for current scale
2. **Server-Sent Events (SSE)**: Considered for future - Better than polling but more complex to implement initially
3. **Long polling**: Rejected - Similar complexity to SSE but less efficient

**Implementation**:
- Frontend: `setInterval` to poll `/api/chat/{conversation_id}/messages?since={timestamp}` every 2 seconds when chat is open
- Backend: Simple GET endpoint returns messages created after `since` timestamp
- Optimization: Stop polling when user navigates away from chat page

### 2. Conversation Title Generation Strategy

**Decision**: Auto-generate from first user message with manual override capability

**Rationale**:
- **User Experience**: Automatic naming reduces friction for starting conversations
- **Searchability**: Meaningful titles make conversation history browsable
- **Flexibility**: Users can manually rename if auto-generation is inadequate

**Alternatives Considered**:
1. **Prompt user for title**: Rejected - Adds friction to conversation start
2. **AI-generated summary**: Rejected - Adds latency and API costs, unnecessary for MVP
3. **Generic titles ("Conversation 1")**: Rejected - Poor UX for managing multiple conversations

**Implementation**:
- Extract first 50 characters from first user message
- Remove markdown formatting and special characters
- If message starts with question word ("What", "How"), use full question as title
- Provide PUT endpoint for manual title updates: `PUT /api/chat/conversations/{id}/title`

### 3. Markdown Rendering and Code Block Handling

**Decision**: Use OpenAI Chatkit's built-in markdown renderer with syntax highlighting

**Rationale**:
- **Zero configuration**: Chatkit includes markdown rendering out of the box
- **Syntax highlighting**: Code blocks are syntax-highlighted automatically
- **Consistency**: Matches OpenAI ChatGPT UI conventions users are familiar with
- **Security**: Chatkit sanitizes HTML to prevent XSS attacks

**Alternatives Considered**:
1. **Custom markdown renderer (marked.js + highlight.js)**: Rejected - Reinventing wheel, more code to maintain
2. **Plain text only**: Rejected - Poor UX for AI responses containing code or formatted text
3. **React Markdown**: Rejected - Chatkit already provides this functionality

**Implementation**:
- Configure Chatkit with `enableMarkdown: true` option
- No custom rendering logic needed
- Test with code blocks in multiple languages (Python, JavaScript, SQL)

### 4. Tool Call Metadata Storage Format

**Decision**: Store tool calls as JSON in `messages.tool_calls` JSONB column

**Rationale**:
- **Flexibility**: JSON structure allows varying tool schemas without schema migrations
- **Queryability**: PostgreSQL JSONB enables efficient querying of tool usage patterns
- **Auditability**: Full tool execution context preserved for debugging and analytics
- **Native support**: SQLModel and PostgreSQL natively support JSONB columns

**Alternatives Considered**:
1. **Separate `tool_calls` table**: Rejected - Over-normalization for MVP, adds JOIN complexity
2. **String serialization**: Rejected - Loses queryability and type safety
3. **Text column with JSON**: Rejected - JSONB provides better performance and indexing

**Implementation Schema**:
```json
{
  "tool_calls": [
    {
      "tool_name": "create_task",
      "arguments": {"title": "Buy groceries", "priority": "normal"},
      "result": {"task_id": "123", "status": "created"},
      "timestamp": "2025-12-19T10:30:00Z",
      "duration_ms": 245
    }
  ]
}
```

### 5. Chatkit Backend Adapter Pattern

**Decision**: Custom adapter that maps Chatkit's expected API to our FastAPI endpoints

**Rationale**:
- **Control**: Full control over data format and security
- **Integration**: Seamlessly integrates with existing FastAPI auth middleware
- **Flexibility**: Can customize behavior without Chatkit library constraints
- **Documentation**: OpenAI Chatkit docs provide clear adapter interface specification

**Alternatives Considered**:
1. **Chatkit's default adapter**: Rejected - Assumes specific backend API format we don't match
2. **Proxy server**: Rejected - Unnecessary complexity, adds network hop
3. **Fork Chatkit library**: Rejected - Maintenance burden, breaks upgrade path

**Implementation**:
```typescript
// frontend/src/lib/chatkit-config.ts
const chatAdapter = {
  async getConversations() {
    return fetch('/api/chat/conversations').then(res => res.json())
  },
  async getMessages(conversationId) {
    return fetch(`/api/chat/conversations/${conversationId}/messages`).then(res => res.json())
  },
  async sendMessage(conversationId, content) {
    return fetch(`/api/chat/conversations/${conversationId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content })
    }).then(res => res.json())
  }
}
```

### 6. Stateless Agent Context Loading Strategy

**Decision**: Load full conversation history on every request using SQL query with LIMIT

**Rationale**:
- **Constitutional compliance**: Stateless architecture requirement (no in-memory state)
- **Simplicity**: Single SQL query fetches all needed context
- **Scalability**: Works with multiple agent instances (no sticky sessions needed)
- **Context window management**: LIMIT clause prevents context overflow for very long conversations

**Alternatives Considered**:
1. **Caching in Redis**: Rejected - Violates stateless requirement, adds infrastructure dependency
2. **Summary-based context**: Rejected - Adds complexity and potential information loss, not needed for MVP
3. **Lazy loading**: Rejected - Adds latency to agent responses

**Implementation**:
```python
# backend/app/agents/context_manager.py
def load_conversation_context(conversation_id: str, limit: int = 50) -> List[Message]:
    """
    Load most recent messages for agent context.
    Limit to last 50 messages to fit within token budget.
    """
    return db.query(Message)\
        .filter(Message.conversation_id == conversation_id)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .all()[::-1]  # Reverse to chronological order
```

### 7. Conversation Pagination Strategy

**Decision**: Cursor-based pagination using `created_at` timestamp

**Rationale**:
- **Performance**: More efficient than OFFSET for large datasets
- **Consistency**: No skipped/duplicate records when new conversations created during pagination
- **Real-time friendly**: Works well with polling for new conversations
- **Standard pattern**: Widely used in modern APIs (GraphQL Relay, Twitter, Facebook)

**Alternatives Considered**:
1. **Offset-based pagination**: Rejected - Poor performance at scale, inconsistent with concurrent inserts
2. **Keyset pagination**: Considered equivalent - Cursor-based is same pattern with better naming
3. **Load all conversations**: Rejected - Doesn't scale beyond ~50 conversations

**Implementation**:
```
GET /api/chat/conversations?limit=20&cursor=2025-12-19T10:00:00Z
```

Returns:
```json
{
  "conversations": [...],
  "nextCursor": "2025-12-18T09:30:00Z",
  "hasMore": true
}
```

### 8. Message Content Size Limit Enforcement

**Decision**: 10,000 character limit enforced at API layer with client-side validation

**Rationale**:
- **Industry standard**: Matches common chat applications (Slack: 40k, Discord: 2k, WhatsApp: 65k - 10k is reasonable middle ground)
- **Database efficiency**: Keeps row sizes manageable for PostgreSQL performance
- **UX**: Prevents accidental paste of huge text blobs
- **LLM compatibility**: Fits comfortably within AI model context windows

**Alternatives Considered**:
1. **Unlimited size**: Rejected - Database performance issues, poor UX for chat
2. **5,000 characters**: Rejected - Too restrictive for technical discussions with code snippets
3. **20,000 characters**: Rejected - Excessive for chat use case

**Implementation**:
- Pydantic validation: `content: str = Field(max_length=10000)`
- Frontend validation: Show character count when >9,000 characters
- API error response: 400 Bad Request with clear message when limit exceeded

### 9. Conversation Soft Delete Strategy

**Decision**: Soft delete with `deleted_at` timestamp column

**Rationale**:
- **Auditability**: Deleted conversations retained for compliance and debugging
- **Recovery**: Users can potentially recover accidentally deleted conversations
- **Analytics**: Understand conversation lifecycle and deletion patterns
- **Constitutional compliance**: Supports potential future GDPR "right to erasure" implementation

**Alternatives Considered**:
1. **Hard delete**: Rejected - Data loss, no audit trail
2. **Archive status flag**: Considered equivalent - `deleted_at` timestamp provides same functionality plus deletion time
3. **Separate deleted_conversations table**: Rejected - Unnecessary complexity

**Implementation**:
- Add `deleted_at: Optional[datetime]` to Conversation model
- Filter queries: `WHERE deleted_at IS NULL` (exclude deleted)
- Delete endpoint: `UPDATE conversations SET deleted_at = NOW() WHERE id = ?`
- Optional cleanup job: Hard delete conversations deleted >90 days ago (future enhancement)

### 10. CORS Configuration for Chatkit

**Decision**: Explicit CORS configuration allowing frontend origin with credentials

**Rationale**:
- **Security**: Prevents unauthorized origins from accessing chat API
- **Cookies/JWT**: Credentials mode enables JWT token transmission
- **Development workflow**: Different origins for dev (localhost:3000) and prod (vercel.app)

**Alternatives Considered**:
1. **Wildcard CORS**: Rejected - Security risk, doesn't work with credentials
2. **Same-origin only**: Rejected - Vercel deploys frontend and backend to different origins
3. **No CORS**: Rejected - Browser will block requests

**Implementation**:
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Development
        "https://your-app.vercel.app"  # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

## Summary of Decisions

| Area | Decision | Key Reason |
|------|----------|-----------|
| Real-time delivery | HTTP Polling (2-3s interval) | Simplicity, Vercel compatible |
| Conversation titles | Auto-generate from first message | UX, searchability |
| Markdown rendering | Chatkit built-in renderer | Zero config, security |
| Tool call storage | JSONB column in messages table | Flexibility, queryability |
| Chatkit integration | Custom backend adapter | Control, existing auth integration |
| Agent context loading | Full history query (LIMIT 50) | Stateless compliance, simplicity |
| Conversation pagination | Cursor-based (created_at) | Performance, consistency |
| Message size limit | 10,000 characters | Industry standard, performance |
| Conversation deletion | Soft delete (deleted_at) | Auditability, recovery |
| CORS configuration | Explicit origins with credentials | Security, JWT transmission |

## Dependencies and Versions

**Confirmed versions after research**:

### Backend
- `openai-agents-sdk==0.2.0` - Official OpenAI Agents SDK
- `mcp-python==0.1.5` - Model Context Protocol Python implementation
- Existing: `fastapi==0.95.2`, `sqlmodel==0.0.14`, `alembic==1.13.0`

### Frontend
- `@openai/chatkit==1.0.0` - OpenAI ChatKit React components
- Existing: `next==16.0.0`, `react==18.3.0`, `tailwindcss==3.4.0`

## Next Steps

With all technical decisions made, proceed to:
1. **Phase 1**: Generate data-model.md with database schemas
2. **Phase 1**: Generate API contracts (OpenAPI spec)
3. **Phase 1**: Generate quickstart.md with setup instructions
4. **Phase 1**: Update agent context files with new technologies
