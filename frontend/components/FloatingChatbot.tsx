"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/components/AuthProvider";
import { api } from "@/lib/api";
import { useLanguage } from "@/lib/i18n/LanguageContext";
import { detectLanguage, isMixedLanguage } from "@/lib/languageDetection";

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

interface ConversationListItem {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
  last_message_preview: string | null;
}

type ChatMode = 'floating' | 'sidebar' | 'embedded';

export default function FloatingChatbot() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [chatMode, setChatMode] = useState<ChatMode>('floating');
  const [showHistory, setShowHistory] = useState(false);
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [deletingConvId, setDeletingConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const [voiceInputLang, setVoiceInputLang] = useState<'en-US' | 'ur-PK' | 'fr-FR' | 'ar-SA'>('en-US');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Load chat mode preference from localStorage
  useEffect(() => {
    const savedMode = localStorage.getItem('chatMode') as ChatMode;
    if (savedMode) {
      setChatMode(savedMode);
    }
  }, []);

  // Save chat mode preference to localStorage
  const handleModeChange = (mode: ChatMode) => {
    setChatMode(mode);
    localStorage.setItem('chatMode', mode);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = voiceInputLang;

        recognitionRef.current.onresult = (event: any) => {
          const current = event.resultIndex;
          const transcriptText = event.results[current][0].transcript;
          setTranscript(transcriptText);

          if (event.results[current].isFinal) {
            setInput(transcriptText);
            setIsListening(false);
          }
        };

        recognitionRef.current.onerror = (event: any) => {
          console.error('Speech recognition error:', event.error);
          setIsListening(false);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
  }, [voiceInputLang]); // Re-initialize when language changes

  // Load speech synthesis voices
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      // Load voices (may be async in some browsers)
      const loadVoices = () => {
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
          console.log('Available speech voices:', voices.map(v => `${v.name} (${v.lang})`));
        }
      };

      // Load immediately
      loadVoices();

      // Some browsers fire this event when voices are loaded
      if (window.speechSynthesis.onvoiceschanged !== undefined) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
      }
    }
  }, []);

  const toggleVoiceRecognition = () => {
    if (!recognitionRef.current) {
      alert(t('voice.notSupported'));
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setTranscript("");
      // Update language before starting (in case it changed)
      recognitionRef.current.lang = voiceInputLang;
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const getVoiceLanguageLabel = (lang: string) => {
    switch (lang) {
      case 'en-US': return '🇺🇸 EN';
      case 'ur-PK': return '🇵🇰 اردو';
      case 'fr-FR': return '🇫🇷 FR';
      case 'ar-SA': return '🇸🇦 العربية';
      default: return lang;
    }
  };

  const speakMessage = (text: string, messageId: string) => {
    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    // Check if already speaking this message
    if (speakingMessageId === messageId) {
      setSpeakingMessageId(null);
      return;
    }

    // Check for mixed-language content
    const mixedLangInfo = isMixedLanguage(text);

    // Detect primary language of the text
    const langInfo = detectLanguage(text);

    // Warn user about mixed-language limitations
    if (mixedLangInfo.isMixed) {
      console.warn('Mixed-language content detected:', mixedLangInfo.scripts);
      console.log('Primary language detected:', langInfo.code, langInfo.name);
      console.log('Note: Text-to-speech may only pronounce parts of mixed-language text correctly.');
    }

    // Map language codes to speech synthesis language codes
    const langMap: Record<string, string[]> = {
      ur: ['ur-PK', 'ur-IN', 'ur'],
      ar: ['ar-SA', 'ar-AE', 'ar-EG', 'ar'],
      fr: ['fr-FR', 'fr-CA', 'fr'],
      en: ['en-US', 'en-GB', 'en-AU', 'en']
    };

    // Get available voices
    const voices = window.speechSynthesis.getVoices();

    // Find a voice that matches the detected language
    const preferredLangs = langMap[langInfo.code] || ['en-US'];
    let selectedVoice = null;

    for (const lang of preferredLangs) {
      selectedVoice = voices.find(voice => voice.lang.startsWith(lang));
      if (selectedVoice) break;
    }

    // If no voice found for the language, show a warning and don't speak
    if (!selectedVoice && langInfo.code !== 'en') {
      console.warn(`No voice available for ${langInfo.name}. Available voices:`, voices.map(v => v.lang));
      alert(`Text-to-speech is not available for ${langInfo.name}. Your browser doesn't have voices installed for this language.`);
      return;
    }

    // Use browser Text-to-Speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    utterance.lang = preferredLangs[0]; // Set language

    // Set voice if found
    if (selectedVoice) {
      utterance.voice = selectedVoice;
      console.log(`Using voice: ${selectedVoice.name} (${selectedVoice.lang})`);
    }

    utterance.onstart = () => {
      setSpeakingMessageId(messageId);
      if (mixedLangInfo.isMixed) {
        console.log('⚠️ Mixed-language TTS: Only portions matching the voice language may be spoken correctly.');
      }
    };

    utterance.onend = () => {
      setSpeakingMessageId(null);
    };

    utterance.onerror = (event) => {
      setSpeakingMessageId(null);
      console.error('Speech synthesis error:', event.error);
      if (event.error === 'not-allowed' || event.error === 'language-unavailable') {
        alert(`Text-to-speech failed: ${event.error}. Your browser may not support ${langInfo.name} speech.`);
      }
    };

    window.speechSynthesis.speak(utterance);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !input.trim() || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      // Create conversation if it doesn't exist
      let currentConversationId = conversationId;
      if (!currentConversationId) {
        const convResponse = await api.post('/api/chat/conversations', {
          title: 'Quick Chat'
        });
        currentConversationId = convResponse.id;
        setConversationId(currentConversationId);
      }

      // Send message to conversation
      const response = await api.post(`/api/chat/conversations/${currentConversationId}/messages`, {
        content: userMessage.content,
      });

      const assistantMessage: Message = {
        id: response.id,
        role: response.role,
        content: response.content,
        tool_calls: response.tool_calls?.tool_calls,
        created_at: response.created_at
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      setMessages(prev => prev.filter(msg => msg.id !== userMessage.id));
    } finally {
      setLoading(false);
    }
  };

  const fetchConversations = async () => {
    if (!user) return;

    setLoadingConversations(true);
    try {
      const response = await api.get('/api/chat/conversations', {
        params: { limit: 20 }
      });
      setConversations(response.conversations || []);
    } catch (err) {
      console.error('Failed to fetch conversations:', err);
    } finally {
      setLoadingConversations(false);
    }
  };

  const loadConversation = async (convId: string) => {
    if (!user) return;

    setLoading(true);
    setError(null);
    try {
      const response = await api.get(`/api/chat/conversations/${convId}/messages`);
      setMessages(response.messages || []);
      setConversationId(convId);
      setShowHistory(false); // Close history panel after loading
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load conversation");
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (convId: string) => {
    if (!user) return;

    // Confirm deletion
    if (!confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      return;
    }

    setDeletingConvId(convId);
    try {
      await api.delete(`/api/chat/conversations/${convId}`);

      // Remove from local state
      setConversations(prev => prev.filter(conv => conv.id !== convId));

      // If deleting current conversation, reset chat
      if (conversationId === convId) {
        setMessages([]);
        setConversationId(null);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
      alert(err instanceof Error ? err.message : "Failed to delete conversation");
    } finally {
      setDeletingConvId(null);
    }
  };

  const handleNewConversation = () => {
    if (messages.length > 0 && confirm(t('chat.startNewConversation'))) {
      setMessages([]);
      setConversationId(null);
      setError(null);
      setShowHistory(false);
    }
  };

  // Fetch conversations when history panel is opened
  useEffect(() => {
    if (showHistory && conversations.length === 0) {
      fetchConversations();
    }
  }, [showHistory]);

  if (!user) return null;

  // Reusable chat header component
  const ChatHeader = () => (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-3 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
        <h3 className="text-white font-semibold">{t('chat.title')}</h3>
      </div>
      <div className="flex gap-2">
        {/* Mode Toggle Dropdown */}
        <div className="relative group">
          <button
            className="text-white/80 hover:text-white transition-colors p-1"
            title="Change layout"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="absolute right-0 top-8 bg-gray-800 rounded-lg shadow-xl border border-gray-700 p-2 hidden group-hover:block min-w-[120px] z-10">
            <button
              onClick={() => handleModeChange('floating')}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                chatMode === 'floating' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              🎈 Floating
            </button>
            <button
              onClick={() => handleModeChange('sidebar')}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                chatMode === 'sidebar' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              📌 Sidebar
            </button>
            <button
              onClick={() => handleModeChange('embedded')}
              className={`w-full text-left px-3 py-2 rounded text-sm transition-colors ${
                chatMode === 'embedded' ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              📊 Bottom Bar
            </button>
          </div>
        </div>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className={`transition-colors ${showHistory ? 'text-white' : 'text-white/80 hover:text-white'}`}
          title="Conversation History"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
        <button
          onClick={handleNewConversation}
          className="text-white/80 hover:text-white transition-colors"
          title={t('chat.newConversation')}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </button>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white/80 hover:text-white transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );

  // Get container classes based on mode
  const getContainerClasses = () => {
    switch (chatMode) {
      case 'floating':
        return 'fixed bottom-24 right-6 z-50 w-96 h-[600px] glass-dark rounded-2xl shadow-2xl border border-white/20 flex flex-col overflow-hidden';
      case 'sidebar':
        return 'fixed right-0 top-0 z-50 w-96 h-full glass-dark shadow-2xl border-l border-white/20 flex flex-col overflow-hidden';
      case 'embedded':
        return 'fixed bottom-0 left-0 right-0 z-50 h-96 glass-dark border-t border-white/20 flex flex-col overflow-hidden';
    }
  };

  return (
    <>
      {/* Floating Chat Button (only for floating mode) */}
      {chatMode === 'floating' && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 flex items-center justify-center text-white hover:scale-110 group"
          aria-label={t('chat.openAssistant')}
        >
          {isOpen ? (
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <div className="relative">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
            </div>
          )}
        </button>
      )}

      {/* Sidebar/Embedded Toggle Button */}
      {(chatMode === 'sidebar' || chatMode === 'embedded') && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`fixed z-40 bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl transition-all ${
            chatMode === 'sidebar'
              ? 'right-0 top-20 rounded-l-lg px-3 py-4'
              : 'bottom-0 right-6 rounded-t-lg px-4 py-2'
          }`}
        >
          {isOpen ? (
            chatMode === 'sidebar' ? '→' : '↓'
          ) : (
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              {chatMode === 'embedded' && <span className="text-sm font-medium">Chat</span>}
            </div>
          )}
        </button>
      )}

      {/* Chat Container */}
      {isOpen && (
        <div className={getContainerClasses()}>
          <div className="relative w-full h-full flex flex-col">
            <ChatHeader />

            {/* Conversation History Panel */}
            {showHistory && (
              <div className="absolute inset-0 bg-gray-900/95 z-10 flex flex-col">
              <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                <h3 className="text-white font-semibold">Conversation History</h3>
                <div className="flex gap-2">
                  <button
                    onClick={fetchConversations}
                    className="text-gray-400 hover:text-white transition-colors"
                    title="Refresh"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setShowHistory(false)}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                {loadingConversations ? (
                  <div className="text-center py-8 text-gray-400">Loading conversations...</div>
                ) : conversations.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">No conversations yet</div>
                ) : (
                  <div className="space-y-2">
                    {conversations.map(conv => (
                      <div
                        key={conv.id}
                        className={`relative p-3 rounded-lg transition-colors group ${
                          conversationId === conv.id
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-800 hover:bg-gray-700 text-gray-200'
                        }`}
                      >
                        <button
                          onClick={() => loadConversation(conv.id)}
                          className="w-full text-left"
                          disabled={deletingConvId === conv.id}
                        >
                          <div className="flex justify-between items-start mb-1">
                            <h4 className="font-medium text-sm pr-8">{conv.title}</h4>
                            <span className="text-xs opacity-70">
                              {new Date(conv.updated_at).toLocaleDateString()}
                            </span>
                          </div>
                          {conv.last_message_preview && (
                            <p className="text-xs opacity-80 truncate">{conv.last_message_preview}</p>
                          )}
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs opacity-60">{conv.message_count} messages</span>
                          </div>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteConversation(conv.id);
                          }}
                          disabled={deletingConvId === conv.id}
                          className="absolute top-3 right-3 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/20"
                          title="Delete conversation"
                        >
                          {deletingConvId === conv.id ? (
                            <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                          ) : (
                            <svg className="w-4 h-4 text-red-400 hover:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="px-4 py-2 bg-red-900/50 border-b border-red-700/50">
              <p className="text-xs text-red-300">{error}</p>
            </div>
          )}

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-900/50">
            {messages.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-4xl mb-3 animate-float">🤖</div>
                <p className="text-gray-400 text-sm px-4">
                  {t('chat.greeting')}
                </p>
              </div>
            ) : (
              <>
                {messages.map(msg => {
                  // Detect language and get styling info
                  const langInfo = detectLanguage(msg.content);
                  const isRTL = langInfo.direction === 'rtl';
                  const isUser = msg.role === 'user';

                  return (
                    <div
                      key={msg.id}
                      className={`flex gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`text-2xl ${isUser ? 'order-2' : 'order-1'}`}>
                        {isUser ? '👤' : '🤖'}
                      </div>
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                          isUser
                            ? 'order-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                            : 'order-2 bg-gray-700/50 text-gray-200'
                        }`}
                        dir={langInfo.direction}
                        style={{
                          fontFamily: langInfo.fontFamily,
                          textAlign: isRTL ? 'right' : 'left'
                        }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm whitespace-pre-wrap flex-1">{msg.content}</p>
                          {msg.role === 'assistant' && (
                            <button
                              onClick={() => speakMessage(msg.content, msg.id)}
                              className={`flex-shrink-0 p-1 rounded transition-colors ${
                                speakingMessageId === msg.id
                                  ? 'bg-blue-500/30 text-blue-300'
                                  : 'text-gray-400 hover:text-blue-400 hover:bg-gray-600/50'
                              }`}
                              title={speakingMessageId === msg.id ? "Stop speaking" : "Speak message"}
                            >
                              {speakingMessageId === msg.id ? (
                                <svg className="w-4 h-4 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
                                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                                </svg>
                              ) : (
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 010-7.072m2.828 0a1 1 0 011.414 0 5 5 0 000 7.072 1 1 0 01-1.414 0z" />
                                </svg>
                              )}
                            </button>
                          )}
                        </div>
                        {msg.tool_calls && msg.tool_calls.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-white/10 space-y-1">
                            {msg.tool_calls.map((call, idx) => (
                              <div key={idx} className="text-xs opacity-80">
                                🔧 {call.tool}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-700/50 rounded-2xl px-4 py-2 flex items-center gap-2">
                      <div className="text-xl">🤖</div>
                      <div className="flex gap-1">
                        {[0, 1, 2].map(i => (
                          <div key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.1}s` }}></div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Voice Recognition Feedback */}
          {isListening && (
            <div className="px-4 py-2 bg-red-600/20 border-t border-red-600/30">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                <p className="text-xs text-red-300">{t('voice.listening')} {transcript && `"${transcript}"`}</p>
              </div>
            </div>
          )}

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="p-4 bg-gray-800/50 border-t border-white/10">
            <div className="flex flex-col gap-2">
              {/* Voice Controls Row */}
              <div className="flex gap-2 items-center">
                <select
                  value={voiceInputLang}
                  onChange={(e) => setVoiceInputLang(e.target.value as 'en-US' | 'ur-PK' | 'fr-FR' | 'ar-SA')}
                  className="px-2 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-500 w-20"
                  disabled={loading || isListening}
                  title="Select voice input language"
                >
                  <option value="en-US">🇺🇸 EN</option>
                  <option value="ur-PK">🇵🇰 اردو</option>
                  <option value="fr-FR">🇫🇷 FR</option>
                  <option value="ar-SA">🇸🇦 AR</option>
                </select>
                <button
                  type="button"
                  onClick={toggleVoiceRecognition}
                  className={`p-2 rounded-lg transition-all ${
                    isListening
                      ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                      : 'bg-blue-600 hover:bg-blue-700'
                  } text-white flex-shrink-0`}
                  title={isListening ? t('voice.stopVoiceInput') : t('voice.startVoiceInput')}
                  disabled={loading}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </button>
              </div>

              {/* Text Input Row */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder={t('chat.placeholder')}
                  disabled={loading}
                  className="flex-1 px-3 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg text-sm font-medium hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {t('chat.send')}
                </button>
              </div>
            </div>
          </form>
          </div>
        </div>
      )}

      <style jsx global>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </>
  );
}
