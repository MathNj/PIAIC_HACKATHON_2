# CORS Configuration for JWT Authentication

## Current Configuration

**File**: `backend/app/main.py` (lines 63-72)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # Specific frontend origin
    allow_credentials=True,  # Enable credentials mode for JWT
    allow_methods=["*"],  # All HTTP methods
    allow_headers=["*"],  # All headers (including Authorization)
    expose_headers=["*"],  # Allow frontend to read response headers
)
```

## Why This Configuration?

### 1. Specific Origin Instead of Wildcard

**Before** (Insecure):
```python
allow_origins=["*"]  # Allow all origins
allow_credentials=False
```

**After** (Secure):
```python
allow_origins=[settings.FRONTEND_URL]  # Only allow known frontend
allow_credentials=True
```

**Benefits**:
- Prevents unauthorized domains from making API requests
- Required for credentials mode (cannot use `["*"]` with `credentials=True`)
- Better security for production deployments

### 2. Credentials Mode Enabled

**Purpose**: Allows the browser to send cookies and credentials with cross-origin requests.

**For JWT Authentication**:
- While JWT tokens are sent in `Authorization` header (not cookies)
- Enabling `allow_credentials=True` with specific origins is a security best practice
- Ensures proper CORS validation for authenticated requests

**Important**: The frontend does NOT use `credentials: "include"` in fetch requests because:
- JWT is sent in the `Authorization` header
- `credentials: "include"` is only needed for cookie-based auth
- Combining `credentials: "include"` with `allow_origins=["*"]` causes CORS errors

### 3. Environment-Based Configuration

**Local Development** (`.env`):
```env
FRONTEND_URL=http://localhost:3000
```

**Production** (Environment Variable):
```env
FRONTEND_URL=https://your-frontend.vercel.app
```

**Multiple Origins** (if needed):
You can extend the configuration to support multiple origins:

```python
# In config.py
FRONTEND_URLS = os.environ.get(
    "FRONTEND_URLS",
    "http://localhost:3000"
).split(",")

# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_URLS,  # List of allowed origins
    allow_credentials=True,
)
```

**Example** (multiple environments):
```env
FRONTEND_URLS=http://localhost:3000,https://staging.vercel.app,https://production.vercel.app
```

## Testing CORS Configuration

### 1. Verify Configuration
```bash
cd backend
python -c "
from app.main import app
for m in app.user_middleware:
    if hasattr(m, 'cls') and 'CORS' in m.cls.__name__:
        print('CORS:', m.kwargs)
"
```

**Expected Output**:
```python
{
    'allow_origins': ['http://localhost:3000'],
    'allow_credentials': True,
    'allow_methods': ['*'],
    'allow_headers': ['*'],
    'expose_headers': ['*']
}
```

### 2. Test from Frontend
Open browser console on `http://localhost:3000`:

```javascript
// Test health endpoint (no auth)
fetch("http://localhost:8000/health")
  .then(res => res.json())
  .then(data => console.log("Success:", data))
  .catch(err => console.error("CORS Error:", err));

// Test with JWT (after login)
fetch("http://localhost:8000/api/user123/tasks", {
  headers: {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
  }
})
  .then(res => res.json())
  .then(data => console.log("Tasks:", data))
  .catch(err => console.error("Error:", err));
```

**Expected**: No CORS errors in console

### 3. Check Response Headers
In browser DevTools:
1. Network tab
2. Make API request
3. View Response Headers

**Expected Headers**:
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### 4. Test Preflight Request
```bash
curl -X OPTIONS "http://localhost:8000/api/user123/tasks" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -v
```

**Expected**: 200 OK with CORS headers

## Common CORS Errors (Fixed)

### Error 1: Wildcard + Credentials Conflict
**Browser Error**:
```
The value of the 'Access-Control-Allow-Origin' header must not be the wildcard '*'
when the request's credentials mode is 'include'.
```

**Fix**: Use specific origin instead of wildcard ✅ DONE

### Error 2: Origin Not Allowed
**Browser Error**:
```
Access to fetch at 'http://backend' from origin 'http://frontend' has been blocked by CORS policy
```

**Fix**: Add frontend URL to `allow_origins` ✅ DONE

### Error 3: Missing Authorization Header
**Browser Error**:
```
Request header field authorization is not allowed by Access-Control-Allow-Headers
```

**Fix**: Use `allow_headers=["*"]` ✅ DONE

## Production Deployment

### Vercel (Frontend)
Set environment variable:
```bash
vercel env add FRONTEND_URL
# Value: https://your-app.vercel.app
```

### Railway/Render (Backend)
Set environment variable:
```bash
FRONTEND_URL=https://your-frontend.vercel.app
```

### Kubernetes
ConfigMap:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
data:
  FRONTEND_URL: "https://frontend-production.vercel.app"
```

Deployment:
```yaml
containers:
- name: backend
  env:
  - name: FRONTEND_URL
    valueFrom:
      configMapKeyRef:
        name: backend-config
        key: FRONTEND_URL
```

## Security Considerations

✅ **Specific origin** - Only known frontend can access API
✅ **Credentials enabled** - Proper CORS validation for authenticated requests
✅ **Environment-based** - Different origins for dev/staging/production
✅ **No wildcard in production** - Prevents unauthorized access
✅ **Authorization header allowed** - JWT tokens can be sent

## Troubleshooting

If CORS errors occur:

1. **Check environment variable**:
   ```bash
   echo $FRONTEND_URL  # Should match frontend domain
   ```

2. **Verify backend config**:
   ```bash
   python -c "from app.config import settings; print(settings.FRONTEND_URL)"
   ```

3. **Check browser console** for exact error message

4. **Verify response headers** in Network tab

5. **Clear browser cache** and hard reload (Ctrl+Shift+R)

6. **Restart backend** after changing `.env`:
   ```bash
   uvicorn app.main:app --reload
   ```

## References

- FastAPI CORS Middleware: https://fastapi.tiangolo.com/tutorial/cors/
- MDN CORS Guide: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- JWT Best Practices: https://datatracker.ietf.org/doc/html/rfc8725
