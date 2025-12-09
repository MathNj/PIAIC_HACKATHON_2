"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/components/AuthProvider";
import { api } from "@/lib/api";
import Link from "next/link";


interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  tool_calls?: ToolCall[];
  created_at?: string;
}

interface ToolCall {
  tool: string;
  arguments: Record<string, any>;
  result?: any;
  success?: boolean;
  timestamp?: string;
}

const ChatPage = () => {
  const { user, signOut } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleNewConversation = () => {
    if (messages.length > 0 && confirm("Are you sure you want to start a new conversation?")) {
      setMessages([]);
      setConversationId(null);
      setError(null);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !input.trim() || loading) return;

    const userMessage: Message = { id: `user-${Date.now()}`, role: "user", content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const response = await api.post(`/api/${user.id}/chat`, {
        conversation_id: conversationId,
        message: userMessage.content,
      });
      setConversationId(response.conversation_id);
      const assistantMessage: Message = { id: `assistant-${response.message.id}`, ...response.message };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-pink-900 flex items-center justify-center">
        <div className="spinner-lg"></div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-900 via-gray-900 to-pink-900 text-white flex flex-col">
      <ChatHeader onNewChat={handleNewConversation} onSignOut={signOut} userName={user?.name || "User"} />
      <div className="flex-1 max-w-5xl w-full mx-auto px-4 pb-4 flex flex-col">
        {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 glass-dark rounded-2xl border border-white/10 shadow-lg mb-4">
          {messages.length === 0 ? <WelcomeEmptyState /> : <MessageList messages={messages} loading={loading} />}
          <div ref={messagesEndRef} />
        </div>
        <ChatInput input={input} setInput={setInput} handleSubmit={handleSubmit} loading={loading} />
      </div>
      <style jsx global>{`
        .btn-secondary {
          background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2);
          color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; font-weight: 500; transition: all 0.2s;
        }
        .btn-secondary:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.3); }
        .spinner-lg { width: 50px; height: 50px; border: 4px solid rgba(255, 255, 255, 0.2); border-top-color: #6366f1; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </main>
  );
};

// ============================================
// SUB-COMPONENTS
// ============================================

const ChatHeader = ({ onNewChat, onSignOut, userName }: { onNewChat: () => void; onSignOut: () => void; userName: string; }) => (
  <header className="sticky top-0 z-30 glass-dark border-b border-white/10 shadow-lg py-4">
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
      <h1 className="text-2xl font-bold gradient-text">AI Assistant</h1>
      <div className="flex items-center gap-3">
        <span className="text-gray-300 text-sm hidden sm:block">Welcome, {userName}!</span>
        <button onClick={onNewChat} className="btn-secondary text-sm">New Chat</button>
        <Link href="/dashboard" className="btn-secondary text-sm">Dashboard</Link>
        <button onClick={onSignOut} className="btn-secondary text-sm !text-red-600 hover:!text-red-800">Sign Out</button>
      </div>
    </div>
  </header>
);

const AnimatedBackground = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
    <div className="absolute top-0 left-0 w-96 h-96 bg-purple-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-float"></div>
    <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-float" style={{ animationDelay: "1s" }}></div>
    <div className="absolute bottom-0 left-1/2 w-96 h-96 bg-pink-500 rounded-full mix-blend-screen filter blur-3xl opacity-20 animate-float" style={{ animationDelay: "2s" }}></div>
  </div>
);

const ErrorMessage = ({ message, onDismiss }: { message: string, onDismiss: () => void }) => (
  <div className="mb-4 rounded-lg bg-red-900/50 p-4 border border-red-700 flex justify-between items-center">
    <p className="text-sm text-red-300">{message}</p>
    <button onClick={onDismiss} className="text-red-300 hover:text-red-100">&times;</button>
  </div>
);

const WelcomeEmptyState = () => (
  <div className="text-center py-12 flex flex-col items-center justify-center h-full">
    <div className="text-6xl mb-4 animate-float">🤖</div>
    <h3 className="text-2xl font-semibold text-white mb-2">AI Task Assistant</h3>
    <p className="text-gray-400 mb-8 max-w-md mx-auto">I can create, update, list, and delete tasks for you. Just ask!</p>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto text-left w-full">
      <SuggestionCard>Create a high-priority task to "Deploy the new model by Friday"</SuggestionCard>
      <SuggestionCard>Show me all my completed tasks</SuggestionCard>
      <SuggestionCard>Mark task #12 as "low" priority</SuggestionCard>
      <SuggestionCard>Delete task "Old quarterly report"</SuggestionCard>
    </div>
  </div>
);

const SuggestionCard = ({ children }: { children: React.ReactNode }) => (
  <div className="glass-dark p-4 rounded-lg border border-white/10 hover:bg-white/5 transition-colors cursor-pointer">
    <p className="text-sm text-gray-300">{children}</p>
  </div>
);

const MessageList = ({ messages, loading }: { messages: Message[], loading: boolean }) => (
  <>
    {messages.map(msg => <ChatMessage key={msg.id} message={msg} />)}
    {loading && <LoadingIndicator />}
  </>
);

const ChatMessage = ({ message }: { message: Message }) => (
  <div className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
    <div className={`flex-shrink-0 text-3xl ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
      {message.role === 'user' ? '👤' : '🤖'}
    </div>
    <div className={`max-w-3xl rounded-2xl px-5 py-3 ${message.role === 'user' ? 'order-1 bg-gradient-to-r from-blue-600 to-purple-600' : 'order-2 bg-gray-700/50'}`}>
      <p className="text-base whitespace-pre-wrap break-words">{message.content}</p>
      {message.role === 'assistant' && message.tool_calls && <ToolCallDisplay tool_calls={message.tool_calls} />}
      {message.created_at && <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-100/70' : 'text-gray-400'}`}>{new Date(message.created_at).toLocaleTimeString()}</p>}
  </div>
  </div>
);

const ToolCallDisplay = ({ tool_calls }: { tool_calls: ToolCall[] }) => (
  <div className="mt-4 space-y-3">
    {tool_calls.map((call, idx) => (
      <div key={idx} className="glass-dark border border-white/10 rounded-lg p-3 text-xs">
        <div className="font-semibold text-gray-300 mb-2 flex items-center gap-2">🔧 {call.tool}</div>
        <pre className="text-gray-400 bg-black/20 rounded p-2 overflow-x-auto">{JSON.stringify(call.arguments, null, 2)}</pre>
        {call.result && <pre className="text-green-400 bg-black/20 rounded p-2 mt-2 overflow-x-auto">{JSON.stringify(call.result, null, 2)}</pre>}
      </div>
    ))}
  </div>
);

const LoadingIndicator = () => (
  <div className="flex justify-start">
    <div className="bg-gray-700/50 rounded-2xl px-5 py-3 flex items-center gap-3">
      <div className="text-2xl">🤖</div>
      <div className="flex gap-1.5">
        {[0, 1, 2].map(i => <div key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.1}s` }}></div>)}
      </div>
    </div>
  </div>
);

const ChatInput = ({ input, setInput, handleSubmit, loading }: { input: string, setInput: (val: string) => void, handleSubmit: (e: React.FormEvent) => void, loading: boolean }) => (
  <form onSubmit={handleSubmit} className="flex gap-3 relative z-10">
    <input
      type="text"
      value={input}
      onChange={e => setInput(e.target.value)}
      placeholder="e.g., Create a task to buy groceries..."
      disabled={loading}
      className="flex-1 w-full px-5 py-4 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
    />
    <button type="submit" disabled={loading || !input.trim()} className="btn-primary px-8 py-4 text-base disabled:opacity-50">Send</button>
  </form>
);

export default ChatPage;

