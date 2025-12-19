# Stateless Architecture Code Review Checklist

Use this checklist when reviewing agent code to ensure stateless architecture compliance.

## 1. Instance Variables Check

### ❌ Anti-Patterns to Reject

```python
class Agent:
    def __init__(self):
        self.conversations = {}           # ❌ REJECT
        self.message_history = {}         # ❌ REJECT
        self.conversation_cache = {}      # ❌ REJECT
        self.state = {}                   # ❌ REJECT
```

### ✅ Acceptable Patterns

```python
class Agent:
    def __init__(self, db_engine):
        self.db_engine = db_engine        # ✅ OK: Database connection (no state)
        self.model_name = "gpt-4"         # ✅ OK: Configuration (immutable)
        self.max_tokens = 8000            # ✅ OK: Configuration (immutable)
```

**Review Questions:**
- [ ] Does the agent class have instance variables for conversations/messages/history?
- [ ] Are instance variables immutable configuration only?
- [ ] Is there any mutable state stored in instance variables?

---

## 2. Global State Check

### ❌ Anti-Patterns to Reject

```python
CONVERSATION_STATE = {}               # ❌ REJECT
MESSAGE_CACHE = defaultdict(list)     # ❌ REJECT
ACTIVE_CONVERSATIONS = set()          # ❌ REJECT
```

### ✅ Acceptable Patterns

```python
DATABASE_URL = os.getenv("DATABASE_URL")  # ✅ OK: Configuration
MAX_HISTORY_MESSAGES = 50                 # ✅ OK: Constant
MODEL_CONFIG = {                          # ✅ OK: Immutable config
    "model": "gpt-4",
    "temperature": 0.7
}
```

**Review Questions:**
- [ ] Are there global dictionaries/lists storing conversation data?
- [ ] Are global variables immutable configuration/constants only?
- [ ] Is there any mutable global state?

---

## 3. Database Query Pattern Check

### ❌ Anti-Patterns to Reject

```python
def run_agent(conversation_id: str, user_message: str):
    # ❌ REJECT: No database query, must be using in-memory state
    if conversation_id not in self.cache:
        self.cache[conversation_id] = []

    messages = self.cache[conversation_id]
    # ...
```

### ✅ Required Pattern

```python
def run_agent(conversation_id: str, user_message: str, db: Session):
    # ✅ REQUIRED: Load from database every request
    history = db.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    ).all()

    # Use history for this request only
    # ...
```

**Review Questions:**
- [ ] Does the function accept a database session parameter?
- [ ] Is conversation history loaded from database on every call?
- [ ] Are there any "if not in cache" checks for conversation data?

---

## 4. Session-Based State Check

### ❌ Anti-Patterns to Reject

```python
@app.post("/chat")
async def chat(request: Request):
    session = request.session

    # ❌ REJECT: Storing conversation_id in session (unless session is DB-backed)
    if "conversation_id" not in session:
        session["conversation_id"] = create_conversation()

    conversation_id = session["conversation_id"]
    # ...
```

### ✅ Acceptable Patterns

```python
@app.post("/chat/{conversation_id}/messages")
async def send_message(
    conversation_id: str,              # ✅ OK: Explicit URL parameter
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # ✅ OK: conversation_id from URL, state in database
    ...
```

**Review Questions:**
- [ ] Is conversation_id passed explicitly in URL/body, not from session?
- [ ] If session is used, is it only for authentication (JWT token)?
- [ ] Is all conversation state stored in database, not session?

---

## 5. Caching Strategy Check

### ❌ Anti-Patterns to Reject

```python
from functools import lru_cache

@lru_cache(maxsize=None)              # ❌ REJECT: Unbounded cache
def get_conversation_title(conversation_id: str) -> str:
    # Never invalidates, grows indefinitely
    ...

# ❌ REJECT: No TTL or invalidation
TITLE_CACHE = {}
def get_title(conversation_id: str) -> str:
    if conversation_id not in TITLE_CACHE:
        TITLE_CACHE[conversation_id] = query_db(conversation_id)
    return TITLE_CACHE[conversation_id]
```

### ✅ Acceptable Patterns

```python
# ✅ OK: Direct database query (fast with indexes)
def get_conversation_title(conversation_id: str, db: Session) -> str:
    conversation = db.get(Conversation, conversation_id)
    return conversation.title if conversation else None

# ✅ OK: Bounded cache with TTL (Redis)
import redis
redis_client = redis.Redis(...)

def get_conversation_title(conversation_id: str) -> str:
    # Check cache (5 minute TTL)
    cached = redis_client.get(f"title:{conversation_id}")
    if cached:
        return cached.decode()

    # Query database on cache miss
    title = query_database(conversation_id)

    # Cache with TTL
    redis_client.setex(f"title:{conversation_id}", 300, title)

    return title
```

**Review Questions:**
- [ ] Are caches bounded (have maxsize)?
- [ ] Do caches have TTL and invalidation strategy?
- [ ] Is direct database query with proper indexes used instead of caching?

---

## 6. Function Signature Check

### ❌ Anti-Patterns to Reject

```python
# ❌ REJECT: No database session parameter
async def run_agent(conversation_id: str, user_message: str):
    # Must be using in-memory state if no DB access
    ...

# ❌ REJECT: Agent method without database session
class Agent:
    async def chat(self, conversation_id: str, message: str):
        # How does it access conversation history without DB?
        ...
```

### ✅ Required Pattern

```python
# ✅ REQUIRED: Database session parameter
async def run_agent(
    conversation_id: str,
    user_message: str,
    user_id: str,
    db: Session              # Database session for stateless access
):
    history = load_conversation_context(conversation_id, db)
    # ...

# ✅ OK: Agent method with database session
class Agent:
    async def chat(
        self,
        conversation_id: str,
        message: str,
        db: Session          # Database session injected
    ):
        history = self.load_history(conversation_id, db)
        # ...
```

**Review Questions:**
- [ ] Do agent functions accept a database session parameter?
- [ ] Is the database session used to load conversation history?
- [ ] Are there functions that should access conversation data but don't have DB param?

---

## 7. Concurrency Safety Check

### ❌ Anti-Patterns to Reject

```python
# ❌ REJECT: Shared mutable state without locks
class Agent:
    def __init__(self):
        self.message_count = {}       # Race condition risk

    async def add_message(self, conversation_id: str):
        # ❌ Not thread-safe
        if conversation_id not in self.message_count:
            self.message_count[conversation_id] = 0
        self.message_count[conversation_id] += 1
```

### ✅ Acceptable Pattern

```python
# ✅ OK: No shared mutable state
async def add_message(conversation_id: str, db: Session):
    # Database handles concurrency
    message = Message(conversation_id=conversation_id, ...)
    db.add(message)
    db.commit()

    # Query database for count (always accurate)
    count = db.exec(
        select(func.count(Message.id))
        .where(Message.conversation_id == conversation_id)
    ).one()
```

**Review Questions:**
- [ ] Is there shared mutable state accessed concurrently?
- [ ] Are locks/synchronization primitives used (suggests stateful design)?
- [ ] Is all state in database (which handles concurrency correctly)?

---

## 8. Testing Coverage Check

**Required Tests:**
- [ ] Test: State isolation between requests
- [ ] Test: Concurrent request handling
- [ ] Test: Instance restart simulation
- [ ] Test: Load balancing compatibility
- [ ] Test: No memory leaks from accumulated state

**Recommended Test File:**
```
backend/tests/test_stateless_compliance.py
```

---

## 9. Documentation Check

**Required Documentation:**
- [ ] Function docstring mentions "stateless" or "loads from database"
- [ ] README explains stateless architecture
- [ ] ADR documents stateless architecture decision
- [ ] Code comments explain why database is queried on every request

**Example:**
```python
async def run_agent(conversation_id: str, user_message: str, db: Session):
    """
    Run stateless AI agent on user message.

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

---

## 10. Performance Check

**Database Query Optimization:**
- [ ] Proper indexes exist for conversation queries
- [ ] Connection pooling configured
- [ ] Query limits used (e.g., LIMIT 50 for message history)
- [ ] EXPLAIN ANALYZE verifies index usage

**Acceptable Performance:**
- Database query time: <20ms for 50 messages
- End-to-end request time: <500ms (including AI call)

---

## Summary Checklist

Use this quick checklist for final approval:

- [ ] ✅ No instance variables storing conversation state
- [ ] ✅ No global dictionaries caching messages
- [ ] ✅ Database session parameter in all agent functions
- [ ] ✅ Conversation history loaded from database on every request
- [ ] ✅ No session-based conversation tracking (except DB-backed auth)
- [ ] ✅ Caches (if any) have TTL and invalidation strategy
- [ ] ✅ Concurrent request handling tested
- [ ] ✅ Instance restart doesn't lose state (all in DB)
- [ ] ✅ Documentation mentions stateless architecture
- [ ] ✅ Performance acceptable (<20ms DB queries with proper indexes)

---

## Quick Decision Tree

```
Does code store conversation data in instance variables or global dicts?
├─ YES → ❌ REJECT (violates stateless architecture)
└─ NO → Continue

Does code load conversation history from database on every request?
├─ NO → ❌ REJECT (violates stateless architecture)
└─ YES → Continue

Does code use unbounded caches without TTL?
├─ YES → ❌ REJECT (unbounded state accumulation)
└─ NO → Continue

Can code handle concurrent requests to same conversation?
├─ NO → ❌ REJECT (not horizontally scalable)
└─ YES → Continue

Does code work correctly after instance restart?
├─ NO → ❌ REJECT (relies on in-memory state)
└─ YES → ✅ APPROVE
```

---

## Common Mistakes and Fixes

### Mistake 1: "Performance optimization" with in-memory cache

**Wrong:**
```python
class Agent:
    def __init__(self):
        self.cache = {}  # "To avoid repeated DB queries"
```

**Right:**
```python
# Use proper database indexes instead
# With indexes, queries are fast enough (<20ms)
```

### Mistake 2: "User session" for conversation tracking

**Wrong:**
```python
session["current_conversation"] = conversation_id
```

**Right:**
```python
# Pass conversation_id explicitly in API call
@router.post("/chat/{conversation_id}/messages")
```

### Mistake 3: "Singleton pattern" for agent

**Wrong:**
```python
# Single agent instance shared across requests
agent = Agent()

@app.post("/chat")
async def chat(request):
    return await agent.run(request.conversation_id, request.message)
```

**Right:**
```python
# Stateless function, no shared instance
@app.post("/chat/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    data: MessageCreate,
    db: Session = Depends(get_session)
):
    return await run_agent(conversation_id, data.content, db)
```

---

**Last Updated:** 2024-12-19
**Review this checklist for every agent code change**
