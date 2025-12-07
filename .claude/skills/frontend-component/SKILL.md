---
name: "frontend-component"
description: "Builds Next.js 16+ App Router components with TypeScript, Tailwind CSS, and proper API integration. Use for UI implementation tasks in Phase II/III."
version: "2.0.0"
---

# Frontend Component Skill

## When to Use
- User asks to "build the UI" or "create a component"
- User says "Make a form for..." or "Implement the frontend"
- After backend API is ready
- Phase II/III frontend development

## Context
This skill implements frontend features following:
- **Project Structure**: See `@frontend/CLAUDE.md`
- **Tech Stack**: Next.js 16+ (App Router), TypeScript, Tailwind CSS, React hooks
- **API Client**: Use `lib/tasks-api.ts` pattern (centralized API calls)
- **Authentication**: JWT tokens via `AuthProvider` context
- **Styling**: Tailwind CSS utilities only (no inline styles or CSS files)

## Workflow
1. **Read Spec**: Read `@specs/features/[feature-name].md` for UI requirements
2. **Type Definitions**: Create TypeScript interfaces in `lib/types.ts` matching backend schemas
3. **API Client**: Create API methods in `lib/[feature]-api.ts` using centralized pattern
4. **Component Structure**: Build components with proper client/server component separation
5. **State Management**: Handle loading, error, and success states
6. **Authentication Integration**: Use `useAuth()` hook for user context
7. **Styling**: Apply Tailwind CSS with mobile-first approach
8. **Error Handling**: Display user-friendly error messages

## Output Format

### 1. Type Definitions: `frontend/lib/types.ts`
```typescript
/**
 * [Feature] type definitions.
 *
 * These types match the backend Pydantic schemas.
 */

export interface [Feature] {
  id: number;
  user_id: string;
  [field]: [type];
  created_at: string;  // ISO 8601 datetime string
  updated_at: string;  // ISO 8601 datetime string
}

export interface [Feature]CreateInput {
  [field]: [type];
  // user_id extracted from JWT, not provided here
}

export interface [Feature]UpdateInput {
  [field]?: [type];  // All fields optional for partial updates
}

export interface [Feature]ListParams {
  status?: "all" | "[value1]" | "[value2]";
  sort?: "created" | "updated" | "[field]";
}
```

### 2. API Client: `frontend/lib/[feature]-api.ts`
```typescript
/**
 * API client for [Feature] operations.
 *
 * Centralizes all backend communication with proper error handling.
 */

import type { [Feature], [Feature]CreateInput, [Feature]UpdateInput, [Feature]ListParams } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get authentication token from localStorage.
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

/**
 * Make authenticated API request.
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const [feature]Api = {
  /**
   * List all [features] for a user.
   */
  async list(userId: string, params?: [Feature]ListParams): Promise<[Feature][]> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append("status", params.status);
    if (params?.sort) queryParams.append("sort", params.sort);

    const query = queryParams.toString();
    const endpoint = `/api/${userId}/[features]${query ? `?${query}` : ""}`;

    return apiRequest<[Feature][]>(endpoint);
  },

  /**
   * Get a single [feature] by ID.
   */
  async getById(userId: string, [feature]Id: number): Promise<[Feature]> {
    return apiRequest<[Feature]>(`/api/${userId}/[features]/${[feature]Id}`);
  },

  /**
   * Create a new [feature].
   */
  async create(userId: string, data: [Feature]CreateInput): Promise<[Feature]> {
    return apiRequest<[Feature]>(`/api/${userId}/[features]`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Update an existing [feature].
   */
  async update(
    userId: string,
    [feature]Id: number,
    data: [Feature]UpdateInput
  ): Promise<[Feature]> {
    return apiRequest<[Feature]>(`/api/${userId}/[features]/${[feature]Id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a [feature].
   */
  async delete(userId: string, [feature]Id: number): Promise<void> {
    await apiRequest<{ detail: string }>(`/api/${userId}/[features]/${[feature]Id}`, {
      method: "DELETE",
    });
  },
};
```

### 3. Main Component: `frontend/app/[feature]/page.tsx`
```typescript
"use client";

/**
 * [Feature] Page
 *
 * Displays and manages [features] for the authenticated user.
 */

import { useState, useEffect } from "react";
import { useAuth } from "@/components/AuthProvider";
import { [feature]Api } from "@/lib/[feature]-api";
import type { [Feature], [Feature]CreateInput } from "@/lib/types";

export default function [Feature]Page() {
  const { user } = useAuth();
  const [[features], set[Features]] = useState<[Feature][]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create dialog state
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newData, setNewData] = useState<[Feature]CreateInput>({
    [field]: "",
  });
  const [creating, setCreating] = useState(false);

  // Fetch [features] on mount
  useEffect(() => {
    if (!user) return;

    const fetch[Features] = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await [feature]Api.list(user.id);
        set[Features](data);
      } catch (err) {
        console.error("Failed to fetch [features]:", err);
        setError(err instanceof Error ? err.message : "Failed to load [features]");
      } finally {
        setLoading(false);
      }
    };

    fetch[Features]();
  }, [user]);

  // Create handler
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    try {
      setCreating(true);
      setError(null);

      const new[Feature] = await [feature]Api.create(user.id, newData);
      set[Features]([...[features], new[Feature]]);

      // Reset form
      setNewData({ [field]: "" });
      setShowCreateDialog(false);
    } catch (err) {
      console.error("Failed to create [feature]:", err);
      setError(err instanceof Error ? err.message : "Failed to create [feature]");
    } finally {
      setCreating(false);
    }
  };

  // Delete handler
  const handleDelete = async ([feature]Id: number) => {
    if (!user) return;
    if (!confirm("Are you sure you want to delete this [feature]?")) return;

    try {
      setError(null);
      await [feature]Api.delete(user.id, [feature]Id);
      set[Features]([features].filter(t => t.id !== [feature]Id));
    } catch (err) {
      console.error("Failed to delete [feature]:", err);
      setError(err instanceof Error ? err.message : "Failed to delete [feature]");
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              [Features]
            </h1>
            <button
              onClick={() => setShowCreateDialog(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Create [Feature]
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Message */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="flex justify-center py-12">
            <p className="text-gray-600">Loading [features]...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && [features].length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No [features] yet</p>
            <button
              onClick={() => setShowCreateDialog(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Create your first [feature]
            </button>
          </div>
        )}

        {/* [Features] Grid */}
        {!loading && [features].length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[features].map(([feature]) => (
              <div
                key={[feature].id}
                className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {[feature].[field]}
                  </h3>
                  <button
                    onClick={() => handleDelete([feature].id)}
                    className="text-red-600 hover:text-red-800 text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
                <p className="text-sm text-gray-500">
                  Created: {new Date([feature].created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Create [Feature]
            </h2>

            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  [Field Label]
                </label>
                <input
                  type="text"
                  value={newData.[field]}
                  onChange={(e) => setNewData({ ..newData, [field]: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter [field]"
                  required
                />
              </div>

              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreateDialog(false)}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={creating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                  disabled={creating}
                >
                  {creating ? "Creating..." : "Create"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
```

## Component Patterns

### Client vs Server Components
```typescript
// Server Component (default) - Use for static content, data fetching
export default function Layout({ children }) {
  return <div>{children}</div>;
}

// Client Component - Use for interactivity, hooks, browser APIs
"use client";
import { useState } from "react";

export default function InteractiveComponent() {
  const [state, setState] = useState(0);
  return <button onClick={() => setState(state + 1)}>{state}</button>;
}
```

### Authentication Integration
```typescript
"use client";
import { useAuth } from "@/components/AuthProvider";

export default function ProtectedComponent() {
  const { user, signOut } = useAuth();

  if (!user) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <p>Welcome, {user.name}!</p>
      <button onClick={signOut}>Sign Out</button>
    </div>
  );
}
```

### Error Handling
```typescript
try {
  const data = await [feature]Api.create(userId, input);
  // Success handling
} catch (err) {
  console.error("Operation failed:", err);
  setError(err instanceof Error ? err.message : "Unknown error");
}
```

## Tailwind CSS Patterns

### Common Utilities
```typescript
// Buttons
<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
  Primary Button
</button>

// Cards
<div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
  Card Content
</div>

// Forms
<input
  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
/>

// Gradients
<div className="bg-gradient-to-br from-blue-50 via-white to-purple-50">
  Gradient Background
</div>

// Responsive Grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  Grid Items
</div>
```

## Post-Implementation Steps
1. **Test Component**: Verify in browser at http://localhost:3000
2. **Check Responsiveness**: Test mobile, tablet, desktop views
3. **Verify API Integration**: Ensure CRUD operations work
4. **Error States**: Test with network errors, invalid data
5. **Create PHR**: Document the implementation
   - Title: "[Feature] Frontend Implementation"
   - Stage: `green`
   - Feature: `[feature-name]`

## Example
**Input**: "Build UI for tagging system"

**Output**:
- `frontend/lib/types.ts` - Tag, TagCreateInput, TagUpdateInput interfaces
- `frontend/lib/tag-api.ts` - API client with list, create, update, delete methods
- `frontend/app/tags/page.tsx` - Tags page component with CRUD UI
- Color picker component for tag colors
- Tag filter chips on dashboard
- Proper error handling and loading states

## Quality Checklist
Before finalizing:
- [ ] All components marked "use client" if using hooks
- [ ] Types match backend Pydantic schemas exactly
- [ ] API client uses centralized pattern from `lib/[feature]-api.ts`
- [ ] Authentication integrated with useAuth() hook
- [ ] Loading, error, and empty states handled
- [ ] Tailwind CSS only (no inline styles or CSS files)
- [ ] Mobile-first responsive design
- [ ] User-friendly error messages
- [ ] Confirmation dialogs for destructive actions
- [ ] Forms have proper validation
- [ ] Accessibility: keyboard navigation, ARIA labels
