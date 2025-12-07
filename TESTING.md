# Testing Guide: TODO App

Complete guide for testing your full-stack TODO application locally and in production.

---

## 🚀 Quick Start: Test Locally (5 minutes)

Your backend is already running on **http://localhost:8000**

### Method 1: Swagger UI (Easiest) ⭐

1. **Open Interactive API Docs**:
   ```
   http://localhost:8000/docs
   ```

2. **Create a User**:
   - Click **POST /api/signup** → "Try it out"
   - Enter:
     ```json
     {
       "email": "test@example.com",
       "name": "Test User",
       "password": "TestPass123"
     }
     ```
   - Click **Execute**
   - Save the `id` from the response

3. **Login**:
   - Click **POST /api/login** → "Try it out"
   - Enter:
     ```json
     {
       "email": "test@example.com",
       "password": "TestPass123"
     }
     ```
   - Click **Execute**
   - Copy the `access_token`

4. **Authorize**:
   - Click the **Authorize** button (🔓 lock icon) at the top right
   - Paste: `Bearer YOUR_TOKEN_HERE`
   - Click **Authorize**

5. **Test Task Operations**:
   - All task endpoints now work!
   - Try creating, listing, updating tasks

---

## 📡 Method 2: Using Postman

### Import Collection

1. Download Postman: https://www.postman.com/downloads/
2. Import the file: `TODO-API.postman_collection.json`
3. Collection includes all endpoints with automatic token handling

### Test Flow

1. **Run "Signup"** → User ID saved automatically
2. **Run "Login"** → Token saved automatically
3. **Run "Create Task"** → Works with auto-attached token
4. **Run "List Tasks"** → See your tasks
5. All subsequent requests use the saved token!

---

## 💻 Method 3: Command Line (curl)

### Complete Test Script

```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Create user (save the ID from response)
curl -X POST "http://localhost:8000/api/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "TestPass123"
  }'

# 3. Login (copy access_token from response)
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Set variables for easier testing (replace with your values)
export TOKEN="your-access-token-here"
export USER_ID="your-user-id-here"

# 4. Create a task
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'

# 5. List all tasks
curl -X GET "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN"

# 6. Update task (replace {task_id} with actual ID)
curl -X PUT "http://localhost:8000/api/$USER_ID/tasks/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Buy groceries and supplies",
    "description": "Milk, eggs, bread, cleaning products"
  }'

# 7. Mark complete
curl -X PATCH "http://localhost:8000/api/$USER_ID/tasks/1/complete" \
  -H "Authorization: Bearer $TOKEN"

# 8. Delete task
curl -X DELETE "http://localhost:8000/api/$USER_ID/tasks/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 Test Scenarios

### User Authentication Tests

#### ✅ Test 1: Successful Signup
- **Action**: POST /api/signup with valid data
- **Expected**: 201 Created, user object returned (no password)
- **Verify**: User ID is a valid UUID

#### ✅ Test 2: Duplicate Email
- **Action**: POST /api/signup with existing email
- **Expected**: 400 Bad Request, "Email already registered"

#### ✅ Test 3: Weak Password
- **Action**: POST /api/signup with password "weak"
- **Expected**: 400 Bad Request, password requirements error

#### ✅ Test 4: Successful Login
- **Action**: POST /api/login with correct credentials
- **Expected**: 200 OK, JWT token + user object
- **Verify**: Token is a valid JWT string

#### ✅ Test 5: Invalid Login
- **Action**: POST /api/login with wrong password
- **Expected**: 401 Unauthorized, "Invalid email or password"

---

### Task Management Tests

#### ✅ Test 6: Create Task
- **Action**: POST /api/{user_id}/tasks with title + description
- **Expected**: 201 Created, task object with auto-generated ID
- **Verify**: `completed` defaults to `false`

#### ✅ Test 7: List Tasks (Empty)
- **Action**: GET /api/{user_id}/tasks for new user
- **Expected**: 200 OK, empty array `[]`

#### ✅ Test 8: List Tasks (With Data)
- **Action**: Create 3 tasks, then GET /api/{user_id}/tasks
- **Expected**: 200 OK, array with 3 tasks
- **Verify**: Tasks sorted by created_at (newest first)

#### ✅ Test 9: Update Task
- **Action**: PUT /api/{user_id}/tasks/{id} with new title
- **Expected**: 200 OK, updated task
- **Verify**: `updated_at` timestamp changed

#### ✅ Test 10: Toggle Complete
- **Action**: PATCH /api/{user_id}/tasks/{id}/complete
- **Expected**: 200 OK, task with `completed: true`
- **Action**: PATCH again
- **Expected**: Task with `completed: false` (toggled back)

#### ✅ Test 11: Delete Task
- **Action**: DELETE /api/{user_id}/tasks/{id}
- **Expected**: 204 No Content
- **Verify**: Subsequent GET returns 404

---

### Security Tests

#### ✅ Test 12: No Token
- **Action**: GET /api/{user_id}/tasks without Authorization header
- **Expected**: 401 Unauthorized

#### ✅ Test 13: Invalid Token
- **Action**: Request with `Authorization: Bearer invalid-token`
- **Expected**: 401 Unauthorized

#### ✅ Test 14: User ID Mismatch
- **Action**: User A tries to access User B's tasks
- **Expected**: 403 Forbidden
- **How**: Login as User A, use User B's ID in URL

#### ✅ Test 15: Cross-User Data Isolation
- **Action**: Create tasks as User A and User B separately
- **Expected**: User A sees only their tasks, User B sees only theirs
- **Verify**: No data leakage between users

---

## 📊 Database Verification

### Check SQLite Database

```bash
# Open database
sqlite3 backend/todo_app.db

# List all users
SELECT * FROM users;

# List all tasks
SELECT * FROM tasks;

# Count tasks per user
SELECT user_id, COUNT(*) FROM tasks GROUP BY user_id;

# Exit
.quit
```

---

## 🌐 Test Production Deployment

After deploying to Vercel + Railway:

### Update Base URL

Replace `http://localhost:8000` with your Railway backend URL:
```
https://your-app.railway.app
```

### Test Endpoints

1. **Health Check**:
   ```
   curl https://your-app.railway.app/health
   ```

2. **API Documentation**:
   ```
   https://your-app.railway.app/docs
   ```

3. **Run all test scenarios** using production URL

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized
**Cause**: Missing or invalid JWT token
**Fix**:
1. Login again to get fresh token
2. Verify token is in Authorization header
3. Check token hasn't expired (30-day expiration)

### Issue: 403 Forbidden
**Cause**: User ID mismatch (JWT user_id ≠ URL user_id)
**Fix**: Ensure you're using the correct user_id from your JWT

### Issue: 400 Bad Request
**Cause**: Validation error (empty title, invalid email, etc.)
**Fix**: Check error message for specific validation requirement

### Issue: 404 Not Found
**Cause**: Task doesn't exist or wrong ID
**Fix**: Verify task ID exists, check you own the task

### Issue: 500 Internal Server Error
**Cause**: Unexpected server error
**Fix**: Check backend logs for stack trace

---

## 📈 Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
# On Ubuntu: sudo apt-get install apache2-utils
# On Mac: brew install apr-util

# Test health endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/health

# Test authenticated endpoint (with token)
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/USER_ID/tasks
```

### Expected Performance
- Health check: <10ms per request
- Task list (100 tasks): <100ms per request
- Task creation: <50ms per request

---

## ✅ End-to-End Test Checklist

Complete flow from signup to task management:

- [ ] Open http://localhost:8000/docs
- [ ] Create new user via /api/signup
- [ ] Login via /api/login
- [ ] Copy and authorize with JWT token
- [ ] Create 5 different tasks
- [ ] List all tasks (should show 5)
- [ ] Update task #1
- [ ] Mark task #2 as complete
- [ ] Delete task #3
- [ ] List tasks again (should show 4)
- [ ] Filter completed tasks
- [ ] Logout (clear token)
- [ ] Verify 401 on next request

---

## 🔄 Automated Testing (Future)

For production, consider adding:

### Backend (Python)
```bash
pip install pytest pytest-asyncio httpx
pytest tests/
```

### Frontend (JavaScript)
```bash
npm install --save-dev jest @testing-library/react
npm test
```

### E2E (Playwright)
```bash
npm install --save-dev @playwright/test
npx playwright test
```

---

## 📝 Test Data

Use these sample datasets for testing:

### Sample Users
```json
[
  {"email": "alice@example.com", "name": "Alice", "password": "Alice123"},
  {"email": "bob@example.com", "name": "Bob", "password": "BobPass123"},
  {"email": "carol@example.com", "name": "Carol", "password": "Carol456"}
]
```

### Sample Tasks
```json
[
  {"title": "Buy groceries", "description": "Milk, eggs, bread"},
  {"title": "Finish homework", "description": "Math assignment due Friday"},
  {"title": "Call dentist", "description": "Schedule cleaning appointment"},
  {"title": "Pay bills", "description": "Electric, water, internet"},
  {"title": "Exercise", "description": "30 minutes cardio"}
]
```

---

## 📞 Support

If tests fail:
1. Check backend server is running: http://localhost:8000/health
2. Review backend logs for errors
3. Verify environment variables are set correctly
4. Check database file exists: `backend/todo_app.db`
5. Review DEPLOYMENT.md for deployment issues
