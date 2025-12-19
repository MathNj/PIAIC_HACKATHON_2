# OpenAI Agents SDK Refactor

## Overview
Refactored `agent_runner/runner.py` to use the **proper openai-agents SDK pattern** instead of manually calling AsyncOpenAI chat completions.

## What Changed

### Before (Manual Pattern)
```python
from agents import AsyncOpenAI  # ❌ Wrong import

client = AsyncOpenAI(api_key=..., base_url=...)
response = await client.chat.completions.create(
    model="models/gemini-2.5-flash",
    messages=messages,
    tools=tool_schemas,
    tool_choice="auto"
)
# Manual tool calling loop...
```

**Problems:**
- Manual tool calling loop (error-prone)
- Not using the Agent/Runner abstraction
- Importing AsyncOpenAI from wrong package
- Converting MCP tools to OpenAI format manually

### After (openai-agents SDK Pattern)
```python
# ✅ Correct imports
from openai import AsyncOpenAI  # Standard OpenAI SDK
from agents import Agent, Runner, set_default_openai_client, function_tool

# 1. Configure custom Gemini client
gemini_client = AsyncOpenAI(
    api_key=settings.GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(gemini_client)

# 2. Wrap MCP tools with @function_tool decorator
@function_tool
def list_tasks_tool(status: Optional[str] = None):
    """List all tasks for the authenticated user."""
    return list_tasks(user_token=_user_token_context, status=status)

# 3. Create Agent with tools
agent = Agent(
    name="Task Management Assistant",
    instructions=AGENT_INSTRUCTIONS,
    model="gemini-2.5-flash",
    tools=[list_tasks_tool, create_task_tool, ...]
)

# 4. Run agent with Runner.run()
result = await Runner.run(agent, message)
```

**Benefits:**
- ✅ Uses official openai-agents SDK pattern
- ✅ Automatic tool calling loop (no manual management)
- ✅ Cleaner code with Agent/Runner abstraction
- ✅ Proper separation: OpenAI SDK for client, agents SDK for orchestration
- ✅ Function tools with @function_tool decorator
- ✅ Automatic tool discovery and execution

## Architecture

### 1. Client Configuration
```python
def _configure_gemini_client():
    """Configure AsyncOpenAI client for Gemini v1beta endpoint."""
    gemini_client = AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    set_default_openai_client(gemini_client)
```

- Uses `set_default_openai_client()` to configure Gemini as the backend
- Gemini v1beta supports OpenAI-compatible API
- Model name: `gemini-2.5-flash` (no `models/` prefix needed with SDK)

### 2. Tool Wrappers
```python
def _create_tool_wrappers(user_token: Optional[str], user_id: str):
    """Create @function_tool wrappers for MCP tools."""

    @function_tool
    def create_task_tool(title: str, description: Optional[str] = None, ...):
        """Create a new task."""
        return create_task(
            user_token=_user_token_context,
            title=title,
            description=description,
            ...
        )

    return [list_tasks_tool, create_task_tool, ...]
```

- Each MCP tool wrapped with `@function_tool` decorator
- Automatically injects `user_token` for authentication
- SDK handles tool schema generation and calling

### 3. Agent Creation & Execution
```python
agent = Agent(
    name="Task Management Assistant",
    instructions=AGENT_INSTRUCTIONS,
    model="gemini-2.5-flash",
    tools=[list_tasks_tool, create_task_tool, ...]
)

result = await Runner.run(agent, full_message)
```

- `Agent` encapsulates model, instructions, and tools
- `Runner.run()` handles entire conversation loop
- Automatic tool calling, error handling, and response generation

## Import Structure

### Correct Import Pattern
```python
# OpenAI SDK - for client configuration
from openai import AsyncOpenAI

# OpenAI Agents SDK - for Agent/Runner orchestration
from agents import Agent, Runner, set_default_openai_client, function_tool
```

### Why This Matters
- `openai` package: Standard OpenAI Python SDK (client only)
- `agents` package: OpenAI Agents SDK (orchestration framework)
- `AsyncOpenAI` comes from `openai`, NOT from `agents`
- `Agent`, `Runner`, etc. come from `agents` (openai-agents package)

## Gemini v1beta Integration

### Base URL
```python
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
```

- Gemini's OpenAI-compatible endpoint
- Uses v1beta API (not v1)
- Supports chat completions with tools/function calling

### Model Name
```python
model="gemini-2.5-flash"  # No "models/" prefix with SDK
```

- When using openai-agents SDK: `gemini-2.5-flash`
- When calling API directly: `models/gemini-2.5-flash`
- SDK handles the prefix automatically

## Dependencies

### requirements.txt
```txt
openai>=1.87.0           # OpenAI Python SDK (base client)
openai-agents>=0.0.19    # OpenAI Agents SDK (framework)
mcp>=1.9.4               # Model Context Protocol SDK
```

### Package Naming
- **PyPI package**: `openai-agents`
- **Import name**: `agents` (not `openai_agents`)
- Example: `pip install openai-agents` → `from agents import Agent`

## Testing

All 37 tests passing:
```bash
cd backend
python -m pytest tests/ -v
# ===== 37 passed, 137 warnings in 17.91s =====
```

Backend imports successfully:
```bash
python -c "from app.main import app; print('Success')"
python -c "from agent_runner.runner import run_chat_turn; print('Success')"
```

## References

- [OpenAI Agents SDK Docs](https://github.com/openai/openai-agents-python)
- [Gemini OpenAI Compatibility](https://ai.google.dev/gemini-api/docs/openai)
- [MCP Protocol](https://github.com/anthropics/mcp)

## Key Takeaways

1. **Use `set_default_openai_client()`** to configure custom LLM providers like Gemini
2. **Use `Agent` and `Runner`** from openai-agents SDK (not manual loops)
3. **Wrap tools with `@function_tool`** for automatic discovery and calling
4. **Import `AsyncOpenAI` from `openai`**, not from `agents`
5. **Gemini v1beta** supports OpenAI-compatible API with tool calling
6. **Model name**: `gemini-2.5-flash` (no prefix with SDK)

---

**Status**: ✅ Refactored and tested successfully
**Tests**: 37/37 passing
**Imports**: Working correctly
**Pattern**: Official openai-agents SDK pattern
