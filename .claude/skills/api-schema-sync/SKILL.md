---
name: "api-schema-sync"
description: "Synchronizes API contracts between FastAPI backend (Pydantic) and Next.js frontend (TypeScript). Handles type conversions, validates schema alignment, and fixes integration issues."
version: "1.0.0"
---

# API Schema Sync Skill

## When to Use
- User reports "type mismatch" or "validation error" between frontend and backend
- Backend schema changed and frontend needs updating
- Error shows "Input should be a valid integer, unable to parse string"
- Frontend expects different field names than backend returns
- Adding new API endpoints or updating existing contracts
- Frontend build errors about missing TypeScript types

## Context
This skill handles frontend-backend schema synchronization following:
- **Backend**: FastAPI 0.95.2, Pydantic v2 (validation), SQLModel (ORM)
- **Frontend**: Next.js 16+ (TypeScript), Fetch API
- **Serialization**: JSON (API communication)
- **Authentication**: JWT in Authorization header
- **Common Issues**:
  - Field name mismatches (priority vs priority_id)
  - Type conversions (UUID ↔ string, datetime ↔ ISO string)
  - Optional/nullable field handling
  - Enum vs literal types

## Workflow
1. **Identify Mismatch**: Find discrepancy between backend schema and frontend types
2. **Check Backend Schema**: Read Pydantic schemas in `backend/app/schemas/`
3. **Check Frontend Types**: Read TypeScript types in `frontend/lib/types.ts`
4. **Determine Source of Truth**: Backend Pydantic schema is authoritative
5. **Update Frontend Types**: Align TypeScript interfaces with Pydantic models
6. **Add Conversion Helpers**: Create functions for complex type mappings
7. **Test Integration**: Verify API calls work end-to-end
8. **Update Components**: Update React components using the types

## Output Formats

### 1. Type Synchronization (Backend → Frontend)

**Backend Pydantic Schema** (`backend/app/schemas/task.py`):
```python
"""Task Pydantic schemas for API validation."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskRead(BaseModel):
    """
    Task response schema.

    This is what the backend API returns.
    """
    id: int
    user_id: str  # UUID serialized as string
    title: str
    description: Optional[str] = None
    completed: bool
    priority_id: Optional[int] = None  # FK to priorities table (1=High, 2=Normal, 3=Low)
    due_date: Optional[str] = None  # ISO 8601 datetime string
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    tag_ids: list[int] = []
    created_at: str  # ISO 8601 datetime
    updated_at: str  # ISO 8601 datetime

    class Config:
        orm_mode = True
```

**Frontend TypeScript Type** (`frontend/lib/types.ts`):
```typescript
/**
 * Task type matching backend TaskRead schema.
 *
 * IMPORTANT: Keep in sync with backend/app/schemas/task.py
 */
export interface Task {
  id: number;
  user_id: string;  // UUID string
  title: string;
  description?: string | null;  // Optional in API
  completed: boolean;
  priority_id?: number | null;  // Integer FK (1=High, 2=Normal, 3=Low)
  due_date?: string | null;  // ISO 8601 datetime string
  is_recurring: boolean;
  recurrence_pattern?: string | null;
  tag_ids: number[];
  created_at: string;  // ISO 8601 datetime
  updated_at: string;
}
```

### 2. Handling Type Conversions

**Priority Conversion Helpers** (`frontend/lib/types.ts`):
```typescript
/**
 * Priority display types (for UI).
 *
 * Backend stores as integer ID, frontend displays as string.
 */
export type TaskPriority = "high" | "normal" | "low";

/**
 * Map priority ID (backend) to display string (frontend).
 */
export const PRIORITY_ID_MAP: { [key: number]: TaskPriority } = {
  1: "high",
  2: "normal",
  3: "low",
};

/**
 * Map display string to priority ID.
 */
export const PRIORITY_STRING_TO_ID: { [key in TaskPriority]: number } = {
  high: 1,
  normal: 2,
  low: 3,
};

/**
 * Convert priority_id (backend integer) to display string.
 *
 * @param priority_id - Priority ID from backend (1, 2, 3, or null)
 * @returns Priority string for UI ("high" | "normal" | "low")
 */
export function getPriorityString(priority_id?: number | null): TaskPriority {
  if (!priority_id || !PRIORITY_ID_MAP[priority_id]) {
    return "normal";  // Default fallback
  }
  return PRIORITY_ID_MAP[priority_id];
}

/**
 * Convert priority string (UI) to priority_id (backend).
 *
 * @param priority - Priority string from UI
 * @returns Priority ID for backend API
 */
export function getPriorityId(priority: TaskPriority): number {
  return PRIORITY_STRING_TO_ID[priority];
}
```

**Date Conversion Helpers** (`frontend/lib/utils.ts`):
```typescript
/**
 * Format ISO datetime string for display.
 *
 * @param isoString - ISO 8601 datetime from backend
 * @returns Formatted date string (e.g., "Dec 12, 2025")
 */
export function formatDate(isoString?: string | null): string {
  if (!isoString) return "No date";

  const date = new Date(isoString);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

/**
 * Convert Date object to ISO string for backend.
 *
 * @param date - JavaScript Date object
 * @returns ISO 8601 string for backend API
 */
export function dateToISO(date: Date): string {
  return date.toISOString();
}
```

### 3. API Client Type Safety

**Typed API Client** (`frontend/lib/api.ts`):
```typescript
import { getJWT, signOut } from "./auth";
import type { Task } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  || (process.env.NODE_ENV === "production"
    ? "https://backend-production-url.com"
    : "http://localhost:8000");

/**
 * Generic request wrapper with type safety.
 *
 * @param path - API endpoint path
 * @param options - Fetch options
 * @returns Typed response data
 */
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
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
      signOut();
      if (typeof window !== "undefined") {
        window.location.href = "/login?session_expired=true";
      }
      return Promise.reject(new Error("Unauthorized - session expired"));
    }

    // Handle 422 Validation Error (Pydantic)
    if (response.status === 422) {
      const errorData = await response.json();
      if (Array.isArray(errorData.detail)) {
        const errorMessages = errorData.detail.map((err: any) => {
          const field = err.loc.slice(1).join(".");
          return `${field}: ${err.msg}`;
        }).join(", ");
        throw new Error(errorMessages);
      }
      throw new Error(errorData.detail || "Validation failed");
    }

    // Handle other errors
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

/**
 * Typed API methods.
 */
export const api = {
  get: <T = any>(path: string): Promise<T> => request<T>(path, { method: "GET" }),

  post: <T = any>(path: string, body?: any): Promise<T> =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }),

  put: <T = any>(path: string, body?: any): Promise<T> =>
    request<T>(path, { method: "PUT", body: body ? JSON.stringify(body) : undefined }),

  patch: <T = any>(path: string, body?: any): Promise<T> =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }),

  delete: <T = any>(path: string): Promise<T> => request<T>(path, { method: "DELETE" }),
};

/**
 * Task API methods with full type safety.
 */
export const taskApi = {
  /**
   * Get all tasks for a user.
   */
  list: async (userId: string): Promise<Task[]> => {
    return api.get<Task[]>(`/api/${userId}/tasks?status=all&sort=created`);
  },

  /**
   * Create a new task.
   */
  create: async (userId: string, data: Partial<Task>): Promise<Task> => {
    return api.post<Task>(`/api/${userId}/tasks`, data);
  },

  /**
   * Update an existing task.
   */
  update: async (userId: string, taskId: number, data: Partial<Task>): Promise<Task> => {
    return api.put<Task>(`/api/${userId}/tasks/${taskId}`, data);
  },

  /**
   * Delete a task.
   */
  delete: async (userId: string, taskId: number): Promise<void> => {
    return api.delete(`/api/${userId}/tasks/${taskId}`);
  },
};
```

### 4. Component Integration

**Using Types in Components** (`frontend/app/dashboard/page.tsx`):
```typescript
"use client";

import { useState, useEffect } from "react";
import { taskApi } from "@/lib/api";
import { getPriorityString, formatDate } from "@/lib/utils";
import type { Task } from "@/lib/types";

export default function Dashboard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const userId = localStorage.getItem("user_id");
      if (!userId) throw new Error("No user ID found");

      const data = await taskApi.list(userId);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading tasks...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onUpdate={loadTasks}
        />
      ))}
    </div>
  );
}

interface TaskCardProps {
  task: Task;
  onUpdate: () => void;
}

function TaskCard({ task, onUpdate }: TaskCardProps) {
  // Type-safe access to task properties
  const priority = getPriorityString(task.priority_id);  // Convert integer to string
  const dueDate = formatDate(task.due_date);  // Format ISO datetime

  return (
    <div>
      <h3>{task.title}</h3>
      {task.description && <p>{task.description}</p>}
      <span>Priority: {priority}</span>
      <span>Due: {dueDate}</span>
      <span>Recurring: {task.is_recurring ? "Yes" : "No"}</span>
    </div>
  );
}
```

## Common Integration Issues

### Issue 1: Field Name Mismatch

**Problem**: Backend returns `priority_id`, frontend expects `priority`

**Backend Schema**:
```python
# backend/app/schemas/task.py
class TaskRead(BaseModel):
    priority_id: Optional[int] = None  # Backend returns integer ID
```

**Frontend Type (WRONG)**:
```typescript
// frontend/lib/types.ts ❌ WRONG
interface Task {
  priority: "low" | "normal" | "high";  // Backend doesn't return this!
}
```

**Fix**:
```typescript
// frontend/lib/types.ts ✅ CORRECT
interface Task {
  priority_id?: number | null;  // Matches backend exactly
}

// Add conversion helper for display
const priority = getPriorityString(task.priority_id);  // "high" | "normal" | "low"
```

### Issue 2: Optional vs Required Fields

**Backend Schema**:
```python
class TaskRead(BaseModel):
    description: Optional[str] = None  # Can be null
    completed: bool  # Required, never null
```

**Frontend Type**:
```typescript
interface Task {
  description?: string | null;  // Optional AND nullable
  completed: boolean;  // Required, always present
}
```

### Issue 3: Array vs List Types

**Backend Schema**:
```python
class TaskRead(BaseModel):
    tag_ids: list[int] = []  # Empty list by default
```

**Frontend Type (WRONG)**:
```typescript
// ❌ WRONG - May be undefined
interface Task {
  tag_ids?: number[];
}
```

**Frontend Type (CORRECT)**:
```typescript
// ✅ CORRECT - Always array (empty or populated)
interface Task {
  tag_ids: number[];
}
```

### Issue 4: Date Serialization

**Backend Schema**:
```python
from datetime import datetime

class TaskRead(BaseModel):
    created_at: str  # SQLModel datetime serialized to ISO 8601 string

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()  # datetime → "2025-12-12T10:00:00Z"
        }
```

**Frontend Type**:
```typescript
interface Task {
  created_at: string;  // ISO 8601 datetime string

  // NOT Date object! Backend sends string
}

// Convert to Date when needed
const createdDate = new Date(task.created_at);
```

## Validation Error Handling

### Parsing FastAPI 422 Errors

**Backend Error Response**:
```json
{
  "detail": [
    {
      "loc": ["body", "priority_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "type": "int_parsing",
      "input": "high"
    }
  ]
}
```

**Frontend Error Parser** (`frontend/lib/api.ts`):
```typescript
// Already in api.ts request() function
if (response.status === 422) {
  const errorData = await response.json();
  if (Array.isArray(errorData.detail)) {
    const errorMessages = errorData.detail.map((err: any) => {
      const field = err.loc.slice(1).join(".");  // Remove "body" prefix
      return `${field}: ${err.msg}`;
    }).join(", ");
    throw new Error(errorMessages);  // "priority_id: Input should be a valid integer..."
  }
  throw new Error(errorData.detail || "Validation failed");
}
```

## Schema Sync Checklist

When backend schema changes:
- [ ] Update `frontend/lib/types.ts` interfaces to match Pydantic schemas
- [ ] Update API client method signatures (`frontend/lib/api.ts`)
- [ ] Add/remove fields in form components
- [ ] Update validation logic in forms
- [ ] Test all affected API calls (create, read, update)
- [ ] Update mock data for tests
- [ ] Document breaking changes in PR description

When adding new endpoints:
- [ ] Add TypeScript interface for request body
- [ ] Add TypeScript interface for response
- [ ] Add method to `api` object with type annotations
- [ ] Document endpoint in API reference
- [ ] Add error handling for 422 validation errors
- [ ] Test with real backend before deploying

## Example Usage

**Scenario**: Backend changed `priority: string` → `priority_id: int`, frontend breaks

**Steps**:
1. Check backend schema: `backend/app/schemas/task.py` → `priority_id: Optional[int]`
2. Update frontend type: `frontend/lib/types.ts` → Change `priority: string` to `priority_id?: number | null`
3. Add conversion helpers: Create `getPriorityString(priority_id)` and `PRIORITY_ID_MAP`
4. Update components: Replace `task.priority` with `getPriorityString(task.priority_id)`
5. Update forms: Use `getPriorityId(selectedPriority)` when submitting
6. Test API: Create task with `priority_id: 1`, verify backend accepts integer
7. Rebuild frontend: `docker build --build-arg NEXT_PUBLIC_API_URL=... -t frontend:latest .`
8. Deploy: `kubectl rollout restart deployment/frontend`

## Quality Checklist
Before finalizing:
- [ ] All TypeScript interfaces match Pydantic schemas exactly
- [ ] Field names identical between backend and frontend
- [ ] Optional/nullable fields handled correctly (? and | null)
- [ ] Type conversion helpers created for complex mappings
- [ ] 422 validation errors parsed and displayed user-friendly
- [ ] API client methods use generic types for type safety
- [ ] Components use typed interfaces, not `any`
- [ ] Date/time fields use ISO 8601 strings (not Date objects)
- [ ] Array fields default to empty array, not undefined
- [ ] UUID fields treated as strings in TypeScript
- [ ] Integration tested end-to-end with real backend
- [ ] Frontend build passes without type errors
