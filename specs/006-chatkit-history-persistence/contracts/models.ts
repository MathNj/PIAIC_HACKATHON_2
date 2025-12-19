/**
 * TypeScript interfaces for Chat API
 *
 * Generated from OpenAPI spec: chat-api.yaml
 * Phase III: OpenAI Chatkit Integration & History Persistence
 *
 * These types match the backend Pydantic schemas exactly to ensure type safety
 * across the frontend-backend boundary.
 */

/**
 * Message author role
 */
export type MessageRole = 'user' | 'assistant';

/**
 * Tool execution status
 */
export type ToolExecutionStatus = 'success' | 'error';

/**
 * MCP tool invocation record
 */
export interface ToolCall {
  tool_name: string;
  arguments: Record<string, any>;
  result: Record<string, any>;
  timestamp: string; // ISO 8601 format
  duration_ms: number;
  status: ToolExecutionStatus;
}

/**
 * Tool calls metadata (stored in messages.tool_calls JSONB column)
 */
export interface ToolCallsMetadata {
  tool_calls: ToolCall[];
}

/**
 * Conversation entity
 */
export interface Conversation {
  id: string; // UUID
  user_id: string; // UUID
  title: string;
  created_at: string; // ISO 8601 format
  updated_at: string; // ISO 8601 format
  message_count: number;
  last_message_preview?: string | null;
}

/**
 * Request: Create new conversation
 */
export interface ConversationCreate {
  title?: string | null;
}

/**
 * Request: Update conversation title
 */
export interface ConversationUpdate {
  title: string;
}

/**
 * Response: Paginated conversation list
 */
export interface ConversationListResponse {
  conversations: Conversation[];
  nextCursor?: string | null; // ISO 8601 timestamp for cursor pagination
  hasMore: boolean;
}

/**
 * Message entity
 */
export interface Message {
  id: string; // UUID
  conversation_id: string; // UUID
  role: MessageRole;
  content: string;
  tool_calls?: ToolCallsMetadata | null;
  created_at: string; // ISO 8601 format
}

/**
 * Request: Send new message
 */
export interface MessageCreate {
  content: string;
}

/**
 * Response: Conversation message history
 */
export interface MessageListResponse {
  messages: Message[];
  conversation_id: string;
  total_count: number;
}

/**
 * Response: Send message result (includes both user and assistant messages)
 */
export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
}

/**
 * API error response
 */
export interface ApiError {
  detail: string;
}

/**
 * Query parameters for listing conversations
 */
export interface ListConversationsParams {
  limit?: number; // Default: 20, Max: 100
  cursor?: string; // ISO 8601 timestamp
}

/**
 * Query parameters for listing messages
 */
export interface ListMessagesParams {
  limit?: number; // Default: 50, Max: 100
  since?: string; // ISO 8601 timestamp (for polling new messages)
}

/**
 * OpenAI Chatkit configuration types
 */

/**
 * Chatkit adapter interface for backend integration
 */
export interface ChatkitAdapter {
  getConversations(): Promise<Conversation[]>;
  getMessages(conversationId: string): Promise<Message[]>;
  sendMessage(conversationId: string, content: string): Promise<SendMessageResponse>;
  createConversation(title?: string): Promise<Conversation>;
  updateConversationTitle(conversationId: string, title: string): Promise<Conversation>;
  deleteConversation(conversationId: string): Promise<void>;
}

/**
 * Chatkit configuration
 */
export interface ChatkitConfig {
  adapter: ChatkitAdapter;
  enableMarkdown?: boolean; // Default: true
  enableSyntaxHighlighting?: boolean; // Default: true
  pollingInterval?: number; // Milliseconds, default: 2000
  maxMessageLength?: number; // Default: 10000
}

/**
 * Frontend chat state
 */
export interface ChatState {
  conversations: Conversation[];
  activeConversationId: string | null;
  messages: Message[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
}

/**
 * Chat action types for state management
 */
export enum ChatActionType {
  LOAD_CONVERSATIONS = 'LOAD_CONVERSATIONS',
  SELECT_CONVERSATION = 'SELECT_CONVERSATION',
  LOAD_MESSAGES = 'LOAD_MESSAGES',
  SEND_MESSAGE = 'SEND_MESSAGE',
  RECEIVE_MESSAGE = 'RECEIVE_MESSAGE',
  CREATE_CONVERSATION = 'CREATE_CONVERSATION',
  UPDATE_CONVERSATION_TITLE = 'UPDATE_CONVERSATION_TITLE',
  DELETE_CONVERSATION = 'DELETE_CONVERSATION',
  SET_LOADING = 'SET_LOADING',
  SET_ERROR = 'SET_ERROR',
  CLEAR_ERROR = 'CLEAR_ERROR',
}

/**
 * Type guards for runtime type checking
 */
export function isUserMessage(message: Message): boolean {
  return message.role === 'user';
}

export function isAssistantMessage(message: Message): boolean {
  return message.role === 'assistant';
}

export function hasToolCalls(message: Message): boolean {
  return message.tool_calls !== null && message.tool_calls !== undefined;
}

/**
 * Validation utilities
 */
export function validateMessageContent(content: string): { valid: boolean; error?: string } {
  if (!content || content.trim().length === 0) {
    return { valid: false, error: 'Message cannot be empty' };
  }

  if (content.length > 10000) {
    return { valid: false, error: 'Message exceeds 10,000 character limit' };
  }

  return { valid: true };
}

export function validateConversationTitle(title: string): { valid: boolean; error?: string } {
  if (!title || title.trim().length === 0) {
    return { valid: false, error: 'Title cannot be empty' };
  }

  if (title.length > 200) {
    return { valid: false, error: 'Title exceeds 200 character limit' };
  }

  return { valid: true };
}

/**
 * Formatting utilities
 */
export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

export function getConversationPreview(conversation: Conversation): string {
  return conversation.last_message_preview || 'No messages yet';
}

export function truncateTitle(title: string, maxLength: number = 50): string {
  if (title.length <= maxLength) return title;
  return title.substring(0, maxLength - 3) + '...';
}

/**
 * API client helper types
 */
export interface ApiRequestConfig {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  endpoint: string;
  body?: any;
  params?: Record<string, string | number | undefined>;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  status: number;
}

/**
 * Example usage patterns for documentation
 */

// Example: Create new conversation
// const newConv = await api.post<Conversation>('/api/chat/conversations', { title: 'My Chat' });

// Example: List conversations with pagination
// const list = await api.get<ConversationListResponse>('/api/chat/conversations', { limit: 20 });

// Example: Send message
// const response = await api.post<SendMessageResponse>(
//   `/api/chat/conversations/${conversationId}/messages`,
//   { content: 'Hello AI!' }
// );

// Example: Poll for new messages
// const newMessages = await api.get<MessageListResponse>(
//   `/api/chat/conversations/${conversationId}/messages`,
//   { since: lastMessageTimestamp }
// );
