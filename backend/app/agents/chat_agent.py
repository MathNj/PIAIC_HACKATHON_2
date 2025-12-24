"""
Stateless AI chat agent with OpenAI integration and MCP tools.

This module implements a stateless AI agent that accepts conversation history
as a parameter (constitutional requirement for horizontal scaling).

CONSTITUTIONAL REQUIREMENT:
- Agent interacts with tasks ONLY via MCP tools (mcp_list_tasks, mcp_create_task, etc.)
- Uses official FastMCP SDK from mcp package (>= 1.9.4)
- NO direct API calls from agent - all task operations go through MCP

Functions:
    - run_agent: Execute stateless AI agent with conversation history and MCP tools
    - _execute_tool: Execute a single MCP tool (internal)
    - _convert_mcp_tools_to_openai_format: Convert FastMCP tools to OpenAI function format
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
import json
import time
import logging
import os

from openai import OpenAI, OpenAIError
from jose import jwt

# Import MCP server and tool execution (official FastMCP SDK)
from app_mcp.server import get_mcp_server, execute_mcp_tool
from app.config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# Helper: Convert FastMCP TextContent to serializable dict
# ============================================================================

def convert_textcontent_to_dict(result: Any) -> Any:
    """
    Convert FastMCP TextContent object to JSON-serializable dict/list/str.

    FastMCP's call_tool returns TextContent objects with structure:
    TextContent(type="text", text='{"key": "value"}')

    This function extracts the .text attribute and parses it as JSON.

    Args:
        result: Result from execute_mcp_tool (could be TextContent or dict)

    Returns:
        Parsed JSON data (dict/list/str) that's JSON-serializable
    """
    # Handle None
    if result is None:
        logger.warning(f"[TextContent Converter] Received None, returning empty dict")
        return {}

    # Log what we received for debugging
    result_type = type(result).__name__
    logger.info(f"[TextContent Converter] Received type: {result_type}")

    # AGGRESSIVE: Check for TextContent by type name OR by having .text attribute
    is_textcontent = result_type == 'TextContent' or (hasattr(result, 'text') and hasattr(result, 'type'))

    if is_textcontent:
        logger.info(f"[TextContent Converter] Detected TextContent object")
        try:
            # Extract text content from TextContent object
            text_content = result.text if hasattr(result, 'text') else str(result)
            logger.info(f"[TextContent Converter] Extracted text (first 500 chars): {str(text_content)[:500]}")

            # Try to parse as JSON
            try:
                parsed = json.loads(text_content)
                parsed_type = type(parsed).__name__
                logger.info(f"[TextContent Converter] ✓ Successfully parsed as {parsed_type}")
                return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"[TextContent Converter] Not JSON, returning as plain text: {e}")
                # If not valid JSON, return the text as-is (it's a string)
                return text_content
        except Exception as e:
            logger.error(f"[TextContent Converter] ✗ Extraction failed: {e}", exc_info=True)
            # Last resort: force to string
            try:
                return str(result.text) if hasattr(result, 'text') else str(result)
            except:
                return {"error": "TextContent conversion failed completely"}

    # If it's a list, convert each item
    if isinstance(result, list):
        logger.info(f"[TextContent Converter] Converting list with {len(result)} items")
        return [convert_textcontent_to_dict(item) for item in result]

    # If it's a dict, return as-is (already serializable)
    if isinstance(result, dict):
        logger.info(f"[TextContent Converter] Already a dict, returning as-is")
        return result

    # If it's a primitive (str, int, float, bool), return as-is
    if isinstance(result, (str, int, float, bool)):
        logger.info(f"[TextContent Converter] Primitive type ({result_type}), returning as-is")
        return result

    # Unknown type - try to make it serializable
    logger.warning(f"[TextContent Converter] Unknown type {result_type}, attempting conversion")
    if hasattr(result, 'model_dump'):
        logger.info(f"[TextContent Converter] Has model_dump, using it")
        return result.model_dump()
    elif hasattr(result, '__dict__'):
        logger.info(f"[TextContent Converter] Has __dict__, using it")
        return result.__dict__
    else:
        logger.warning(f"[TextContent Converter] Converting to string as last resort")
        return str(result)


# ============================================================================
# OpenAI Client and JWT Token Generation
# ============================================================================

def get_openai_client() -> OpenAI:
    """
    Get OpenAI-compatible client instance (supports OpenAI, Groq, etc.).

    Supports custom base URLs via OPENAI_BASE_URL environment variable.
    This allows using Groq or other OpenAI-compatible APIs.

    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable is required for AI agent"
        )

    base_url = os.getenv("OPENAI_BASE_URL")

    if base_url:
        logger.info(f"Using custom OpenAI base URL: {base_url}")
        return OpenAI(api_key=api_key, base_url=base_url)
    else:
        return OpenAI(api_key=api_key)


def _generate_jwt_token(user_id: UUID) -> str:
    """
    Generate JWT token for MCP tool authentication.

    MCP tools require JWT authentication with user_id in the token payload.
    This function generates a short-lived token for tool execution context.

    Args:
        user_id: User UUID to encode in token

    Returns:
        JWT token string

    Example:
        token = _generate_jwt_token(user_id)
        # Token payload: {"user_id": "550e8400-...", "exp": 1735...}
    """
    payload = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=5),  # 5-minute expiry for tool execution
        "iat": datetime.utcnow(),
        "purpose": "mcp_tool_execution"
    }

    token = jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm="HS256"
    )

    return token


def _convert_mcp_tools_to_openai_format() -> List[Dict[str, Any]]:
    """
    Convert FastMCP tool schemas to OpenAI function calling format.

    FastMCP uses MCP protocol schemas, but OpenAI requires a different format.
    This function bridges the two formats.

    Returns:
        List of OpenAI-compatible tool definitions

    Example:
        [
            {
                "type": "function",
                "function": {
                    "name": "mcp_list_tasks",
                    "description": "List all tasks for the authenticated user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["all", "pending", "completed"]}
                        },
                        "required": []  # user_token is injected, not required from agent
                    }
                }
            },
            ...
        ]

    NOTE: user_token parameter is REMOVED from OpenAI schema since it's
    injected automatically during tool execution.
    """
    mcp_server = get_mcp_server()
    mcp_tools_list = mcp_server.list_tools()

    openai_tools = []

    # Manually define tool schemas in OpenAI format (user_token parameter excluded)
    # These mirror the MCP tools but are compatible with OpenAI function calling
    tool_definitions = [
        {
            "type": "function",
            "function": {
                "name": "mcp_list_tasks",
                "description": "List all tasks for the authenticated user with optional status filtering (all, pending, completed)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by completion status (default: all)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_create_task",
                "description": "Create a new task from natural language description. Supports priority inference from keywords (URGENT→high, maybe→low) and natural language due dates (tomorrow, next week, etc.)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description (max 1000 characters)"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high"],
                            "description": "Task priority level. If omitted, will be inferred from description keywords."
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date - supports natural language (tomorrow, next week, in 3 days) or ISO format (2025-12-25)"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_update_task",
                "description": "Update an existing task's properties (title, description, priority, due_date, completed status). IMPORTANT: You must first call mcp_list_tasks to get the task's numeric ID before calling this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "description": "REQUIRED: Numeric ID of the task to update (get this from mcp_list_tasks first, e.g., 102)",
                            "anyOf": [
                                {"type": "integer"},
                                {"type": "string", "pattern": "^[0-9]+$"}
                            ]
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional new title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "normal", "high"],
                            "description": "Optional new priority"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Optional new due date (ISO 8601 format)"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Optional new completion status"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_delete_task",
                "description": "Permanently delete a task by ID. IMPORTANT: You must first call mcp_list_tasks to get the task's numeric ID before calling this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "description": "REQUIRED: Numeric ID of the task to delete (get this from mcp_list_tasks first, e.g., 102)",
                            "anyOf": [
                                {"type": "integer"},
                                {"type": "string", "pattern": "^[0-9]+$"}
                            ]
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_toggle_task_completion",
                "description": "Toggle task completion status (mark as complete if pending, or pending if complete). IMPORTANT: You must first call mcp_list_tasks to get the task's numeric ID before calling this function.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "description": "REQUIRED: Numeric ID of the task to toggle (get this from mcp_list_tasks first, e.g., 79)",
                            "anyOf": [
                                {"type": "integer"},
                                {"type": "string", "pattern": "^[0-9]+$"}
                            ]
                        }
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_get_task_summary",
                "description": "Get task statistics and summary with counts by status, priority, and timeframe (total, completed, pending, high_priority, overdue, due_today, due_this_week)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timeframe": {
                            "type": "string",
                            "enum": ["all", "today", "week", "overdue"],
                            "description": "Filter timeframe for summary (default: all)"
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "mcp_suggest_task_prioritization",
                "description": "Get AI-powered task prioritization suggestions based on urgency, due dates, and priority levels. Returns tasks sorted by computed priority score with reasoning.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]

    logger.info(f"Converted {len(tool_definitions)} MCP tools to OpenAI function calling format")

    return tool_definitions


async def run_agent(
    user_id: UUID,
    message: str,
    history: List[Dict[str, str]],
    mcp_tools: Optional[List[Dict[str, Any]]] = None,
    max_tool_calls: int = 10,
    model: str = None,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute stateless AI agent with conversation history and MCP tools.

    CONSTITUTIONAL REQUIREMENT:
    - No class-level state. Accept history parameter.
    - Agent must be restartable without losing context.
    - Agent interacts with tasks ONLY via MCP tools (official FastMCP SDK)

    Args:
        user_id: Current user ID (for MCP tool authentication and tenant isolation)
        message: User's new message to process
        history: Conversation history from database (list of {"role": str, "content": str})
        mcp_tools: DEPRECATED - MCP tools are auto-loaded from FastMCP server
        max_tool_calls: Maximum tool execution iterations (default: 10)
        model: OpenAI model to use (default: gpt-4)
        system_prompt: Optional system prompt override

    Returns:
        {
            "response": str,  # AI assistant response text
            "tool_calls": [   # Audit trail of tool executions
                {
                    "tool_name": str,
                    "arguments": dict,
                    "result": dict,
                    "timestamp": str,  # ISO 8601
                    "duration_ms": int,
                    "status": "success" | "error"
                }
            ],
            "model": str,  # Model used
            "tokens_used": int,  # Total tokens consumed
            "finish_reason": str  # "stop", "length", "tool_calls", etc.
        }

    Raises:
        OpenAIError: If OpenAI API call fails
        ValueError: If OPENAI_API_KEY not set

    Example:
        >>> history = await load_conversation_context(conv_id, session)
        >>> result = await run_agent(
        ...     user_id=user.id,
        ...     message="Create a task for groceries",
        ...     history=history
        ... )
        >>> print(result["response"])
        "I've created a task for groceries with ID 123"
    """
    start_time = time.time()

    # Use model from environment variable if not provided
    if model is None:
        model = os.getenv("OPENAI_MODEL", "gpt-4")

    logger.info(
        f"Agent execution started with MCP tools",
        extra={
            "user_id": str(user_id),
            "message_length": len(message),
            "history_length": len(history),
            "model": model
        }
    )

    # Initialize OpenAI client
    try:
        client = get_openai_client()
    except ValueError as e:
        logger.error(f"OpenAI client initialization failed: {e}")
        raise

    # Generate JWT token for MCP tool authentication
    # This token is injected into all tool calls for user authentication
    user_token = _generate_jwt_token(user_id)
    logger.debug(f"Generated JWT token for MCP tool execution")

    # Load MCP tools from FastMCP server and convert to OpenAI format
    openai_tools = _convert_mcp_tools_to_openai_format()
    logger.info(f"Loaded {len(openai_tools)} MCP tools for agent")

    # Build messages array for OpenAI
    messages = []

    # Add system prompt (if not already in history)
    if system_prompt or (not history or history[0].get("role") != "system"):
        default_system_prompt = (
            "You are a helpful AI assistant for a task management application. "
            "You have access to tools that let you create, update, list, delete, and manage tasks. "
            "\n\n🌍 MULTILINGUAL REQUIREMENT:\n"
            "You are a POLYGLOT assistant supporting English, Urdu (اردو), French (Français), and Arabic (العربية).\n"
            "- ALWAYS detect the language of the user's message\n"
            "- ALWAYS respond in the SAME language the user used\n"
            "- If user writes in Urdu, respond in Urdu. If French, respond in French. If Arabic, respond in Arabic.\n"
            "- NEVER reply in English if the user asks in another language (unless they explicitly request English)\n"
            "- Maintain the same language throughout the conversation unless the user switches\n"
            "\n\nCRITICAL: Task IDs are INTEGERS, not strings!\n"
            "\nWORKFLOW EXAMPLES:\n"
            "User: 'Delete the test task'\n"
            "1. Call mcp_list_tasks() → Get [{\"id\": 102, \"title\": \"test\"}, ...]\n"
            "2. Call mcp_delete_task(task_id=102) ← Use the numeric ID 102\n"
            "\n"
            "User: 'Edit my shopping task'\n"
            "1. Call mcp_list_tasks() → Get [{\"id\": 85, \"title\": \"shopping\"}, ...]\n"
            "2. Call mcp_update_task(task_id=85, title=\"new title\") ← Use the numeric ID 85\n"
            "\n"
            "User: 'میری خریداری کی فہرست دکھائیں' (Urdu: Show my shopping list)\n"
            "1. Call mcp_list_tasks() → Get tasks\n"
            "2. Respond: 'یہاں آپ کے کام ہیں...' (Here are your tasks...)\n"
            "\n"
            "When users ask to create tasks, use the mcp_create_task tool with natural language support "
            "(e.g., 'tomorrow' for due dates, 'URGENT' in description sets high priority). "
            "Be concise, friendly, and proactive. Always confirm operations."
        )
        messages.append({
            "role": "system",
            "content": system_prompt or default_system_prompt
        })

    # Add conversation history
    messages.extend(history)

    # Add new user message
    messages.append({
        "role": "user",
        "content": message
    })

    # Tool execution tracking
    tool_calls_audit = []
    total_tokens = 0
    iteration = 0
    executed_tools = set()  # Track executed tool signatures to prevent duplicates across iterations

    # Agent execution loop (for multi-turn tool calling)
    while iteration < max_tool_calls:
        iteration += 1

        try:
            # Call OpenAI API with MCP tools (official FastMCP SDK integration)
            logger.debug(f"OpenAI API call (iteration {iteration}) with {len(openai_tools)} tools")

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=openai_tools,  # MCP tools in OpenAI function calling format
                tool_choice="auto",  # Let model decide when to use tools
                temperature=0.7,
                max_tokens=2000
            )

            # Extract response
            assistant_message = completion.choices[0].message
            finish_reason = completion.choices[0].finish_reason
            total_tokens += completion.usage.total_tokens

            # No tool calls - return final response
            if not hasattr(assistant_message, 'tool_calls') or not assistant_message.tool_calls:
                response_text = assistant_message.content or ""

                duration_ms = int((time.time() - start_time) * 1000)

                logger.info(
                    f"Agent execution completed",
                    extra={
                        "user_id": str(user_id),
                        "iterations": iteration,
                        "tool_calls": len(tool_calls_audit),
                        "tokens_used": total_tokens,
                        "duration_ms": duration_ms,
                        "finish_reason": finish_reason
                    }
                )

                return {
                    "response": response_text,
                    "tool_calls": tool_calls_audit,
                    "model": model,
                    "tokens_used": total_tokens,
                    "finish_reason": finish_reason
                }

            # Tool calls present - execute them
            logger.info(
                f"Agent requested {len(assistant_message.tool_calls)} tool calls in iteration {iteration}"
            )

            # Log each tool call for debugging
            for idx, tc in enumerate(assistant_message.tool_calls):
                try:
                    args_dict = json.loads(tc.function.arguments)
                    logger.info(
                        f"[Iteration {iteration}] Tool call #{idx + 1}: {tc.function.name}({args_dict})"
                    )
                except:
                    logger.info(
                        f"[Iteration {iteration}] Tool call #{idx + 1}: {tc.function.name} (args: {tc.function.arguments[:100]})"
                    )

            # BUGFIX: Deduplicate tool calls (Groq Llama sometimes makes duplicate calls)
            # 1. Remove duplicates within this response
            # 2. Remove duplicates across all iterations (prevent re-executing same tool)
            unique_tool_calls = []
            seen_calls = set()
            skipped_already_executed = 0

            for tc in assistant_message.tool_calls:
                call_signature = (tc.function.name, tc.function.arguments)

                # Skip if already executed in a previous iteration
                if call_signature in executed_tools:
                    skipped_already_executed += 1
                    logger.warning(
                        f"Skipping duplicate tool call (already executed): {tc.function.name}"
                    )
                    continue

                # Skip if duplicate within this response
                if call_signature not in seen_calls:
                    unique_tool_calls.append(tc)
                    seen_calls.add(call_signature)
                    executed_tools.add(call_signature)  # Mark as executed

            if len(unique_tool_calls) < len(assistant_message.tool_calls):
                logger.warning(
                    f"Deduplicated tool calls: {len(assistant_message.tool_calls)} → {len(unique_tool_calls)} (skipped {skipped_already_executed} already executed)"
                )

            # If all tool calls were duplicates, break the loop to prevent infinite iteration
            if len(unique_tool_calls) == 0:
                logger.warning("All tool calls were duplicates - stopping agent loop")
                break

            # Add assistant message with tool calls to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in unique_tool_calls  # Use deduplicated calls
                ]
            })

            # Execute each tool call (deduplicated)
            for tool_call in unique_tool_calls:
                tool_start = time.time()
                tool_name = tool_call.function.name
                tool_arguments_str = tool_call.function.arguments

                try:
                    # Parse arguments
                    tool_arguments = json.loads(tool_arguments_str)

                    logger.debug(
                        f"Executing tool: {tool_name}",
                        extra={"arguments": tool_arguments}
                    )

                    # Execute MCP tool via FastMCP SDK (with injected JWT token)
                    raw_result = await _execute_tool(
                        tool_name=tool_name,
                        arguments=tool_arguments,
                        user_token=user_token  # Inject JWT token for authentication
                    )

                    # BUGFIX: Convert TextContent to JSON-serializable dict/list
                    # FastMCP returns TextContent objects that aren't directly serializable
                    tool_result = convert_textcontent_to_dict(raw_result)

                    # AGGRESSIVE FAILSAFE: If still TextContent, extract text manually
                    if type(tool_result).__name__ == 'TextContent':
                        logger.error(f"Conversion failed! Still TextContent after convert_textcontent_to_dict")
                        try:
                            tool_result = json.loads(tool_result.text)
                            logger.info(f"Manually extracted text from TextContent")
                        except:
                            tool_result = {"text": str(tool_result.text)}
                            logger.error(f"Manual extraction also failed, wrapped in dict")

                    tool_status = "success"

                    logger.info(
                        f"✓ Tool executed successfully: {tool_name}",
                        extra={
                            "result_type": type(tool_result).__name__,
                            "result_preview": str(tool_result)[:200] if tool_result else None
                        }
                    )

                except json.JSONDecodeError as e:
                    logger.error(
                        f"✗ Tool arguments JSON decode failed: {tool_name}",
                        extra={
                            "error": str(e),
                            "arguments_str": tool_arguments_str[:200]
                        }
                    )
                    tool_result = {
                        "error": "Invalid tool arguments format",
                        "details": str(e)
                    }
                    tool_status = "error"

                except Exception as e:
                    logger.error(
                        f"✗ Tool execution failed: {tool_name}",
                        exc_info=True,
                        extra={
                            "error": str(e),
                            "arguments": tool_arguments if 'tool_arguments' in locals() else "N/A"
                        }
                    )
                    tool_result = {
                        "error": "Tool execution failed",
                        "details": str(e)
                    }
                    tool_status = "error"

                # Record tool execution
                tool_duration_ms = int((time.time() - tool_start) * 1000)
                tool_calls_audit.append({
                    "tool_name": tool_name,
                    "arguments": tool_arguments if isinstance(tool_arguments, dict) else {},
                    "result": tool_result,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "duration_ms": tool_duration_ms,
                    "status": tool_status
                })

                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise

        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            raise

    # Exceeded max iterations
    logger.warning(
        f"Agent exceeded max tool call iterations",
        extra={"max_tool_calls": max_tool_calls}
    )

    return {
        "response": "I apologize, but I've reached the maximum number of tool calls. Please try breaking down your request.",
        "tool_calls": tool_calls_audit,
        "model": model,
        "tokens_used": total_tokens,
        "finish_reason": "max_iterations"
    }


async def _execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    user_token: str
) -> Dict[str, Any]:
    """
    Execute a single MCP tool via official FastMCP SDK.

    CONSTITUTIONAL REQUIREMENT: Agent interacts with tasks ONLY via MCP tools.
    This function calls the MCP server which uses the official FastMCP SDK pattern.

    Args:
        tool_name: Name of the MCP tool to execute (e.g., "mcp_list_tasks")
        arguments: Tool arguments from OpenAI (user_token excluded)
        user_token: JWT token for authentication (injected, not from OpenAI)

    Returns:
        Tool execution result as dictionary

    Raises:
        Exception: If tool execution fails

    Example:
        result = await _execute_tool(
            tool_name="mcp_create_task",
            arguments={"title": "Buy groceries", "due_date": "tomorrow"},
            user_token="eyJhbGciOiJIUzI1NiIs..."
        )
        # Returns: {"id": 123, "title": "Buy groceries", ...}
    """
    logger.info(
        f"Executing MCP tool via FastMCP SDK: {tool_name}",
        extra={
            "tool_name": tool_name,
            "arguments": arguments
        }
    )

    # BUGFIX: Handle None arguments (some tools like list_tasks have no required params)
    if arguments is None:
        arguments = {}

    # BUGFIX: Convert string task_id to integer (Groq Llama sometimes passes strings)
    # This handles cases where the LLM passes "102" instead of 102
    if "task_id" in arguments and isinstance(arguments["task_id"], str):
        try:
            arguments["task_id"] = int(arguments["task_id"])
            logger.info(f"Converted string task_id to integer: {arguments['task_id']}")
        except ValueError:
            logger.error(f"Invalid task_id string: {arguments['task_id']}")
            raise ValueError(f"task_id must be a numeric value, got: {arguments['task_id']}")

    # Inject user_token into arguments (required by all MCP tools)
    # This ensures JWT authentication for tenant isolation
    tool_arguments_with_token = {
        "user_token": user_token,
        **arguments
    }

    try:
        # Call MCP tool via FastMCP's execute_mcp_tool helper
        # This uses the official FastMCP SDK pattern
        result = await execute_mcp_tool(
            tool_name=tool_name,
            arguments=tool_arguments_with_token
        )

        logger.info(
            f"MCP tool executed successfully: {tool_name}",
            extra={"tool_name": tool_name, "result_type": type(result).__name__}
        )

        return result

    except Exception as e:
        logger.error(
            f"MCP tool execution failed: {tool_name} - {str(e)}",
            exc_info=True,
            extra={
                "tool_name": tool_name,
                "arguments": arguments,
                "error": str(e)
            }
        )
        # Re-raise to be caught by run_agent's error handling
        raise
