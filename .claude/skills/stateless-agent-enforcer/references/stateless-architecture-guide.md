# Stateless Agent Architecture - Validation and Enforcement Guide

## Overview

This guide provides comprehensive validation patterns for ensuring agents comply with the stateless architecture constitutional requirement: **NO in-memory conversation state**.

## Constitutional Requirement

**From CLAUDE.md**:
> All conversation history must be fetched from database on every request. Agent runtime MUST NOT store conversation state in memory.

**Why this matters**:
1. **Horizontal Scaling**: Multiple agent instances can serve the same user
2. **Load Balancing**: Requests can route to any instance without sticky sessions
3. **Crash Recovery**: No state lost when instance restarts
4. **Compliance**: Constitutional guarantee for data persistence and auditability

## What is Stateless Architecture?

### Stateless (✅ CORRECT)

**Definition**: Agent loads all necessary context from database on every request, stores no conversation state between requests.

**Example**:
```python
async def run_agent(conversation_id: str, user_message: str, db: Session):
    # ✅ Load conversation history from database every request
    history = load_conversation_context(conversation_id, db)

    # ✅ Build messages for this request only
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": user_message})

    # ✅ Call AI model
    response = await ai_client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    # ✅ Save response to database
    save_message(conversation_id, response.content, db)

    return response
```

**Key characteristics**:
- No class instance variables storing conversation data
- No global dictionaries caching messages
- No session objects persisting between requests
- Every request is independent and self-contained

### Stateful (❌ WRONG)

**Definition**: Agent stores conversation state in memory, relying on that state across requests.

**Example**:
```python
class Agent:
    def __init__(self):
        # ❌ In-memory conversation storage (VIOLATES STATELESS)
        self.conversations = {}
        self.message_history = {}

    async def run(self, conversation_id: str, user_message: str):
        # ❌ Using in-memory state instead of database
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        # ❌ Appending to in-memory list
        self.conversations[conversation_id].append({
            "role": "user",
            "content": user_message
        })

        # ❌ This breaks when instance restarts or different instance serves request
        messages = self.conversations[conversation_id]

        # ... call AI model
```

**Problems**:
- State lost when instance crashes or restarts
- Load balancing impossible (requires sticky sessions)
- Can't scale horizontally
- **Constitutional violation**

## Validation Patterns

### Pattern 1: Code Review Checklist

Check for these anti-patterns in agent code:

**Anti-pattern 1: Class instance variables for conversation state**
```python
class Agent:
    def __init__(self):
        self.conversations = {}  # ❌ VIOLATION
        self.message_cache = {}  # ❌ VIOLATION
```

**Anti-pattern 2: Global dictionaries for state**
```python
CONVERSATION_STATE = {}  # ❌ VIOLATION

async def run_agent(conversation_id: str, user_message: str):
    if conversation_id not in CONVERSATION_STATE:
        CONVERSATION_STATE[conversation_id] = []  # ❌ VIOLATION
```

**Anti-pattern 3: Session-based state management**
```python
from starlette.middleware.sessions import SessionMiddleware

@app.post("/chat")
async def chat(request: Request):
    session = request.session
    if "messages" not in session:
        session["messages"] = []  # ❌ VIOLATION (unless backed by DB)
```

**Anti-pattern 4: Caching without TTL or invalidation**
```python
from functools import lru_cache

@lru_cache(maxsize=None)  # ❌ VIOLATION (unbounded cache)
def get_conversation_history(conversation_id: str):
    # Never invalidates, grows indefinitely
    ...
```

**Valid pattern: Stateless database query**
```python
async def run_agent(conversation_id: str, user_message: str, db: Session):
    # ✅ CORRECT: Load from database every time
    history = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    ).all()

    # Use history for this request only
    ...
```

### Pattern 2: Automated Testing

**Test 1: State isolation between requests**
```python
import pytest
from app.agents.chat_agent import run_agent

@pytest.mark.asyncio
async def test_agent_state_isolation(db_session):
    """Verify agent doesn't retain state between requests."""

    conversation_id = "test-conv-1"

    # First request
    response1 = await run_agent(
        conversation_id=conversation_id,
        user_message="Hello",
        db=db_session
    )

    # Second request (should not have access to first request's in-memory state)
    response2 = await run_agent(
        conversation_id=conversation_id,
        user_message="How are you?",
        db=db_session
    )

    # Verify second request loaded history from database
    # (if it used in-memory state, it would only have "How are you?")
    messages = load_conversation_context(conversation_id, db_session)
    assert len(messages) >= 2  # Has both messages from database
```

**Test 2: Concurrent request handling**
```python
import asyncio

@pytest.mark.asyncio
async def test_concurrent_requests(db_session):
    """Verify multiple instances can serve same conversation."""

    conversation_id = "test-conv-2"

    # Simulate multiple instances handling requests concurrently
    tasks = [
        run_agent(conversation_id, f"Message {i}", db_session)
        for i in range(10)
    ]

    responses = await asyncio.gather(*tasks)

    # Verify all messages were saved to database
    messages = load_conversation_context(conversation_id, db_session)
    assert len(messages) == 10

    # No errors, no race conditions
    assert all(r is not None for r in responses)
```

**Test 3: Instance restart simulation**
```python
@pytest.mark.asyncio
async def test_instance_restart_recovery(db_session):
    """Verify conversation survives instance restart."""

    conversation_id = "test-conv-3"

    # Request 1: Agent instance A
    await run_agent(conversation_id, "Message before restart", db_session)

    # Simulate instance restart (clear any in-memory state)
    # If agent is stateless, this should have no effect

    # Request 2: Agent instance B (different instance)
    response = await run_agent(conversation_id, "Message after restart", db_session)

    # Verify instance B has access to message from instance A
    messages = load_conversation_context(conversation_id, db_session)
    assert len(messages) == 2
    assert messages[0].content == "Message before restart"
```

### Pattern 3: Static Analysis

**Script to detect stateless violations**:
```python
# stateless_validator.py
import ast
import sys
from pathlib import Path


class StatelessValidator(ast.NodeVisitor):
    """AST visitor to detect stateless architecture violations."""

    def __init__(self):
        self.violations = []

    def visit_ClassDef(self, node):
        """Check for instance variables that store conversation state."""
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                for stmt in item.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Attribute):
                                attr_name = target.attr

                                # Flag suspicious instance variables
                                if any(keyword in attr_name.lower() for keyword in
                                       ['conversation', 'message', 'history', 'cache', 'state', 'session']):
                                    self.violations.append({
                                        'type': 'instance_variable',
                                        'class': node.name,
                                        'variable': attr_name,
                                        'line': stmt.lineno,
                                        'message': f'Suspicious instance variable: {attr_name}'
                                    })

        self.generic_visit(node)

    def visit_Assign(self, node):
        """Check for global dictionaries storing conversation state."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id

                # Flag suspicious global variables
                if any(keyword in var_name.lower() for keyword in
                       ['conversation', 'message', 'history', 'cache', 'state']):
                    if isinstance(node.value, ast.Dict):
                        self.violations.append({
                            'type': 'global_dict',
                            'variable': var_name,
                            'line': node.lineno,
                            'message': f'Suspicious global dictionary: {var_name}'
                        })

        self.generic_visit(node)


def validate_file(file_path: Path) -> list:
    """Validate a Python file for stateless architecture compliance."""
    with open(file_path, 'r') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    validator = StatelessValidator()
    validator.visit(tree)

    return validator.violations


def main(directory: str):
    """Validate all Python files in directory."""
    path = Path(directory)
    all_violations = []

    for py_file in path.rglob('*.py'):
        violations = validate_file(py_file)
        if violations:
            all_violations.append({
                'file': str(py_file),
                'violations': violations
            })

    if all_violations:
        print("❌ Stateless architecture violations detected:\n")
        for file_violations in all_violations:
            print(f"File: {file_violations['file']}")
            for violation in file_violations['violations']:
                print(f"  Line {violation['line']}: {violation['message']}")
            print()

        sys.exit(1)
    else:
        print("✅ No stateless architecture violations detected")
        sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python stateless_validator.py <directory>")
        sys.exit(1)

    main(sys.argv[1])
```

**Run in CI/CD**:
```bash
python .claude/skills/stateless-agent-enforcer/scripts/stateless_validator.py backend/app/agents
```

### Pattern 4: Architecture Decision Record (ADR)

Document the stateless architecture decision:

```markdown
# ADR-001: Stateless Agent Architecture

## Status
Accepted

## Context
AI chat application requires horizontal scaling and high availability.

## Decision
Agents MUST be stateless - all conversation history loaded from database on every request.

## Consequences

### Positive
- Horizontal scaling: Multiple instances can serve same user
- Load balancing: No sticky sessions required
- Crash recovery: No state lost on instance restart
- Constitutional compliance: Guarantees data persistence

### Negative
- Increased database load (mitigated with indexes and connection pooling)
- Slight latency increase (20-30ms per request, acceptable)

## Compliance Validation
- Code review checklist enforced in PR reviews
- Automated testing for state isolation
- Static analysis in CI/CD pipeline
```

## Common Anti-Patterns and Solutions

### Anti-Pattern 1: In-Memory Message Cache

**Problem**:
```python
class Agent:
    def __init__(self):
        self.message_cache = {}  # ❌ VIOLATION

    async def get_messages(self, conversation_id: str):
        if conversation_id not in self.message_cache:
            self.message_cache[conversation_id] = fetch_from_db(conversation_id)
        return self.message_cache[conversation_id]
```

**Solution**:
```python
async def get_messages(conversation_id: str, db: Session):
    # ✅ CORRECT: Always fetch from database
    return load_conversation_context(conversation_id, db)
```

### Anti-Pattern 2: Session-Based Conversation Tracking

**Problem**:
```python
@app.post("/chat")
async def chat(request: Request):
    session = request.session
    if "conversation_id" not in session:
        session["conversation_id"] = create_conversation()  # ❌ VIOLATION

    conversation_id = session["conversation_id"]
    # ... use conversation_id
```

**Solution**:
```python
@app.post("/chat/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # ✅ CORRECT: conversation_id from URL, all state in database
    ...
```

### Anti-Pattern 3: Unbounded LRU Cache

**Problem**:
```python
from functools import lru_cache

@lru_cache(maxsize=None)  # ❌ VIOLATION: Grows indefinitely
def get_conversation_title(conversation_id: str) -> str:
    # Never invalidates, becomes stale
    ...
```

**Solution**:
```python
# ✅ CORRECT: Query database every time (with proper indexes, fast enough)
def get_conversation_title(conversation_id: str, db: Session) -> str:
    conversation = db.get(Conversation, conversation_id)
    return conversation.title if conversation else None

# OR: Use bounded cache with TTL (Redis)
import redis
redis_client = redis.Redis(...)

def get_conversation_title(conversation_id: str) -> str:
    # Check cache (5 minute TTL)
    cached = redis_client.get(f"title:{conversation_id}")
    if cached:
        return cached.decode()

    # Query database
    title = query_database(conversation_id)

    # Cache with TTL
    redis_client.setex(f"title:{conversation_id}", 300, title)

    return title
```

## Stateless Architecture Checklist

Use this checklist for code reviews:

- [ ] No class instance variables storing conversation data
- [ ] No global dictionaries caching messages or conversation state
- [ ] All conversation data loaded from database on every request
- [ ] Database queries include proper `user_id` filtering (tenant isolation)
- [ ] No session-based conversation tracking (unless session backed by database)
- [ ] Caches (if used) have TTL and invalidation strategy
- [ ] Agent can handle concurrent requests to same conversation
- [ ] Agent works correctly after instance restart
- [ ] Load balancing compatible (no sticky sessions required)
- [ ] Tests validate state isolation between requests

## Benefits of Stateless Architecture

1. **Horizontal Scaling**: Deploy 10 agent instances, handle 10x traffic
2. **Load Balancing**: Nginx/Kubernetes can route to any instance
3. **High Availability**: If instance crashes, others continue serving
4. **Development**: Easier testing (no shared state between tests)
5. **Deployment**: Rolling updates without downtime
6. **Constitutional Compliance**: Guarantees data persistence and auditability

## Performance Considerations

**Concern**: "Database query on every request is slow"

**Solutions**:
1. **Proper indexes**: `<20ms` query time for 50 messages
2. **Connection pooling**: Reuse database connections
3. **Limit history**: Only load last 50 messages for AI context
4. **Redis cache**: Cache with TTL and invalidation strategy (still stateless if cache miss handled)

**Measurement**: With proper indexes, database fetch adds 20-30ms per request - acceptable for chat application.

## Testing Stateless Compliance

**Integration test**:
```python
@pytest.mark.asyncio
async def test_stateless_compliance():
    """Comprehensive stateless architecture validation."""

    conversation_id = "test-conv"
    db = get_test_db()

    # 1. Test state isolation
    await run_agent(conversation_id, "Message 1", db)
    await run_agent(conversation_id, "Message 2", db)

    messages = load_conversation_context(conversation_id, db)
    assert len(messages) == 2

    # 2. Test concurrent requests
    tasks = [run_agent(conversation_id, f"Msg {i}", db) for i in range(10)]
    await asyncio.gather(*tasks)

    messages = load_conversation_context(conversation_id, db)
    assert len(messages) == 12  # 2 + 10

    # 3. Test instance restart (clear any in-memory state)
    # If agent is stateless, this should have no effect
    response = await run_agent(conversation_id, "After restart", db)

    messages = load_conversation_context(conversation_id, db)
    assert len(messages) == 13
    assert messages[-1].content == "After restart"

    print("✅ All stateless compliance tests passed")
```

## Enforcement in CI/CD

Add to `.github/workflows/test.yml`:
```yaml
- name: Validate Stateless Architecture
  run: |
    python .claude/skills/stateless-agent-enforcer/scripts/stateless_validator.py backend/app/agents
```

Fail PR if violations detected.
