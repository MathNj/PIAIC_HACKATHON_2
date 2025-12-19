# OpenAI Function Calling Guide

Comprehensive guide for implementing function calling (tool use) with OpenAI API for building AI agents that can interact with external systems.

## Overview

Function calling allows GPT models to:
- Call external functions/APIs based on user queries
- Structured data extraction from natural language
- Multi-step reasoning with tool use
- Build autonomous agents

**Supported Models**:
- GPT-4 Turbo
- GPT-4
- GPT-3.5 Turbo (1106+)

## Basic Function Calling

### 1. Define Function Schema

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### 2. Call OpenAI with Tools

```python
from openai import OpenAI
import json

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What's the weather like in Boston?"}
    ],
    tools=tools,
    tool_choice="auto"  # Let model decide when to call functions
)

message = response.choices[0].message

# Check if model wants to call a function
if message.tool_calls:
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    print(f"Model wants to call: {function_name}")
    print(f"With arguments: {function_args}")
    # Output: Model wants to call: get_current_weather
    # With arguments: {'location': 'Boston', 'unit': 'fahrenheit'}
```

### 3. Execute Function and Send Result Back

```python
# Execute the function
def get_current_weather(location: str, unit: str = "fahrenheit"):
    # Call actual weather API
    return {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"]
    }

# Get function result
if function_name == "get_current_weather":
    function_result = get_current_weather(**function_args)

# Send result back to model
messages = [
    {"role": "user", "content": "What's the weather like in Boston?"},
    message,  # Assistant's message with tool call
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(function_result)
    }
]

# Get final response
final_response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

print(final_response.choices[0].message.content)
# Output: "The weather in Boston is currently sunny and windy with a temperature of 72°F."
```

## Advanced Patterns

### Pattern 1: Multi-Function Agent

```python
# Define multiple tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a new task in the todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"]
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks, optionally filtered by status",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"]
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "all"]
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "title": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"]
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"]
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"}
                },
                "required": ["task_id"]
            }
        }
    }
]

# Function implementations
def create_task(**kwargs):
    # Database insert logic
    return {"success": True, "task_id": 123}

def list_tasks(status="all", priority="all"):
    # Database query logic
    return {"tasks": [{"id": 1, "title": "Buy groceries"}]}

def update_task(task_id, **kwargs):
    # Database update logic
    return {"success": True}

def delete_task(task_id):
    # Database delete logic
    return {"success": True}

# Function dispatcher
function_map = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "delete_task": delete_task
}

def execute_function(name: str, arguments: dict):
    if name in function_map:
        return function_map[name](**arguments)
    return {"error": "Function not found"}
```

### Pattern 2: Multi-Step Agent Loop

```python
def run_agent(user_query: str, max_iterations: int = 5):
    """
    Run an agent that can call multiple functions in sequence
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful task management assistant with access to task management tools."
        },
        {"role": "user", "content": user_query}
    ]

    for iteration in range(max_iterations):
        print(f"\n--- Iteration {iteration + 1} ---")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # No more function calls - return final answer
        if not message.tool_calls:
            return message.content

        # Add assistant message to history
        messages.append(message)

        # Execute each function call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"Calling: {function_name}({function_args})")

            # Execute function
            function_result = execute_function(function_name, function_args)

            # Add function result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(function_result)
            })

    return "Agent exceeded maximum iterations"

# Example usage
result = run_agent(
    "Create a high priority task to finish the report by Friday, "
    "then show me all my high priority tasks"
)
print(f"\nFinal result: {result}")
```

### Pattern 3: Parallel Function Calling

```python
def run_parallel_agent(user_query: str):
    """
    Agent that can call multiple functions in parallel
    """
    messages = [
        {"role": "user", "content": user_query}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    if message.tool_calls:
        # Execute all function calls in parallel (using ThreadPoolExecutor)
        from concurrent.futures import ThreadPoolExecutor

        def execute_tool_call(tool_call):
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            result = execute_function(function_name, function_args)
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            }

        with ThreadPoolExecutor() as executor:
            function_messages = list(executor.map(
                execute_tool_call,
                message.tool_calls
            ))

        # Add assistant message and all function results
        messages.append(message)
        messages.extend(function_messages)

        # Get final response
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

        return final_response.choices[0].message.content

    return message.content

# Example: Agent calls multiple functions simultaneously
result = run_parallel_agent(
    "Show me my tasks and also check the weather in Boston"
)
```

### Pattern 4: Forced Function Calling

```python
# Force model to call a specific function
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "The user wants to create a task"}
    ],
    tools=tools,
    tool_choice={
        "type": "function",
        "function": {"name": "create_task"}
    }
)

# Model MUST call create_task function
```

### Pattern 5: Structured Data Extraction

```python
# Use function calling for structured data extraction
extraction_tool = [
    {
        "type": "function",
        "function": {
            "name": "extract_contact_info",
            "description": "Extract contact information from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "company": {"type": "string"},
                    "title": {"type": "string"}
                },
                "required": ["name"]
            }
        }
    }
]

text = """
John Smith is the CEO of Acme Corp.
You can reach him at john.smith@acme.com or call 555-0123.
"""

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": f"Extract contact information from: {text}"}
    ],
    tools=extraction_tool,
    tool_choice={"type": "function", "function": {"name": "extract_contact_info"}}
)

# Get extracted data
tool_call = response.choices[0].message.tool_calls[0]
contact_data = json.loads(tool_call.function.arguments)
print(contact_data)
# {
#     "name": "John Smith",
#     "email": "john.smith@acme.com",
#     "phone": "555-0123",
#     "company": "Acme Corp",
#     "title": "CEO"
# }
```

## FastAPI Integration

### Complete Agent Endpoint

```python
# app/routers/agent.py
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from pydantic import BaseModel
from openai import OpenAI
import json

router = APIRouter(prefix="/agent", tags=["agent"])
client = OpenAI()

class AgentRequest(BaseModel):
    query: str
    max_iterations: int = 5

class AgentResponse(BaseModel):
    result: str
    function_calls: list[dict]
    tokens_used: int

# Import tool definitions and function map
from app.services.tools import tools, execute_function

@router.post("/", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    session: Session = Depends(get_session)
):
    """Execute AI agent with function calling"""

    messages = [
        {
            "role": "system",
            "content": "You are a helpful task management assistant."
        },
        {"role": "user", "content": request.query}
    ]

    function_calls = []
    total_tokens = 0

    for _ in range(request.max_iterations):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools
        )

        total_tokens += response.usage.total_tokens
        message = response.choices[0].message

        if not message.tool_calls:
            return AgentResponse(
                result=message.content,
                function_calls=function_calls,
                tokens_used=total_tokens
            )

        messages.append(message)

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            # Log function call
            function_calls.append({
                "name": function_name,
                "arguments": function_args
            })

            # Execute with database session
            result = execute_function(
                function_name,
                function_args,
                session
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    raise HTTPException(
        status_code=500,
        detail="Agent exceeded maximum iterations"
    )
```

## TypeScript/Next.js Integration

### Function Calling in Next.js

```typescript
// app/api/agent/route.ts
import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

const openai = new OpenAI();

const tools: OpenAI.Chat.ChatCompletionTool[] = [
  {
    type: 'function',
    function: {
      name: 'create_task',
      description: 'Create a new task',
      parameters: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          priority: {
            type: 'string',
            enum: ['low', 'medium', 'high']
          }
        },
        required: ['title']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'list_tasks',
      description: 'List all tasks',
      parameters: {
        type: 'object',
        properties: {
          status: {
            type: 'string',
            enum: ['pending', 'completed', 'all']
          }
        }
      }
    }
  }
];

async function executeFunction(name: string, args: any) {
  const API_URL = process.env.API_URL || 'http://localhost:8000';

  if (name === 'create_task') {
    const res = await fetch(`${API_URL}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(args)
    });
    return res.json();
  }

  if (name === 'list_tasks') {
    const status = args.status || 'all';
    const res = await fetch(`${API_URL}/tasks?status=${status}`);
    return res.json();
  }

  return { error: 'Unknown function' };
}

export async function POST(request: NextRequest) {
  const { query } = await request.json();

  const messages: OpenAI.Chat.ChatCompletionMessageParam[] = [
    {
      role: 'system',
      content: 'You are a helpful task management assistant.'
    },
    { role: 'user', content: query }
  ];

  const maxIterations = 5;

  for (let i = 0; i < maxIterations; i++) {
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages,
      tools
    });

    const message = response.choices[0].message;

    if (!message.tool_calls) {
      return NextResponse.json({
        result: message.content
      });
    }

    messages.push(message);

    for (const toolCall of message.tool_calls) {
      const functionName = toolCall.function.name;
      const functionArgs = JSON.parse(toolCall.function.arguments);

      const result = await executeFunction(functionName, functionArgs);

      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        content: JSON.stringify(result)
      });
    }
  }

  return NextResponse.json(
    { error: 'Agent exceeded maximum iterations' },
    { status: 500 }
  );
}
```

## Best Practices

### 1. Clear Function Descriptions

```python
# ❌ BAD: Vague description
{
    "name": "do_something",
    "description": "Does something with tasks"
}

# ✅ GOOD: Clear, specific description
{
    "name": "create_task",
    "description": "Create a new task in the todo list with title, description, priority (low/medium/high), and optional due date in YYYY-MM-DD format"
}
```

### 2. Use Enums for Limited Options

```python
# ✅ GOOD: Use enums to constrain values
{
    "priority": {
        "type": "string",
        "enum": ["low", "medium", "high"],
        "description": "Task priority level"
    }
}
```

### 3. Mark Required Parameters

```python
{
    "parameters": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"}
        },
        "required": ["title"]  # Only title is required
    }
}
```

### 4. Handle Function Errors Gracefully

```python
def execute_function(name: str, arguments: dict):
    try:
        if name == "create_task":
            return create_task(**arguments)
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 5. Set Iteration Limits

```python
# Prevent infinite loops
max_iterations = 10
for i in range(max_iterations):
    # Agent loop
    pass
```

### 6. Log Function Calls

```python
import logging

logger = logging.getLogger(__name__)

def execute_function(name: str, arguments: dict):
    logger.info(f"Executing function: {name} with args: {arguments}")
    result = function_map[name](**arguments)
    logger.info(f"Function result: {result}")
    return result
```

## Common Patterns

### Pattern: Database CRUD Agent

```python
tools = [
    # Create
    {"function": {"name": "create_task", ...}},
    # Read
    {"function": {"name": "get_task", ...}},
    {"function": {"name": "list_tasks", ...}},
    # Update
    {"function": {"name": "update_task", ...}},
    # Delete
    {"function": {"name": "delete_task", ...}}
]
```

### Pattern: Search and Retrieval

```python
tools = [
    {
        "function": {
            "name": "search_documents",
            "description": "Search documents using semantic search",
            "parameters": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5}
            }
        }
    },
    {
        "function": {
            "name": "get_document",
            "description": "Retrieve full document by ID"
        }
    }
]
```

### Pattern: External API Integration

```python
tools = [
    {
        "function": {
            "name": "get_weather",
            "description": "Get current weather from external API"
        }
    },
    {
        "function": {
            "name": "send_email",
            "description": "Send email via SendGrid API"
        }
    },
    {
        "function": {
            "name": "create_calendar_event",
            "description": "Create event in Google Calendar"
        }
    }
]
```

## Troubleshooting

**Issue**: Model doesn't call functions
**Solution**: Improve function descriptions, use `tool_choice="required"`, check if query actually needs function

**Issue**: Wrong function arguments
**Solution**: Add clear parameter descriptions, use enums, add examples in description

**Issue**: Infinite loops
**Solution**: Set max_iterations, add exit conditions, improve system prompt

**Issue**: Function errors
**Solution**: Add try/except blocks, return error details to model, validate arguments

**Issue**: Too many function calls
**Solution**: Reduce max_iterations, improve system prompt to be more direct, use `tool_choice` strategically
