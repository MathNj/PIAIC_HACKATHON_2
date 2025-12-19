// OpenAI Chatkit configuration with custom backend adapter
// Copy this file to: frontend/src/lib/chatkit-config.ts

import { createChatkitAdapter } from "@/lib/api/chat";
import type { ChatkitConfig } from "@openai/chatkit";

export const chatkitConfig: ChatkitConfig = {
  // Custom backend adapter for database-backed conversation persistence
  adapter: createChatkitAdapter(),

  // UI Configuration
  enableMarkdown: true,
  enableSyntaxHighlighting: true,
  enableCodeCopy: true,

  // Real-time updates via HTTP polling (2-3 seconds)
  pollingInterval: 2000,

  // Theme customization (optional)
  theme: {
    primaryColor: "#0070f3",
    backgroundColor: "#ffffff",
    textColor: "#000000",
    borderColor: "#e5e7eb",
  },

  // Message configuration
  maxMessageLength: 10000,
  placeholder: "Type your message...",
  sendButtonText: "Send",

  // Conversation list configuration
  showConversationList: true,
  conversationListTitle: "Conversations",
  newConversationButtonText: "New Chat",

  // Error handling
  onError: (error: Error) => {
    console.error("Chatkit error:", error);
    // Add custom error handling here (e.g., toast notification)
  },

  // Callbacks
  onMessageSent: (conversationId: string, content: string) => {
    console.log("Message sent:", { conversationId, content });
  },

  onConversationCreated: (conversationId: string) => {
    console.log("Conversation created:", conversationId);
  },

  onConversationSelected: (conversationId: string) => {
    console.log("Conversation selected:", conversationId);
  },
};

export default chatkitConfig;
