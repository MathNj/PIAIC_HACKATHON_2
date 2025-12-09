"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";

interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const userId = localStorage.getItem("user_id");
      if (!userId) {
        router.push("/login");
        return;
      }

      const response = await api.get(`/api/${userId}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = () => {
    router.push("/chat");
  };

  const handleOpenConversation = (id: number) => {
    router.push(`/chat?conversation_id=${id}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-lg text-gray-600">Loading conversations...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Conversations
              </h1>
              <p className="mt-2 text-gray-600">Your chat history with the AI assistant</p>
            </div>
            <div className="flex gap-4">
              <button
                onClick={handleNewChat}
                className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-semibold shadow-md hover:shadow-lg transform hover:scale-105 transition-all"
              >
                + New Chat
              </button>
              <button
                onClick={() => router.push("/dashboard")}
                className="px-6 py-3 bg-white text-gray-700 rounded-lg font-semibold shadow-md hover:shadow-lg transform hover:scale-105 transition-all border border-gray-200"
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Conversations List */}
        {conversations.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <div className="text-gray-400 text-6xl mb-4">💬</div>
            <h3 className="text-2xl font-bold text-gray-700 mb-2">No conversations yet</h3>
            <p className="text-gray-500 mb-6">Start a new chat to get help managing your tasks</p>
            <button
              onClick={handleNewChat}
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg font-semibold shadow-md hover:shadow-xl transform hover:scale-105 transition-all"
            >
              Start Your First Chat
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => handleOpenConversation(conv.id)}
                className="bg-white rounded-xl shadow-md p-6 cursor-pointer hover:shadow-xl transform hover:scale-[1.02] transition-all border border-gray-100 hover:border-purple-200"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">
                      {conv.title}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>
                        Created: {new Date(conv.created_at).toLocaleDateString()}
                      </span>
                      <span>•</span>
                      <span>
                        Last updated: {new Date(conv.updated_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  <div className="text-purple-500">
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
