// TypeScript types for OpenAI Chatkit integration with database-backed conversation history
// Copy this file to: frontend/src/types/chat.ts

export type MessageRole = "user" | "assistant";

export interface Conversation {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview?: string | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  tool_calls?: ToolCallsMetadata | null;
  created_at: string;
}

export interface ToolCallsMetadata {
  tool_name: string;
  tool_args: Record<string, any>;
  tool_result?: any;
  execution_time_ms?: number;
}

export interface ConversationCreate {
  title?: string;
}

export interface ConversationUpdate {
  title: string;
}

export interface MessageCreate {
  content: string;
}

export interface ConversationListResponse {
  conversations: Conversation[];
  cursor?: string | null;
  has_more: boolean;
}

export interface MessageListResponse {
  messages: Message[];
  conversation_id: string;
}

export interface SendMessageResponse {
  user_message: Message;
  assistant_message: Message;
}

// API Error Response
export interface ApiError {
  detail: string;
  status_code: number;
}

// Chatkit Adapter Interface
export interface ChatkitAdapter {
  getConversations(): Promise<Conversation[]>;
  getMessages(conversationId: string): Promise<Message[]>;
  sendMessage(conversationId: string, content: string): Promise<SendMessageResponse>;
  createConversation(title?: string): Promise<Conversation>;
  updateConversation(conversationId: string, title: string): Promise<Conversation>;
  deleteConversation(conversationId: string): Promise<void>;
}

// Type Guards
export function isUserMessage(message: Message): boolean {
  return message.role === "user";
}

export function isAssistantMessage(message: Message): boolean {
  return message.role === "assistant";
}

export function hasToolCalls(message: Message): boolean {
  return message.tool_calls !== null && message.tool_calls !== undefined;
}

// Validation Utilities
export function validateMessageContent(content: string): boolean {
  return content.length > 0 && content.length <= 10000;
}

export function validateConversationTitle(title: string): boolean {
  return title.length > 0 && title.length <= 200;
}

// Formatting Utilities
export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString();
}

export function truncateTitle(title: string, maxLength: number = 50): string {
  if (title.length <= maxLength) return title;
  return title.slice(0, maxLength - 3) + "...";
}

export function getConversationPreview(conversation: Conversation): string {
  return conversation.last_message_preview || "No messages yet";
}
