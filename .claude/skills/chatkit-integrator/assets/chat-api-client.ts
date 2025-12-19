// API client for OpenAI Chatkit backend integration
// Copy this file to: frontend/src/lib/api/chat.ts

import type {
  Conversation,
  ConversationCreate,
  ConversationUpdate,
  ConversationListResponse,
  Message,
  MessageCreate,
  MessageListResponse,
  SendMessageResponse,
  ChatkitAdapter,
} from "@/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Helper function to get JWT token from storage
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

// Helper function to build authenticated headers
function getAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

// Helper function to handle API errors
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: response.statusText,
      status_code: response.status,
    }));
    throw new Error(error.detail || "API request failed");
  }
  return response.json();
}

// Conversation API Endpoints
export const conversationApi = {
  async list(cursor?: string, limit: number = 20): Promise<ConversationListResponse> {
    const params = new URLSearchParams();
    if (cursor) params.append("cursor", cursor);
    params.append("limit", limit.toString());

    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations?${params}`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<ConversationListResponse>(response);
  },

  async create(data: ConversationCreate): Promise<Conversation> {
    const response = await fetch(`${API_BASE_URL}/api/chat/conversations`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<Conversation>(response);
  },

  async get(conversationId: string): Promise<Conversation> {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations/${conversationId}`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<Conversation>(response);
  },

  async update(
    conversationId: string,
    data: ConversationUpdate
  ): Promise<Conversation> {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations/${conversationId}`,
      {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    );
    return handleResponse<Conversation>(response);
  },

  async delete(conversationId: string): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations/${conversationId}`,
      {
        method: "DELETE",
        headers: getAuthHeaders(),
      }
    );
    if (!response.ok) {
      throw new Error("Failed to delete conversation");
    }
  },
};

// Message API Endpoints
export const messageApi = {
  async list(
    conversationId: string,
    since?: string
  ): Promise<MessageListResponse> {
    const params = new URLSearchParams();
    if (since) params.append("since", since);

    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations/${conversationId}/messages?${params}`,
      {
        method: "GET",
        headers: getAuthHeaders(),
      }
    );
    return handleResponse<MessageListResponse>(response);
  },

  async send(
    conversationId: string,
    data: MessageCreate
  ): Promise<SendMessageResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/chat/conversations/${conversationId}/messages`,
      {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      }
    );
    return handleResponse<SendMessageResponse>(response);
  },
};

// Combined API object
export const chatApi = {
  conversations: conversationApi,
  messages: messageApi,

  // Convenience methods for common operations
  async listConversations(cursor?: string, limit?: number) {
    return conversationApi.list(cursor, limit);
  },

  async createConversation(data: ConversationCreate) {
    return conversationApi.create(data);
  },

  async getMessages(conversationId: string, since?: string) {
    return messageApi.list(conversationId, since);
  },

  async sendMessage(conversationId: string, data: MessageCreate) {
    return messageApi.send(conversationId, data);
  },

  async updateConversationTitle(conversationId: string, title: string) {
    return conversationApi.update(conversationId, { title });
  },

  async deleteConversation(conversationId: string) {
    return conversationApi.delete(conversationId);
  },
};

// Chatkit Adapter Implementation
export const createChatkitAdapter = (): ChatkitAdapter => ({
  async getConversations() {
    const response = await chatApi.listConversations();
    return response.conversations;
  },

  async getMessages(conversationId: string) {
    const response = await chatApi.getMessages(conversationId);
    return response.messages;
  },

  async sendMessage(conversationId: string, content: string) {
    return chatApi.sendMessage(conversationId, { content });
  },

  async createConversation(title?: string) {
    return chatApi.createConversation({ title });
  },

  async updateConversation(conversationId: string, title: string) {
    return chatApi.updateConversationTitle(conversationId, title);
  },

  async deleteConversation(conversationId: string) {
    return chatApi.deleteConversation(conversationId);
  },
});

export default chatApi;
