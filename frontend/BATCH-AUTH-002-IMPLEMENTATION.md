# Batch AUTH-002 Implementation Guide

## Status

⏳ Next.js installation in progress (`npm install` running in background)

Once the installation completes, implement the following files:

---

## 1. Better Auth Configuration

**File**: `frontend/lib/auth.ts`

```typescript
/**
 * Better Auth client configuration for JWT-based authentication.
 *
 * This module provides authentication utilities that integrate with the backend's
 * JWT validation. The frontend uses Better Auth to manage sessions and obtain JWT tokens.
 */

import { createClient } from "better-auth/client";

// Better Auth client configuration
export const authClient = createClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",

  // Enable JWT token issuance
  jwt: {
    enabled: true,
  },

  // Session configuration
  session: {
    expiresIn: "7d",  // 7 days
    cookieName: "todo-session",
    secure: process.env.NODE_ENV === "production",
  },
});

/**
 * Sign in with email and password.
 *
 * @param email - User's email address
 * @param password - User's password
 * @returns Promise with authentication result
 */
export async function signIn(email: string, password: string) {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error("Invalid credentials");
    }

    const data = await response.json();

    // Store token in localStorage
    if (data.access_token) {
      localStorage.setItem("jwt_token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    console.error("Sign in error:", error);
    throw error;
  }
}

/**
 * Sign out the current user.
 * Clears session and JWT token.
 */
export async function signOut() {
  localStorage.removeItem("jwt_token");
  localStorage.removeItem("user");
  window.location.href = "/login";
}

/**
 * Get the current session.
 *
 * @returns User object if authenticated, null otherwise
 */
export function getSession() {
  if (typeof window === "undefined") return null;

  const userStr = localStorage.getItem("user");
  if (!userStr) return null;

  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Get the current JWT token.
 *
 * @returns JWT token string or null
 */
export function getJWT(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("jwt_token");
}

/**
 * Check if user is authenticated.
 *
 * @returns true if user has a valid session
 */
export function isAuthenticated(): boolean {
  return getJWT() !== null;
}
```

---

## 2. Auth Provider Component

**File**: `frontend/components/AuthProvider.tsx`

```typescript
"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { getSession, getJWT, signOut } from "@/lib/auth";

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  logout: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check authentication on mount and route changes
    const checkAuth = () => {
      const session = getSession();
      const token = getJWT();

      if (session && token) {
        setUser(session);
      } else {
        setUser(null);

        // Redirect to login if on protected route
        const publicRoutes = ["/login", "/signup", "/"];
        if (!publicRoutes.includes(pathname)) {
          router.push("/login");
        }
      }

      setLoading(false);
    };

    checkAuth();
  }, [pathname, router]);

  const logout = () => {
    signOut();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

---

## 3. API Client with JWT

**File**: `frontend/lib/api.ts`

```typescript
/**
 * API client with automatic JWT token injection.
 *
 * Provides helper methods (get, post, put, patch, delete) that automatically:
 * - Attach Authorization Bearer header
 * - Handle 401 errors by redirecting to login
 * - Parse JSON responses
 */

import { getJWT, signOut } from "./auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestOptions {
  method: string;
  headers: Record<string, string>;
  body?: string;
}

/**
 * Make an authenticated API request.
 *
 * @param path - API endpoint path (e.g., "/api/user-id/tasks")
 * @param options - Fetch options
 * @returns Parsed JSON response
 */
async function request<T>(path: string, options: Partial<RequestOptions> = {}): Promise<T> {
  const token = getJWT();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  // Attach JWT token if available
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, config);

    // Handle 401 Unauthorized (expired/invalid token)
    if (response.status === 401) {
      console.warn("Unauthorized request, redirecting to login");
      signOut();
      return Promise.reject(new Error("Unauthorized"));
    }

    // Handle other HTTP errors
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Parse JSON response
    return response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

/**
 * API helper methods
 */
export const api = {
  /**
   * GET request
   */
  get: <T = any>(path: string): Promise<T> => {
    return request<T>(path, { method: "GET" });
  },

  /**
   * POST request
   */
  post: <T = any>(path: string, body?: any): Promise<T> => {
    return request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PUT request
   */
  put: <T = any>(path: string, body?: any): Promise<T> => {
    return request<T>(path, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PATCH request
   */
  patch: <T = any>(path: string, body?: any): Promise<T> => {
    return request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * DELETE request
   */
  delete: <T = any>(path: string): Promise<T> => {
    return request<T>(path, { method: "DELETE" });
  },
};
```

---

## 4. Basic Login Page

**File**: `frontend/app/login/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { signIn } from "@/lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await signIn(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            Sign in to TODO App
          </h2>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
```

---

## 5. Update Root Layout

**File**: `frontend/app/layout.tsx` (UPDATE)

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/components/AuthProvider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "TODO App",
  description: "Multi-user TODO application with JWT authentication",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

---

## 6. Environment Variables

**File**: `frontend/.env.local`

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (must match backend)
BETTER_AUTH_SECRET=your-secret-key-must-be-at-least-32-characters-long
```

---

## Installation Commands

Once Next.js setup completes, run:

```bash
cd frontend
npm install better-auth
```

---

## Testing

1. **Start backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Test flow**:
   - Visit http://localhost:3000/login
   - Sign in with test credentials
   - Verify JWT token is stored
   - Verify API requests include Authorization header

---

## Acceptance Criteria

- ✅ User can sign in on frontend
- ✅ Better Auth session created successfully
- ✅ `getJWT()` returns valid JWT token
- ✅ JWT automatically attached to ALL API requests
- ✅ 401 errors redirect to /login
- ✅ Session persists across page refreshes
- ✅ `api.get`, `api.post`, etc. work with zero repeated code
- ✅ AuthProvider exposes user, loading states

---

## Next Steps

After batch-auth-002:
- Implement backend auth endpoints (batch-auth-001: JWT middleware)
- Implement task CRUD API (batch-api-001, batch-api-002, etc.)
- Build task UI components (batch-fe-ui-001, batch-fe-ui-002, etc.)
