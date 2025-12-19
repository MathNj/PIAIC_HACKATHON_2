# Next.js OpenAI Integration Patterns

Complete guide for integrating OpenAI API into Next.js 14+ App Router applications with TypeScript, streaming, and proper patterns.

## Project Setup

### 1. Install Dependencies

```bash
npm install openai
npm install @types/node --save-dev
```

### 2. Environment Variables

Create `.env.local`:
```bash
OPENAI_API_KEY=sk-...
```

**IMPORTANT**: Never expose API keys in client-side code! Always use API routes or server actions.

### 3. OpenAI Client (Server-Side)

```typescript
// lib/openai.ts
import OpenAI from 'openai';

export const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});
```

## Pattern 1: API Route with Non-Streaming

### Server-Side API Route

```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { openai } from '@/lib/openai';

export const runtime = 'edge'; // Use Edge Runtime for better performance

interface ChatRequest {
  message: string;
  conversationId?: string;
}

export async function POST(request: NextRequest) {
  try {
    const { message }: ChatRequest = await request.json();

    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: message }
      ],
      max_tokens: 500,
      temperature: 0.7
    });

    const assistantMessage = response.choices[0].message.content;

    return NextResponse.json({
      message: assistantMessage,
      tokens: response.usage?.total_tokens
    });

  } catch (error) {
    console.error('OpenAI API error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
```

### Client Component

```typescript
// components/ChatSimple.tsx
'use client';

import { useState } from 'react';

export default function ChatSimple() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      const data = await res.json();
      setResponse(data.message);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="w-full p-3 border rounded-lg"
          rows={4}
        />
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-400"
        >
          {loading ? 'Sending...' : 'Send'}
        </button>
      </form>

      {response && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
```

## Pattern 2: Streaming API Route

### Streaming API Route

```typescript
// app/api/chat/stream/route.ts
import { NextRequest } from 'next/server';
import { openai } from '@/lib/openai';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  const { message } = await request.json();

  const stream = await openai.chat.completions.create({
    model: 'gpt-4',
    messages: [
      { role: 'system', content: 'You are a helpful assistant.' },
      { role: 'user', content: message }
    ],
    stream: true
  });

  // Create a ReadableStream
  const encoder = new TextEncoder();
  const readable = new ReadableStream({
    async start(controller) {
      try {
        for await (const chunk of stream) {
          const content = chunk.choices[0]?.delta?.content || '';
          if (content) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({ content })}\n\n`));
          }
        }
        controller.enqueue(encoder.encode('data: [DONE]\n\n'));
        controller.close();
      } catch (error) {
        controller.error(error);
      }
    }
  });

  return new Response(readable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  });
}
```

### Streaming Client Component

```typescript
// components/ChatStreaming.tsx
'use client';

import { useState, useRef } from 'react';

export default function ChatStreaming() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
        signal: abortControllerRef.current.signal
      });

      if (!res.ok) throw new Error('Request failed');

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') break;

            try {
              const parsed = JSON.parse(data);
              setResponse((prev) => prev + parsed.content);
            } catch (e) {
              // Ignore parsing errors
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        console.error('Error:', error);
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleCancel = () => {
    abortControllerRef.current?.abort();
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="w-full p-3 border rounded-lg"
          rows={4}
        />
        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-400"
          >
            {loading ? 'Streaming...' : 'Send'}
          </button>
          {loading && (
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 bg-red-600 text-white rounded-lg"
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      {response && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg whitespace-pre-wrap">
          {response}
        </div>
      )}
    </div>
  );
}
```

## Pattern 3: Server Actions (Next.js 14+)

### Server Action

```typescript
// app/actions/chat.ts
'use server';

import { openai } from '@/lib/openai';

export async function chatAction(message: string) {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: message }
      ]
    });

    return {
      success: true,
      message: response.choices[0].message.content,
      tokens: response.usage?.total_tokens
    };
  } catch (error) {
    return {
      success: false,
      error: 'Failed to process request'
    };
  }
}
```

### Client Component with Server Action

```typescript
// components/ChatServerAction.tsx
'use client';

import { useState, useTransition } from 'react';
import { chatAction } from '@/app/actions/chat';

export default function ChatServerAction() {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    startTransition(async () => {
      const result = await chatAction(message);
      if (result.success) {
        setResponse(result.message || '');
      } else {
        console.error(result.error);
      }
    });
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          className="w-full p-3 border rounded-lg"
          rows={4}
        />
        <button
          type="submit"
          disabled={isPending}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-400"
        >
          {isPending ? 'Sending...' : 'Send'}
        </button>
      </form>

      {response && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <p>{response}</p>
        </div>
      )}
    </div>
  );
}
```

## Pattern 4: Conversation History with Database

### TypeScript Types

```typescript
// types/chat.ts
export interface Message {
  id: number;
  conversationId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
}

export interface Conversation {
  id: number;
  title: string;
  createdAt: string;
  messages: Message[];
}
```

### API Route with History

```typescript
// app/api/conversations/[id]/messages/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { openai } from '@/lib/openai';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { message } = await request.json();
    const conversationId = parseInt(params.id);

    // Load conversation history from database
    const history = await fetch(`${process.env.API_URL}/conversations/${conversationId}/messages`)
      .then(res => res.json());

    // Build messages array
    const messages = [
      { role: 'system', content: 'You are a helpful assistant.' },
      ...history.messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content
      })),
      { role: 'user', content: message }
    ];

    // Call OpenAI
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: messages as any
    });

    const assistantMessage = response.choices[0].message.content;

    // Save messages to database
    await fetch(`${process.env.API_URL}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: [
          { role: 'user', content: message },
          { role: 'assistant', content: assistantMessage }
        ]
      })
    });

    return NextResponse.json({
      message: assistantMessage,
      tokens: response.usage?.total_tokens
    });

  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
```

### Chat Component with History

```typescript
// components/ChatWithHistory.tsx
'use client';

import { useState, useEffect } from 'react';
import { Message } from '@/types/chat';

interface Props {
  conversationId: number;
}

export default function ChatWithHistory({ conversationId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Load conversation history
  useEffect(() => {
    fetch(`/api/conversations/${conversationId}/messages`)
      .then(res => res.json())
      .then(data => setMessages(data.messages));
  }, [conversationId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Add user message optimistically
    const userMessage: Message = {
      id: Date.now(),
      conversationId,
      role: 'user',
      content: input,
      createdAt: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const res = await fetch(`/api/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      });

      const data = await res.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now() + 1,
        conversationId,
        role: 'assistant',
        content: data.message,
        createdAt: new Date().toISOString()
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-4 rounded-lg ${
              msg.role === 'user'
                ? 'bg-blue-100 ml-auto max-w-[80%]'
                : 'bg-gray-100 mr-auto max-w-[80%]'
            }`}
          >
            <p className="text-sm font-semibold mb-1">
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </p>
            <p className="whitespace-pre-wrap">{msg.content}</p>
          </div>
        ))}
        {loading && (
          <div className="bg-gray-100 p-4 rounded-lg max-w-[80%]">
            <p className="animate-pulse">Thinking...</p>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 p-3 border rounded-lg"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg disabled:bg-gray-400"
        >
          Send
        </button>
      </form>
    </div>
  );
}
```

## Pattern 5: OpenAI Chatkit Integration

### Install Chatkit

```bash
npm install @openai/chatkit
```

### Chatkit Configuration

```typescript
// lib/chatkit.ts
import { ChatKitProvider } from '@openai/chatkit';

export const chatkitConfig = {
  apiKey: process.env.OPENAI_API_KEY!,
  model: 'gpt-4',
  systemPrompt: 'You are a helpful assistant.',
};
```

### Chatkit Component

```typescript
// components/ChatKitComponent.tsx
'use client';

import { ChatKitProvider, Chat } from '@openai/chatkit';
import { chatkitConfig } from '@/lib/chatkit';

export default function ChatKitComponent() {
  return (
    <ChatKitProvider config={chatkitConfig}>
      <Chat
        className="h-screen"
        placeholder="Type your message..."
        welcomeMessage="Hello! How can I help you today?"
      />
    </ChatKitProvider>
  );
}
```

## Pattern 6: Error Handling

### API Route with Error Handling

```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { openai } from '@/lib/openai';

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();

    // Validate input
    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Invalid message' },
        { status: 400 }
      );
    }

    if (message.length > 4000) {
      return NextResponse.json(
        { error: 'Message too long' },
        { status: 400 }
      );
    }

    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a helpful assistant.' },
        { role: 'user', content: message }
      ]
    });

    return NextResponse.json({
      message: response.choices[0].message.content
    });

  } catch (error: any) {
    console.error('OpenAI API error:', error);

    // Handle specific OpenAI errors
    if (error?.status === 401) {
      return NextResponse.json(
        { error: 'Invalid API key' },
        { status: 401 }
      );
    }

    if (error?.status === 429) {
      return NextResponse.json(
        { error: 'Rate limit exceeded. Please try again later.' },
        { status: 429 }
      );
    }

    if (error?.status === 500) {
      return NextResponse.json(
        { error: 'OpenAI service error. Please try again.' },
        { status: 500 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to process request' },
      { status: 500 }
    );
  }
}
```

### Client-Side Error Handling

```typescript
// hooks/useChat.ts
import { useState } from 'react';

interface ChatError {
  message: string;
  code?: string;
}

export function useChat() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ChatError | null>(null);

  const sendMessage = async (message: string) => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Request failed');
      }

      const data = await res.json();
      return data.message;

    } catch (err: any) {
      const errorMessage = err.message || 'An unexpected error occurred';
      setError({ message: errorMessage });
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { sendMessage, loading, error };
}
```

## Pattern 7: Rate Limiting

### Client-Side Rate Limiting

```typescript
// hooks/useRateLimitedChat.ts
import { useState, useRef } from 'react';

const RATE_LIMIT_INTERVAL = 60000; // 1 minute
const MAX_REQUESTS = 10;

export function useRateLimitedChat() {
  const [requestCount, setRequestCount] = useState(0);
  const [resetTime, setResetTime] = useState(Date.now() + RATE_LIMIT_INTERVAL);

  const sendMessage = async (message: string) => {
    // Check rate limit
    if (Date.now() > resetTime) {
      setRequestCount(0);
      setResetTime(Date.now() + RATE_LIMIT_INTERVAL);
    }

    if (requestCount >= MAX_REQUESTS) {
      const waitTime = Math.ceil((resetTime - Date.now()) / 1000);
      throw new Error(`Rate limit exceeded. Please wait ${waitTime} seconds.`);
    }

    setRequestCount(prev => prev + 1);

    // Send message
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message })
    });

    return res.json();
  };

  return { sendMessage, requestCount, maxRequests: MAX_REQUESTS };
}
```

## Testing

### API Route Tests

```typescript
// __tests__/api/chat.test.ts
import { POST } from '@/app/api/chat/route';
import { NextRequest } from 'next/server';

jest.mock('@/lib/openai');

describe('/api/chat', () => {
  it('should return chat response', async () => {
    const request = new NextRequest('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: 'Hello' })
    });

    const response = await POST(request);
    const data = await response.json();

    expect(response.status).toBe(200);
    expect(data).toHaveProperty('message');
  });

  it('should handle invalid input', async () => {
    const request = new NextRequest('http://localhost/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message: '' })
    });

    const response = await POST(request);
    expect(response.status).toBe(400);
  });
});
```

## Production Checklist

- [ ] API keys in environment variables (not client-side code)
- [ ] Input validation (length, format)
- [ ] Error handling for all API calls
- [ ] Rate limiting implemented
- [ ] Timeouts configured
- [ ] Logging and monitoring set up
- [ ] Streaming responses tested
- [ ] CORS configured properly
- [ ] Cost tracking enabled
- [ ] Security headers added
