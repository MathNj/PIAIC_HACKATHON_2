"use client";

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/components/AuthProvider';
import { chatkitAdapter } from '@/lib/chatkit-config';
import type { MessageResponse } from '@/src/types/chat';
import Link from 'next/link';

/**
 * Chat Page - OpenAI Chatkit Integration
 *
 * Provides a conversational interface for task management with database-backed
 * conversation persistence and AI agent responses.
 *
 * Features:
 * - Create new conversations
 * - Send messages and receive AI responses
 * - Auto-scroll to latest messages
 * - Loading and error states
 * - Responsive design with Tailwind CSS
 */
export default function ChatPage() {
  const { user, signOut } = useAuth();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  /**
   * Create a new conversation
   */
  const createNewConversation = async () => {
    try {
      setError(null);
      const conv = await chatkitAdapter.createConversation('New Chat');
      setConversationId(conv.id);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create conversation:', err);
      setError('Failed to create new conversation. Please try again.');
    }
  };

  /**
   * Send a message to the current conversation
   */
  const sendMessage = async () => {
    if (!input.trim()) return;

    // Create conversation if it doesn't exist
    if (!conversationId) {
      await createNewConversation();
      return;
    }

    const userMessage = input;
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Add user message to UI (optimistic update)
      const tempUserMessage: MessageResponse = {
        id: Date.now().toString(),
        conversation_id: conversationId,
        role: 'user',
        content: userMessage,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, tempUserMessage]);

      // Send to backend and get AI response
      const response = await chatkitAdapter.sendMessage(conversationId, userMessage);

      // Add AI response to UI
      setMessages((prev) => [...prev, response]);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError(err instanceof Error ? err.message : 'Failed to send message. Please try again.');

      // Remove optimistic user message on error
      setMessages((prev) => prev.slice(0, -1));
      setInput(userMessage); // Restore user input
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle Enter key press to send message
   */
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Show loading spinner while checking auth
  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-pink-900">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-white border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-pink-900 text-white">
      {/* Header */}
      <header className="sticky top-0 z-30 bg-gray-900/50 backdrop-blur-lg border-b border-white/10 shadow-lg py-4">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            AI Task Assistant
          </h1>
          <div className="flex items-center gap-3">
            <span className="text-gray-300 text-sm hidden sm:block">
              Welcome, {user?.name || 'User'}!
            </span>
            <button
              onClick={createNewConversation}
              className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition-all text-sm font-medium"
            >
              New Chat
            </button>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg hover:bg-white/20 transition-all text-sm font-medium"
            >
              Dashboard
            </Link>
            <button
              onClick={signOut}
              className="px-4 py-2 bg-red-600/20 border border-red-500/30 rounded-lg hover:bg-red-600/30 transition-all text-sm font-medium text-red-400"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 pb-4 flex flex-col">
        {/* Error Banner */}
        {error && (
          <div className="my-4 p-4 bg-red-900/50 border border-red-700 rounded-lg flex justify-between items-center">
            <p className="text-sm text-red-300">{error}</p>
            <button
              onClick={() => setError(null)}
              className="text-red-300 hover:text-red-100 text-xl font-bold"
            >
              &times;
            </button>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 bg-gray-900/30 backdrop-blur-sm rounded-2xl border border-white/10 shadow-lg mb-4">
          {/* Empty State */}
          {messages.length === 0 && (
            <div className="text-center py-12 flex flex-col items-center justify-center h-full">
              <div className="text-6xl mb-4 animate-bounce">🤖</div>
              <h3 className="text-2xl font-semibold text-white mb-2">AI Task Assistant</h3>
              <p className="text-gray-400 mb-8 max-w-md mx-auto">
                I can create, update, list, and delete tasks for you. Just ask!
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto text-left w-full">
                <SuggestionCard>Create a high-priority task to &quot;Deploy the new model by Friday&quot;</SuggestionCard>
                <SuggestionCard>Show me all my completed tasks</SuggestionCard>
                <SuggestionCard>Mark task #12 as &quot;low&quot; priority</SuggestionCard>
                <SuggestionCard>Delete task &quot;Old quarterly report&quot;</SuggestionCard>
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}

          {/* Loading Indicator */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-700/50 rounded-2xl px-5 py-3 flex items-center gap-3">
                <div className="text-2xl">🤖</div>
                <div className="flex gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <div
                      key={i}
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: `${i * 0.1}s` }}
                    ></div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Press Enter to send)"
            className="flex-1 px-5 py-4 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-medium hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * Suggestion Card Component
 */
function SuggestionCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-gray-800/30 p-4 rounded-lg border border-white/10 hover:bg-gray-800/50 transition-colors cursor-pointer">
      <p className="text-sm text-gray-300">{children}</p>
    </div>
  );
}

/**
 * Chat Message Component
 */
function ChatMessage({ message }: { message: MessageResponse }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex-shrink-0 text-3xl ${isUser ? 'order-2' : 'order-1'}`}>
        {isUser ? '👤' : '🤖'}
      </div>
      <div
        className={`max-w-3xl rounded-2xl px-5 py-3 ${
          isUser
            ? 'order-1 bg-gradient-to-r from-blue-600 to-purple-600'
            : 'order-2 bg-gray-700/50'
        }`}
      >
        <p className="text-base whitespace-pre-wrap break-words">{message.content}</p>

        {/* Tool Calls Display */}
        {message.tool_calls && message.tool_calls.tool_calls && message.tool_calls.tool_calls.length > 0 && (
          <div className="mt-4 space-y-3">
            {message.tool_calls.tool_calls.map((call, idx) => (
              <div
                key={idx}
                className="bg-gray-800/30 border border-white/10 rounded-lg p-3 text-xs"
              >
                <div className="font-semibold text-gray-300 mb-2 flex items-center gap-2">
                  🔧 {call.tool_name}
                </div>
                <pre className="text-gray-400 bg-black/20 rounded p-2 overflow-x-auto">
                  {JSON.stringify(call.arguments, null, 2)}
                </pre>
                {call.result && (
                  <pre className="text-green-400 bg-black/20 rounded p-2 mt-2 overflow-x-auto">
                    {JSON.stringify(call.result, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        {message.created_at && (
          <p
            className={`text-xs mt-2 ${
              isUser ? 'text-blue-100/70' : 'text-gray-400'
            }`}
          >
            {new Date(message.created_at).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}
