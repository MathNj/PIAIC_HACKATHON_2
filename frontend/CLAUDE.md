# Frontend Guidelines

## Stack
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/UI (accessible component library)
- Better Auth (authentication)
- @tanstack/react-query (data fetching)

## Patterns

### Component Structure
- Use **server components** by default (better performance)
- Use **client components** only when needed:
  - Interactive elements (onClick, onChange, etc.)
  - Browser APIs (localStorage, window, etc.)
  - React hooks (useState, useEffect, etc.)
- Mark client components with `"use client"` directive at the top

### File Organization
```
frontend/
├── app/                    # Pages and layouts (Next.js App Router)
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Landing/home page
│   ├── login/
│   │   └── page.tsx       # Login page
│   ├── signup/
│   │   └── page.tsx       # Signup page
│   └── dashboard/
│       ├── layout.tsx     # Dashboard layout with nav
│       └── page.tsx       # Task list page
├── components/
│   ├── ui/                # Shadcn/UI components (button, input, etc.)
│   ├── tasks/             # Task-specific components
│   │   ├── task-list.tsx
│   │   ├── task-item.tsx
│   │   ├── create-task-dialog.tsx
│   │   └── edit-task-dialog.tsx
│   └── providers/
│       ├── auth-provider.tsx
│       └── query-provider.tsx
└── lib/
    ├── api.ts             # API client (Axios)
    ├── auth.ts            # Better Auth configuration
    └── utils.ts           # Utility functions
```

## API Client

All backend calls should use the centralized API client:

```typescript
// lib/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor: Handle 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const api = {
  // Auth
  signup: (data) => apiClient.post('/api/signup', data),
  login: (data) => apiClient.post('/api/login', data),

  // Tasks
  getTasks: (userId) => apiClient.get(`/api/${userId}/tasks`),
  createTask: (userId, data) => apiClient.post(`/api/${userId}/tasks`, data),
  updateTask: (userId, taskId, data) => apiClient.put(`/api/${userId}/tasks/${taskId}`, data),
  toggleComplete: (userId, taskId) => apiClient.patch(`/api/${userId}/tasks/${taskId}/complete`),
  deleteTask: (userId, taskId) => apiClient.delete(`/api/${userId}/tasks/${taskId}`),
};
```

## Styling

### Tailwind CSS
- Use Tailwind utility classes for all styling
- No inline styles (`style={{...}}`)
- No custom CSS files unless absolutely necessary
- Follow existing component patterns

### Common Patterns
```typescript
// Buttons
<button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
  Click me
</button>

// Cards
<div className="bg-white rounded-lg shadow p-6">
  Content here
</div>

// Forms
<input
  className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
/>
```

## Authentication Flow

### Better Auth Integration

1. **Configuration** (`lib/auth.ts`):
```typescript
import { createAuthClient } from 'better-auth/client';

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

export async function login(email: string, password: string) {
  const response = await api.login({ email, password });
  localStorage.setItem('auth_token', response.data.access_token);
  localStorage.setItem('user', JSON.stringify(response.data.user));
  return response.data;
}

export async function logout() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}

export function getUser() {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
}
```

2. **Auth Provider** (`components/providers/auth-provider.tsx`):
```typescript
"use client"

import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
```

3. **Protected Routes**:
```typescript
// In page.tsx files that require auth
"use client"

import { useAuth } from '@/components/providers/auth-provider';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  if (!user) return null;

  return <div>Dashboard content...</div>;
}
```

## Data Fetching

### React Query Pattern

```typescript
"use client"

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export default function TaskList() {
  const { user } = useAuth();
  const queryClient = useQueryClient();

  // Fetch tasks
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', user?.id],
    queryFn: () => api.getTasks(user.id).then(res => res.data),
    enabled: !!user,
  });

  // Create task mutation
  const createMutation = useMutation({
    mutationFn: (taskData) => api.createTask(user.id, taskData),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', user?.id]);
    },
  });

  // Delete task mutation
  const deleteMutation = useMutation({
    mutationFn: (taskId) => api.deleteTask(user.id, taskId),
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks', user?.id]);
    },
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      {tasks?.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onDelete={() => deleteMutation.mutate(task.id)}
        />
      ))}
    </div>
  );
}
```

## Error Handling

### Display Errors
```typescript
import { toast } from 'sonner'; // or your toast library

try {
  await api.createTask(userId, taskData);
  toast.success('Task created successfully!');
} catch (error) {
  toast.error(error.response?.data?.message || 'Failed to create task');
}
```

## Form Validation

### Client-Side Validation
```typescript
const [errors, setErrors] = useState({});

function validateForm(data) {
  const newErrors = {};

  if (!data.title || data.title.trim().length === 0) {
    newErrors.title = 'Title is required';
  }

  if (data.title.length > 200) {
    newErrors.title = 'Title must be less than 200 characters';
  }

  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
}

// In component
<input
  className={errors.title ? 'border-red-500' : 'border-gray-300'}
/>
{errors.title && <p className="text-red-500 text-sm">{errors.title}</p>}
```

## Shadcn/UI Components

### Installation
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
```

### Usage
```typescript
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

<Button variant="primary" onClick={handleClick}>
  Save Task
</Button>

<Input
  type="text"
  placeholder="Task title"
  value={title}
  onChange={(e) => setTitle(e.target.value)}
/>
```

## Environment Variables

Create `.env.local` in frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-must-be-at-least-32-characters-long
```

**Important**: Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## Running the Frontend

```bash
# Development
cd frontend
npm run dev

# Build
npm run build

# Start production server
npm start

# Lint
npm run lint
```

## TypeScript Best Practices

- Define types for all API responses
- Use interfaces for component props
- Avoid `any` type
- Use type inference when possible

```typescript
// Define types
interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskItemProps {
  task: Task;
  onDelete: (id: number) => void;
  onToggle: (id: number) => void;
}

// Use in component
const TaskItem: React.FC<TaskItemProps> = ({ task, onDelete, onToggle }) => {
  // Component code
};
```

## Testing Checklist

Before committing frontend changes:
- [ ] All TypeScript errors resolved
- [ ] Components render without console errors
- [ ] Forms validate correctly
- [ ] API calls handle errors gracefully
- [ ] Loading states display properly
- [ ] Responsive design works on mobile
- [ ] Authentication flow works end-to-end

## References
- Spec: `@specs/features/task-crud.md`
- API: `@specs/api/rest-endpoints.md`
- Testing: `TESTING.md`
- Deployment: `DEPLOYMENT.md`
