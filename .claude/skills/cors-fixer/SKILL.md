---
name: "cors-fixer"
description: "Diagnoses and fixes CORS (Cross-Origin Resource Sharing) errors between frontend and backend. Handles credentials mode conflicts, wildcard origins, JWT authentication, and environment-specific CORS policies."
version: "1.0.0"
---

# CORS Fixer Skill

## When to Use
- User reports "blocked by CORS policy" error in browser console
- Error shows "Access-Control-Allow-Origin" header issues
- Frontend cannot connect to backend API
- Credentials mode conflicts with wildcard origin
- Preflight OPTIONS requests failing
- JWT authentication not working with CORS

## Context
This skill handles CORS issues following:
- **Backend**: FastAPI with CORSMiddleware
- **Frontend**: Next.js (browser-based fetch)
- **Authentication**: JWT in Authorization header (NOT cookies)
- **Environments**:
  - **Local**: Frontend (localhost:3000) → Backend (localhost:8000)
  - **Vercel**: Frontend (vercel.app) → Backend (vercel.app or DOKS)
  - **Production**: Frontend (vercel.app) → Backend (DOKS LoadBalancer)

## Workflow
1. **Identify Error**: Read browser console CORS error message
2. **Check Backend CORS Config**: Review FastAPI CORSMiddleware settings
3. **Check Frontend Request**: Look for credentials mode or headers
4. **Determine Environment**: Local, staging, or production
5. **Apply Fix**: Update CORS config or frontend request
6. **Rebuild & Deploy**: Rebuild frontend if needed
7. **Test**: Verify frontend can make API calls
8. **Verify Preflight**: Check OPTIONS requests work

## Common CORS Errors

### Error 1: Credentials Mode Conflict

**Browser Error**:
```
Access to fetch at 'http://174.138.120.69/api/login' from origin 'http://144.126.255.56' has been blocked by CORS policy: The value of the 'Access-Control-Allow-Origin' header in the response must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Root Cause**: Cannot use `credentials: "include"` with `Access-Control-Allow-Origin: *`

**Frontend Code (WRONG)**:
```typescript
// frontend/lib/api.ts ❌ WRONG
const response = await fetch(url, {
  credentials: "include",  // Conflicts with wildcard origin
  headers: { Authorization: `Bearer ${token}` }
});
```

**Backend Code**:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Wildcard origin
    allow_credentials=True,  # Conflicts with wildcard!
)
```

**Fix Option 1: Remove credentials mode (RECOMMENDED for JWT)**:
```typescript
// frontend/lib/api.ts ✅ CORRECT
const response = await fetch(url, {
  // No credentials: "include" - JWT in Authorization header is enough
  headers: { Authorization: `Bearer ${token}` }
});
```

**Fix Option 2: Specify exact origins**:
```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://frontend-vercel-url.vercel.app",
        "http://144.126.255.56"
    ],
    allow_credentials=True,
)
```

### Error 2: Missing Authorization Header

**Browser Error**:
```
Access to fetch at 'http://backend/api/tasks' from origin 'http://frontend' has been blocked by CORS policy: Request header field authorization is not allowed by Access-Control-Allow-Headers in preflight response.
```

**Root Cause**: Backend doesn't allow Authorization header in CORS config

**Backend Code (WRONG)**:
```python
# backend/app/main.py ❌ WRONG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],  # Missing "Authorization"!
)
```

**Fix**:
```python
# backend/app/main.py ✅ CORRECT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers (includes Authorization)
)
```

### Error 3: Preflight Request Failing

**Browser Error**:
```
Access to fetch at 'http://backend/api/tasks' from origin 'http://frontend' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

**Root Cause**: OPTIONS request (preflight) not handled correctly

**Backend Code (WRONG)**:
```python
# backend/app/main.py ❌ WRONG
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],  # Missing "OPTIONS"
)
```

**Fix**:
```python
# backend/app/main.py ✅ CORRECT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # Includes OPTIONS for preflight
    allow_headers=["*"],
)
```

### Error 4: Environment-Specific Origins

**Browser Error** (only in production):
```
Access to fetch at 'https://backend-prod.com/api/tasks' from origin 'https://frontend-prod.vercel.app' has been blocked by CORS policy: The 'Access-Control-Allow-Origin' header contains the invalid value 'http://localhost:3000'.
```

**Root Cause**: CORS config includes localhost origins in production

**Backend Code (WRONG)**:
```python
# backend/app/main.py ❌ WRONG - Hardcoded origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only works locally!
)
```

**Fix - Environment-Based Configuration**:
```python
# backend/app/config.py
import os

class Settings:
    # Environment-aware CORS origins
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS",
        "http://localhost:3000,https://*.vercel.app"
    ).split(",")
```

```python
# backend/app/main.py ✅ CORRECT
from app.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,  # Not needed with JWT in headers
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Complete CORS Configuration

### Backend (FastAPI)

**Recommended Configuration** (`backend/app/main.py`):
```python
"""
FastAPI application with CORS middleware.

CORS configured for:
- Local development (localhost:3000)
- Vercel deployments (*.vercel.app)
- Production DOKS (specific IP)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Todo App API")

# Environment-based CORS origins
cors_origins_str = os.environ.get("CORS_ORIGINS", "")
if cors_origins_str:
    # Production: explicit origins from env var
    CORS_ORIGINS = cors_origins_str.split(",")
else:
    # Development: permissive for testing
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,  # JWT in Authorization header, not cookies
    allow_methods=["*"],  # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],  # Content-Type, Authorization, etc.
    expose_headers=["*"],  # Allow frontend to read response headers
)


@app.get("/health")
async def health():
    """Health check endpoint (no CORS issues)."""
    return {"status": "healthy"}
```

**Kubernetes ConfigMap** (`infrastructure/kubernetes/backend-configmap.yaml`):
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  CORS_ORIGINS: "http://144.126.255.56,https://frontend-vercel.vercel.app"
```

**Deployment with ConfigMap**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: backend:latest
        env:
        - name: CORS_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: CORS_ORIGINS
```

### Frontend (Next.js)

**API Client WITHOUT Credentials** (`frontend/lib/api.ts`):
```typescript
import { getJWT, signOut } from "./auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL
  || (process.env.NODE_ENV === "production"
    ? "https://backend-production.com"
    : "http://localhost:8000");

/**
 * Generic request wrapper.
 *
 * IMPORTANT: No credentials mode - JWT in Authorization header only.
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
    // ✅ NO credentials: "include" - not needed with JWT in header
  };

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, config);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: any) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body?: any) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
```

**Login WITHOUT Credentials** (`frontend/lib/auth.ts`):
```typescript
export async function login(email: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
    // ✅ NO credentials: "include"
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }

  const data = await response.json();

  // Store JWT in localStorage (not cookies)
  localStorage.setItem("jwt_token", data.access_token);
  localStorage.setItem("user_id", data.user.id);

  return data;
}
```

## Testing CORS

### 1. Browser Console Test
```javascript
// Open browser console on frontend page
// Try API call manually

fetch("http://174.138.120.69/api/health", {
  method: "GET",
  headers: {
    "Content-Type": "application/json"
  }
})
  .then(res => res.json())
  .then(data => console.log("Success:", data))
  .catch(err => console.error("CORS Error:", err));
```

**Expected**: No CORS error, returns `{"status": "healthy"}`

### 2. Check Response Headers

**Backend Response Headers** (should include):
```
Access-Control-Allow-Origin: http://144.126.255.56
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

**Check in Browser DevTools**:
1. Open Network tab
2. Make API request
3. Click request
4. View Response Headers

### 3. Test Preflight Request

**Manual OPTIONS Request**:
```bash
curl -X OPTIONS "http://174.138.120.69/api/tasks" \
  -H "Origin: http://144.126.255.56" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -v
```

**Expected Response**:
```
< HTTP/1.1 200 OK
< Access-Control-Allow-Origin: http://144.126.255.56
< Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
< Access-Control-Allow-Headers: authorization,content-type
```

## Deployment Considerations

### Rebuilding Frontend After CORS Fix

If CORS config changed in backend:
```bash
# Backend changes take effect immediately (restart pod)
kubectl rollout restart deployment/backend
```

If frontend code changed (removed credentials mode):
```bash
# Rebuild Docker image
cd frontend
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://174.138.120.69 \
  -t registry.digitalocean.com/todo-chatbot-reg/frontend:latest \
  --no-cache .

# Push to registry
docker push registry.digitalocean.com/todo-chatbot-reg/frontend:latest

# Restart deployment
kubectl rollout restart deployment/frontend
```

### Environment Variables

**Backend** (Kubernetes Secret/ConfigMap):
```bash
kubectl create configmap backend-config \
  --from-literal=CORS_ORIGINS="http://144.126.255.56,https://frontend.vercel.app"
```

**Frontend** (Docker build arg):
```bash
docker build \
  --build-arg NEXT_PUBLIC_API_URL=http://174.138.120.69 \
  -t frontend:latest .
```

## Troubleshooting Checklist

When CORS errors occur:
- [ ] Check browser console for exact error message
- [ ] Verify backend CORS middleware is configured
- [ ] Confirm frontend not using `credentials: "include"`
- [ ] Check JWT token in Authorization header (not cookies)
- [ ] Verify CORS_ORIGINS includes frontend origin
- [ ] Test preflight OPTIONS request works
- [ ] Check response headers include Access-Control-Allow-*
- [ ] Verify environment variables loaded correctly
- [ ] Test with simple GET request first (no auth)
- [ ] Clear browser cache and hard reload (Ctrl+Shift+R)

## Example Fix Session

**User Report**: "Frontend can't connect to backend - CORS error"

**Step 1: Check Error**
```
Browser Console:
Access to fetch at 'http://174.138.120.69/api/login' from origin 'http://144.126.255.56' has been blocked by CORS policy: The value of the 'Access-Control-Allow-Origin' header must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Step 2: Find credentials mode**
```bash
# Search frontend code
grep -r "credentials:" frontend/
# Found: frontend/lib/api.ts:47 and frontend/lib/auth.ts:37
```

**Step 3: Remove credentials mode**
```typescript
// frontend/lib/api.ts (Line 44-48)
const config: RequestInit = {
  ...options,
  headers,
  // credentials: "include", // ✅ REMOVED
};
```

**Step 4: Rebuild frontend**
```bash
docker build --build-arg NEXT_PUBLIC_API_URL=http://174.138.120.69 \
  -t registry.digitalocean.com/todo-chatbot-reg/frontend:latest \
  --no-cache .
docker push registry.digitalocean.com/todo-chatbot-reg/frontend:latest
kubectl rollout restart deployment/frontend
```

**Step 5: Test**
```
Browser Console:
fetch("http://174.138.120.69/api/health")
  .then(r => r.json())
  .then(d => console.log(d))
// Output: {status: "healthy"} ✅ CORS RESOLVED
```

## Quality Checklist
Before closing CORS issue:
- [ ] No CORS errors in browser console
- [ ] Frontend can call all API endpoints (GET, POST, PUT, DELETE)
- [ ] JWT authentication working
- [ ] Preflight OPTIONS requests succeed
- [ ] Backend CORS middleware configured correctly
- [ ] Frontend removed credentials mode
- [ ] Environment-specific origins configured
- [ ] Response headers include Access-Control-Allow-*
- [ ] Tested in all environments (local, staging, production)
- [ ] Documentation updated with CORS config
