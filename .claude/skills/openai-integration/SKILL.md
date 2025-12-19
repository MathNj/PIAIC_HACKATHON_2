---
name: openai-integration
description: Integrate OpenAI API (GPT-4, GPT-3.5, embeddings) into applications with proper authentication, streaming, function calling, and error handling. Use when: (1) Implementing AI chat features with OpenAI models, (2) Adding text generation or completion endpoints, (3) Creating embeddings for semantic search, (4) Implementing function/tool calling for AI agents, (5) Setting up streaming responses for real-time chat, (6) Handling OpenAI API errors and rate limits, or (7) Optimizing token usage and costs. This skill provides production-ready patterns for FastAPI and Next.js OpenAI integrations.
---

# OpenAI Integration

This skill provides production-ready patterns for integrating OpenAI API into FastAPI backends and Next.js frontends.

## Quick Start Workflow

### Step 1: Install Dependencies

**Backend (Python)**:
```bash
pip install openai python-dotenv
```

**Frontend (TypeScript)**:
```bash
npm install openai
```

### Step 2: Configure API Key

Create `.env` file:
```bash
OPENAI_API_KEY=sk-...
```

**Never commit API keys to git!** Add `.env` to `.gitignore`.

### Step 3: Choose Integration Pattern

**Pattern 1: Simple Completion** (non-streaming)
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

**Pattern 2: Streaming Response** (real-time chat)
```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Pattern 3: Function Calling** (AI agents)
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools
)
```

### Step 4: Implement Backend Endpoint

See `references/fastapi-openai-patterns.md` for complete FastAPI integration examples.

### Step 5: Implement Frontend Client

See `references/nextjs-openai-patterns.md` for Next.js integration with streaming.

## Key Integration Patterns

### 1. Model Selection

**GPT-4 Turbo** (gpt-4-turbo-preview):
- Best quality, reasoning, and instruction following
- 128K context window
- $10/1M input tokens, $30/1M output tokens
- Use for: Complex reasoning, code generation, analysis

**GPT-4** (gpt-4):
- High quality, 8K context
- $30/1M input tokens, $60/1M output tokens
- Use for: Production chat, critical tasks

**GPT-3.5 Turbo** (gpt-3.5-turbo):
- Fast, affordable, 16K context
- $0.50/1M input tokens, $1.50/1M output tokens
- Use for: Simple tasks, high-volume requests

**Embeddings** (text-embedding-3-small):
- $0.02/1M tokens
- 1536 dimensions
- Use for: Semantic search, RAG systems

### 2. Streaming Responses

**FastAPI with Server-Sent Events (SSE)**:
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

async def generate():
    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield f"data: {chunk.choices[0].delta.content}\n\n"

@app.post("/chat/stream")
async def chat_stream():
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Next.js Client**:
```typescript
const response = await fetch('/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: 'Hello' })
});

const reader = response.body?.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = new TextDecoder().decode(value);
  console.log(text); // Process streamed chunks
}
```

### 3. Function Calling (Tool Use)

Define functions that the model can call:
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"]
                    }
                },
                "required": ["title"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Create a task to buy groceries"}],
    tools=tools
)

# Check if model wants to call a function
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    # Execute the function
    if function_name == "create_task":
        result = create_task(**function_args)

        # Send result back to model
        messages.append({
            "role": "function",
            "name": function_name,
            "content": json.dumps(result)
        })
```

### 4. Error Handling

```python
from openai import OpenAI, OpenAIError, RateLimitError, APIError

try:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
except RateLimitError:
    # Wait and retry with exponential backoff
    time.sleep(2 ** retry_count)
except APIError as e:
    # Handle API errors (500, 503, etc.)
    print(f"OpenAI API error: {e}")
except OpenAIError as e:
    # Handle all other OpenAI errors
    print(f"OpenAI error: {e}")
```

### 5. Rate Limiting and Retries

Use `tenacity` for automatic retries:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_openai(messages):
    return client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
```

### 6. Token Management

**Count tokens before sending**:
```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Check if within limits
tokens = count_tokens(user_message)
if tokens > 8000:
    # Truncate or split message
    pass
```

**Set max_tokens to control costs**:
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=500  # Limit response length
)
```

## Production Best Practices

### 1. Environment Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 2000
    openai_temperature: float = 0.7

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Client Initialization

**Singleton pattern**:
```python
from functools import lru_cache
from openai import OpenAI

@lru_cache()
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_api_key)
```

### 3. System Prompts

Store system prompts separately:
```python
SYSTEM_PROMPTS = {
    "todo_assistant": """You are a helpful task management assistant.
    You help users create, update, and organize their tasks.
    Always be concise and actionable.""",

    "code_reviewer": """You are a senior code reviewer.
    Analyze code for bugs, performance issues, and best practices.
    Provide specific, actionable feedback."""
}

messages = [
    {"role": "system", "content": SYSTEM_PROMPTS["todo_assistant"]},
    {"role": "user", "content": user_message}
]
```

### 4. Conversation History Management

**Truncate old messages to fit context window**:
```python
def truncate_messages(messages: list, max_tokens: int = 8000) -> list:
    total_tokens = sum(count_tokens(m["content"]) for m in messages)

    while total_tokens > max_tokens and len(messages) > 2:
        # Keep system message and remove oldest user/assistant messages
        messages.pop(1)
        total_tokens = sum(count_tokens(m["content"]) for m in messages)

    return messages
```

### 5. Logging and Monitoring

```python
import logging

logger = logging.getLogger(__name__)

def call_openai_with_logging(messages: list):
    logger.info(f"Calling OpenAI with {len(messages)} messages")

    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    duration = time.time() - start_time

    logger.info(f"OpenAI response in {duration:.2f}s, "
                f"tokens: {response.usage.total_tokens}")

    return response
```

## Common Patterns

### Pattern 1: Chat Endpoint with History

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Load conversation history from database
    messages = load_conversation_history(request.conversation_id)

    # Add new user message
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        assistant_message = response.choices[0].message.content

        # Save to database
        save_message(request.conversation_id, "user", request.message)
        save_message(request.conversation_id, "assistant", assistant_message)

        return {"message": assistant_message}

    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Pattern 2: Embeddings for Semantic Search

```python
def create_embeddings(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [data.embedding for data in response.data]

def semantic_search(query: str, documents: list[str], top_k: int = 5):
    # Create embeddings
    query_embedding = create_embeddings([query])[0]
    doc_embeddings = create_embeddings(documents)

    # Calculate cosine similarity
    from numpy import dot
    from numpy.linalg import norm

    similarities = [
        dot(query_embedding, doc_emb) / (norm(query_embedding) * norm(doc_emb))
        for doc_emb in doc_embeddings
    ]

    # Get top k results
    top_indices = sorted(range(len(similarities)),
                        key=lambda i: similarities[i],
                        reverse=True)[:top_k]

    return [documents[i] for i in top_indices]
```

### Pattern 3: Multi-Step Agent with Function Calling

```python
def run_agent(user_query: str):
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools."},
        {"role": "user", "content": user_query}
    ]

    tools = define_tools()  # Define available functions

    while True:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        # If no tool calls, return final answer
        if not message.tool_calls:
            return message.content

        # Execute tool calls
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Execute function
            result = execute_function(function_name, function_args)

            # Add function result to messages
            messages.append({
                "role": "function",
                "name": function_name,
                "content": json.dumps(result)
            })
```

## Cost Optimization

### 1. Use Cheaper Models When Possible

- Use GPT-3.5 for simple tasks (20x cheaper than GPT-4)
- Use GPT-4 only for complex reasoning
- Cache embeddings instead of regenerating

### 2. Reduce Token Usage

- Truncate old conversation history
- Use concise system prompts
- Set `max_tokens` to limit response length

### 3. Implement Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_completion(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content
```

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch

@patch('openai.OpenAI')
def test_chat_endpoint(mock_openai):
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices[0].message.content = "Hello!"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    # Test endpoint
    response = chat("Hi there")
    assert response == "Hello!"
```

### Integration Tests

Test with actual OpenAI API (use test API key):
```python
def test_openai_integration():
    client = OpenAI(api_key=os.getenv("OPENAI_TEST_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say 'test passed'"}]
    )

    assert "test passed" in response.choices[0].message.content.lower()
```

## Troubleshooting

**Issue**: Rate limit errors (429)
**Solution**: Implement exponential backoff with `tenacity`, reduce request rate

**Issue**: High costs
**Solution**: Use GPT-3.5 instead of GPT-4, set `max_tokens`, implement caching

**Issue**: Slow responses
**Solution**: Use streaming, reduce context window, use GPT-3.5 Turbo

**Issue**: Context length exceeded
**Solution**: Truncate conversation history, use smaller model with larger context

**Issue**: Function calling not working
**Solution**: Ensure tool schema matches OpenAI spec, check model supports function calling (GPT-4, GPT-3.5-turbo-1106+)

## Reference Files

- **FastAPI Patterns**: `references/fastapi-openai-patterns.md` - Complete backend integration guide
- **Next.js Patterns**: `references/nextjs-openai-patterns.md` - Frontend integration with streaming
- **Function Calling**: `references/function-calling-guide.md` - Advanced tool use patterns

## Security Checklist

- [ ] API key stored in `.env` (not committed to git)
- [ ] API key loaded from environment variables
- [ ] Rate limiting implemented
- [ ] Error handling for all API calls
- [ ] User input sanitized before sending to OpenAI
- [ ] Costs monitored and alerted
- [ ] Timeouts set for API calls
- [ ] Retry logic implemented with exponential backoff

## Production Deployment Checklist

- [ ] API key configured in production environment
- [ ] Logging and monitoring set up
- [ ] Rate limiting configured
- [ ] Error handling tested
- [ ] Streaming endpoints tested
- [ ] Function calling schemas validated
- [ ] Token usage optimized
- [ ] Costs estimated and budgeted
- [ ] Fallback strategies implemented
- [ ] Health checks added
