/**
 * TypeScript types for OpenAI Chatkit Integration & History Persistence
 *
 * Corresponds to backend Pydantic schemas and SQLModel entities
 * Spec: @specs/006-chatkit-history-persistence/data-model.md
 */

// ============================================================================
// Enums
// ============================================================================

/**
 * Message author role enum
 * Maps to backend MessageRole enum
 */
export enum MessageRole {
  USER = "user",
  ASSISTANT = "assistant"
}

// ============================================================================
// Tool Call Types
// ============================================================================

/**
 * Tool call result for MCP tool invocations
 * Stored in JSONB on assistant messages
 */
export interface ToolCall {
  /** Name of the MCP tool that was invoked */
  tool_name: string;

  /** Arguments passed to the tool (flexible structure) */
  arguments: Record<string, any>;

  /** Result returned by the tool (flexible structure) */
  result: Record<string, any>;

  /** ISO timestamp when tool was invoked */
  timestamp: string;

  /** Execution duration in milliseconds */
  duration_ms: number;

  /** Execution status (success, error, etc.) */
  status: string;
}

/**
 * Container for multiple tool calls in a message
 */
export interface ToolCallsContainer {
  tool_calls: ToolCall[];
}

// ============================================================================
// Core Entity Types
// ============================================================================

/**
 * Conversation entity
 * Represents a chat thread between user and AI assistant
 */
export interface Conversation {
  /** Unique conversation identifier (UUID) */
  id: string;

  /** Owner of this conversation (tenant isolation) */
  user_id: string;

  /** Conversation title (auto-generated or user-set) */
  title: string;

  /** Conversation creation timestamp (ISO 8601) */
  created_at: string;

  /** Last message timestamp for sorting (ISO 8601) */
  updated_at: string;

  /** Soft delete timestamp - null means active (ISO 8601) */
  deleted_at?: string | null;

  /** Computed field: total message count in conversation */
  message_count: number;

  /** Computed field: first 100 chars of last message (for preview) */
  last_message_preview?: string | null;
}

/**
 * Message entity
 * Represents a single message in a conversation (user or assistant)
 */
export interface Message {
  /** Unique message identifier (UUID) */
  id: string;

  /** Parent conversation ID */
  conversation_id: string;

  /** Message author: "user" or "assistant" */
  role: MessageRole | string;

  /** Message text content (markdown supported, max 10,000 chars) */
  content: string;

  /** MCP tool invocations (JSONB, assistant messages only) */
  tool_calls?: ToolCallsContainer | null;

  /** Message creation timestamp (ISO 8601) */
  created_at: string;
}

// ============================================================================
// API Request Types
// ============================================================================

/**
 * Request: Create new conversation
 * POST /api/chat/conversations
 */
export interface ConversationCreate {
  /** Optional title (auto-generated if omitted, max 200 chars) */
  title?: string;
}

/**
 * Request: Update conversation title
 * PATCH /api/chat/conversations/{id}
 */
export interface ConversationUpdate {
  /** New conversation title (required, 1-200 chars) */
  title: string;
}

/**
 * Request: Send new message to conversation
 * POST /api/chat/conversations/{id}/messages
 */
export interface MessageCreate {
  /** Message text content (required, 1-10,000 chars, trimmed) */
  content: string;
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * Response: Single conversation data
 * Includes computed fields (message_count, last_message_preview)
 */
export interface ConversationResponse {
  /** Unique conversation identifier (UUID) */
  id: string;

  /** Owner of this conversation */
  user_id: string;

  /** Conversation title */
  title: string;

  /** Conversation creation timestamp (ISO 8601) */
  created_at: string;

  /** Last message timestamp (ISO 8601) */
  updated_at: string;

  /** Total message count in conversation */
  message_count: number;

  /** First 100 chars of last message (for preview) */
  last_message_preview?: string | null;
}

/**
 * Response: Paginated conversation list
 * GET /api/chat/conversations?limit=20&cursor=2025-12-19T10:00:00.000Z
 */
export interface ConversationListResponse {
  /** Array of conversations (ordered by updated_at DESC) */
  conversations: ConversationResponse[];

  /** ISO timestamp for next page cursor (null if no more pages) */
  nextCursor?: string | null;

  /** Whether more pages exist */
  hasMore: boolean;
}

/**
 * Response: Single message data
 */
export interface MessageResponse {
  /** Unique message identifier (UUID) */
  id: string;

  /** Parent conversation ID */
  conversation_id: string;

  /** Message author: "user" or "assistant" */
  role: string;

  /** Message text content */
  content: string;

  /** MCP tool invocations (assistant messages only) */
  tool_calls?: ToolCallsContainer | null;

  /** Message creation timestamp (ISO 8601) */
  created_at: string;
}

/**
 * Response: Conversation message history
 * GET /api/chat/conversations/{id}/messages
 */
export interface MessageListResponse {
  /** Array of messages (chronologically ordered by created_at ASC) */
  messages: MessageResponse[];

  /** Parent conversation ID */
  conversation_id: string;

  /** Total message count in conversation */
  total_count: number;
}

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if a role is valid MessageRole
 */
export function isMessageRole(role: string): role is MessageRole {
  return role === MessageRole.USER || role === MessageRole.ASSISTANT;
}

/**
 * Type guard to check if a message has tool calls
 */
export function hasToolCalls(message: Message | MessageResponse): message is (Message | MessageResponse) & { tool_calls: ToolCallsContainer } {
  return message.tool_calls !== undefined && message.tool_calls !== null;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Client-side conversation state (before persisted to backend)
 */
export interface ConversationDraft {
  title?: string;
  messages: Array<{
    role: MessageRole;
    content: string;
  }>;
}

/**
 * Error response from chat API
 */
export interface ChatAPIError {
  detail: string;
  status_code: number;
}
