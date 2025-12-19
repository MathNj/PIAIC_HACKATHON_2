---
name: stateless-agent-enforcer
description: Validate and enforce stateless agent architecture compliance with constitutional requirements. Use when: (1) Reviewing agent code for stateless violations, (2) Running CI/CD validation for in-memory state detection, (3) Testing agent code for horizontal scaling compatibility, (4) Creating compliance tests for instance restart scenarios, (5) Documenting stateless architecture decisions in ADRs, (6) Detecting anti-patterns like unbounded caches or global state, or (7) Ensuring constitutional compliance with "NO in-memory conversation state" requirement. This skill provides static analysis tools, test templates, code review checklists, and enforcement patterns for Phase III agent development.
---

# Stateless Agent Enforcer

This skill validates and enforces stateless agent architecture compliance with the constitutional requirement: **NO in-memory conversation state**.

## Constitutional Requirement

**From CLAUDE.md**:
> All conversation history must be fetched from database on every request. Agent runtime MUST NOT store conversation state in memory.

**Why this matters**:
- **Horizontal Scaling**: Multiple agent instances can serve the same user
- **Load Balancing**: Requests can route to any instance without sticky sessions
- **Crash Recovery**: No state lost when instance restarts
- **Compliance**: Constitutional guarantee for data persistence and auditability

## Quick Start Workflow

### Step 1: Review Architecture Guide

Read the comprehensive architecture guide:
```bash
.claude/skills/stateless-agent-enforcer/references/stateless-architecture-guide.md
```

This guide provides:
- Stateless vs stateful architecture definitions
- 7 common anti-patterns and solutions
- Automated validation patterns
- Testing strategies
- CI/CD integration

### Step 2: Run Static Analysis Validator

**Copy validator script** to project root:
```bash
cp .claude/skills/stateless-agent-enforcer/scripts/stateless_validator.py .
```

**Run validation**:
```bash
python stateless_validator.py backend/app/agents
```

**Expected output**:
```
Validating stateless architecture in: backend/app/agents

✅ No stateless architecture violations detected
   Scanned 5 Python files
```

**If violations detected**:
```
❌ Stateless architecture violations detected:

📄 File: backend/app/agents/chat_agent.py
  🔴 Line 15: Instance variable "message_cache" appears to store conversation state
  🟡 Line 42: Function "get_history" uses lru_cache without maxsize

Summary:
  Files scanned: 5
  Files with violations: 1
  High severity: 1
  Medium severity: 1
```

### Step 3: Add Compliance Tests

**Copy test template** to test directory:
```bash
cp .claude/skills/stateless-agent-enforcer/assets/tests/test_stateless_compliance.py backend/tests/
```

**Run tests**:
```bash
pytest backend/tests/test_stateless_compliance.py -v
```

**Tests included**:
- `test_state_isolation_between_requests()` - Verifies no in-memory state
- `test_concurrent_request_handling()` - Validates horizontal scaling
- `test_instance_restart_simulation()` - Confirms crash recovery
- `test_load_balancing_compatibility()` - Ensures any instance can serve any request
- `test_no_memory_leaks_from_state()` - Detects state accumulation

### Step 4: Use Code Review Checklist

**Copy checklist** to project docs:
```bash
cp .claude/skills/stateless-agent-enforcer/assets/checklist/code-review-checklist.md docs/
```

**Use in PR reviews**:
1. Open checklist during code review
2. Verify each item for agent code changes
3. Reject PRs that violate stateless architecture
4. Require fixes before merge

**Quick checklist**:
- [ ] No instance variables storing conversation state
- [ ] No global dictionaries caching messages
- [ ] Database session parameter in all agent functions
- [ ] Conversation history loaded from DB on every request
- [ ] Caches (if any) have TTL and invalidation
- [ ] Concurrent request handling tested
- [ ] Instance restart doesn't lose state

### Step 5: Integrate with CI/CD

**Add to GitHub Actions** `.github/workflows/test.yml`:
```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest

      - name: Validate Stateless Architecture
        run: |
          python stateless_validator.py backend/app/agents

      - name: Run Stateless Compliance Tests
        run: |
          pytest backend/tests/test_stateless_compliance.py -v
```

## What is Stateless Architecture?

### Stateless (✅ CORRECT)

Agent loads all context from database on every request, stores nothing between requests.

**Example**:
```python
async def run_agent(conversation_id: str, user_message: str, db: Session):
    # ✅ Load from database every request
    history = load_conversation_context(conversation_id, db)

    # ✅ Build messages for this request only
    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": user_message})

    # ✅ Call AI model
    response = await ai_client.chat.completions.create(messages=messages)

    # ✅ Save to database
    save_message(conversation_id, response.content, db)

    return response
```

### Stateful (❌ WRONG)

Agent stores conversation state in memory, relies on that state across requests.

**Example**:
```python
class Agent:
    def __init__(self):
        self.conversations = {}  # ❌ In-memory state (VIOLATES STATELESS)

    async def run(self, conversation_id: str, user_message: str):
        # ❌ Using in-memory cache instead of database
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        # ❌ This breaks on instance restart or load balancing
        messages = self.conversations[conversation_id]
        ...
```

## Common Anti-Patterns

### Anti-Pattern 1: Instance Variables for Conversation State

**Problem**:
```python
class Agent:
    def __init__(self):
        self.message_cache = {}  # ❌ VIOLATION
```

**Solution**:
```python
async def run_agent(conversation_id: str, db: Session):
    # ✅ CORRECT: Always fetch from database
    messages = load_conversation_context(conversation_id, db)
```

### Anti-Pattern 2: Global State Dictionaries

**Problem**:
```python
CONVERSATION_STATE = {}  # ❌ VIOLATION

async def run_agent(conversation_id: str, user_message: str):
    if conversation_id not in CONVERSATION_STATE:
        CONVERSATION_STATE[conversation_id] = []
```

**Solution**:
```python
# ✅ CORRECT: No global state, database query
async def run_agent(conversation_id: str, db: Session):
    messages = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(50)
    ).all()
```

### Anti-Pattern 3: Unbounded LRU Cache

**Problem**:
```python
from functools import lru_cache

@lru_cache(maxsize=None)  # ❌ VIOLATION: Grows indefinitely
def get_conversation_title(conversation_id: str):
    ...
```

**Solution**:
```python
# ✅ CORRECT: Direct database query with proper indexes
def get_conversation_title(conversation_id: str, db: Session):
    conversation = db.get(Conversation, conversation_id)
    return conversation.title if conversation else None
```

### Anti-Pattern 4: Session-Based Conversation Tracking

**Problem**:
```python
@app.post("/chat")
async def chat(request: Request):
    session = request.session
    conversation_id = session.get("conversation_id")  # ❌ VIOLATION
```

**Solution**:
```python
@app.post("/chat/{conversation_id}/messages")
async def send_message(
    conversation_id: str,  # ✅ CORRECT: Explicit URL parameter
    db: Session = Depends(get_session)
):
    ...
```

## Validation Tools

### 1. Static Analysis Validator

**Script**: `scripts/stateless_validator.py`

**Detects**:
- Class instance variables storing conversation state
- Global dictionaries caching messages
- Unbounded LRU caches (`@lru_cache(maxsize=None)`)

**Usage**:
```bash
python stateless_validator.py backend/app/agents
```

**Exit codes**:
- `0`: No violations
- `1`: Violations detected (fails CI/CD)

### 2. Compliance Test Suite

**File**: `assets/tests/test_stateless_compliance.py`

**Tests**:
- State isolation between requests
- Concurrent request handling (10 parallel requests)
- Instance restart simulation
- Load balancing compatibility
- Memory leak detection

**Usage**:
```bash
pytest backend/tests/test_stateless_compliance.py -v
```

### 3. Code Review Checklist

**File**: `assets/checklist/code-review-checklist.md`

**Sections**:
- Instance variables check
- Global state check
- Database query pattern check
- Session-based state check
- Caching strategy check
- Function signature check
- Concurrency safety check
- Testing coverage check
- Documentation check
- Performance check

**Usage**: Use in PR reviews for agent code changes

## Benefits of Stateless Architecture

1. **Horizontal Scaling**: Deploy 10 instances, handle 10x traffic
2. **Load Balancing**: Nginx/Kubernetes routes to any instance
3. **High Availability**: Instance crashes don't lose data
4. **Development**: Easier testing (no shared state)
5. **Deployment**: Rolling updates without downtime
6. **Constitutional Compliance**: Guarantees persistence

## Performance Considerations

**Concern**: "Database query on every request is slow"

**Solutions**:
1. **Proper indexes**: `<20ms` query time for 50 messages
2. **Connection pooling**: Reuse database connections
3. **Limit history**: Only load last 50 messages
4. **Redis cache**: Cache with TTL (still stateless if cache miss handled)

**Measurement**: With proper indexes, database fetch adds 20-30ms per request - acceptable for chat.

## CI/CD Integration

**GitHub Actions example**:
```yaml
- name: Validate Stateless Architecture
  run: python stateless_validator.py backend/app/agents

- name: Run Compliance Tests
  run: pytest backend/tests/test_stateless_compliance.py -v
```

**Fail PR if**:
- Static analysis detects violations
- Compliance tests fail

## Documentation Requirements

**Required in code**:
```python
async def run_agent(conversation_id: str, user_message: str, db: Session):
    """
    Run stateless AI agent.

    STATELESS REQUIREMENT: Loads full conversation history from database
    on every request. This enables horizontal scaling and load balancing.

    Args:
        conversation_id: UUID of conversation
        user_message: User's message
        db: Database session for loading history

    Returns:
        Agent response
    """
    # Load history from database (stateless architecture)
    history = load_conversation_context(conversation_id, db, limit=50)
    ...
```

**Required in ADR**:
Document stateless architecture decision with rationale and compliance validation.

## Quick Decision Tree

```
Does code store conversation data in instance variables or global dicts?
├─ YES → ❌ REJECT (violates stateless)
└─ NO → Continue

Does code load conversation history from database on every request?
├─ NO → ❌ REJECT (violates stateless)
└─ YES → Continue

Does code use unbounded caches without TTL?
├─ YES → ❌ REJECT (unbounded state)
└─ NO → Continue

Can code handle concurrent requests to same conversation?
├─ NO → ❌ REJECT (not scalable)
└─ YES → Continue

Does code work correctly after instance restart?
├─ NO → ❌ REJECT (relies on memory)
└─ YES → ✅ APPROVE
```

## Reference Files

- **Architecture Guide**: `references/stateless-architecture-guide.md` - Complete validation patterns
- **Validator Script**: `scripts/stateless_validator.py` - Static analysis tool
- **Compliance Tests**: `assets/tests/test_stateless_compliance.py` - Test templates
- **Review Checklist**: `assets/checklist/code-review-checklist.md` - PR review guide
