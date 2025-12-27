# Email Notifications Feature Specification

**Feature ID**: 009
**Feature Name**: Email Notifications for Task Operations and Security Alerts
**Status**: Planned
**Phase**: Phase II (Backend Implementation)
**Priority**: Medium
**Estimated Effort**: 5-7 hours

---

## Overview

Implement email notifications to keep users informed of task operations and account security events. Users will receive automatic email notifications when tasks are created, updated, deleted, or completed, as well as security alerts when they log in to their account.

### Goals
- ✅ Notify users of all task CRUD operations
- ✅ Send security alerts for login events
- ✅ Provide clear, actionable email content
- ✅ Ensure reliable delivery with error handling
- ✅ Maintain fast API response times

### Non-Goals
- ❌ Email preferences/opt-out UI (deferred to future phase)
- ❌ Async email sending via Dapr (deferred to Phase V)
- ❌ Email analytics/tracking
- ❌ HTML email customization by users
- ❌ Digest emails (batched notifications)

---

## User Stories

### US-009-001: Task Creation Notification
**As a** user
**I want to** receive an email when I create a task
**So that** I have a record of my task and can access it from my email

**Acceptance Criteria**:
- [ ] Email sent immediately after task creation
- [ ] Email contains task title, description, due date, and priority
- [ ] Email includes link to view task in the app
- [ ] Email fails gracefully without blocking API response
- [ ] Email uses branded HTML template

### US-009-002: Task Update Notification
**As a** user
**I want to** receive an email when I update a task
**So that** I can track what changed and have an audit trail

**Acceptance Criteria**:
- [ ] Email sent immediately after task update
- [ ] Email shows what fields changed (before/after)
- [ ] Email includes link to view updated task
- [ ] Email sent for both manual updates and AI-generated updates

### US-009-003: Task Deletion Notification
**As a** user
**I want to** receive an email when I delete a task
**So that** I have confirmation and can recover details if needed

**Acceptance Criteria**:
- [ ] Email sent immediately after task deletion
- [ ] Email contains deleted task details for record-keeping
- [ ] Email includes timestamp of deletion
- [ ] Email confirms deletion was intentional

### US-009-004: Task Completion Notification
**As a** user
**I want to** receive an email when I complete or reopen a task
**So that** I can celebrate completion or track status changes

**Acceptance Criteria**:
- [ ] Email sent when task marked as complete
- [ ] Email sent when completed task is reopened
- [ ] Email clearly indicates completion status
- [ ] Email includes task details and completion time

### US-009-005: Login Security Alert
**As a** user
**I want to** receive an email when someone logs into my account
**So that** I can detect unauthorized access

**Acceptance Criteria**:
- [ ] Email sent immediately after successful login
- [ ] Email includes login timestamp (UTC)
- [ ] Email includes IP address of login
- [ ] Email includes browser/device information
- [ ] Email includes "Not you? Secure your account" link

---

## Technical Design

### Architecture

```
┌─────────────────┐
│   Task API      │
│   Endpoint      │
└────────┬────────┘
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌─────────────────┐           ┌─────────────────┐
│  Save to DB     │           │  Email Service  │
└─────────────────┘           └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │   Gmail SMTP    │
                              └─────────────────┘
```

### Email Service Module

**Location**: `backend/app/services/email.py`

**Class**: `EmailService`

**Methods**:
```python
class EmailService:
    def __init__(self):
        """Initialize SMTP connection settings from config"""

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        """Send email via SMTP (low-level method)"""

    async def send_task_created_email(
        self,
        user: User,
        task: Task
    ) -> None:
        """Send notification for task creation"""

    async def send_task_updated_email(
        self,
        user: User,
        task: Task,
        changes: Optional[dict] = None
    ) -> None:
        """Send notification for task update"""

    async def send_task_deleted_email(
        self,
        user: User,
        task_title: str,
        task_details: dict
    ) -> None:
        """Send notification for task deletion"""

    async def send_login_notification_email(
        self,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> None:
        """Send security alert for login event"""
```

### Email Templates

**Location**: `backend/app/templates/email/`

**Templates**:
1. `base.html` - Base template with header/footer
2. `task_created.html` - Task creation notification
3. `task_updated.html` - Task update notification
4. `task_deleted.html` - Task deletion notification
5. `login_notification.html` - Login security alert

**Template Engine**: Plain Python string formatting (simple) or Jinja2 (recommended)

**Example Template Structure**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Responsive email styles */
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 TODO App</h1>
        </div>
        <div class="content">
            {{ content }}
        </div>
        <div class="footer">
            <p>Sent from TODO App | <a href="#">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>
```

### Configuration

**SMTP Settings** (in `backend/app/config.py`):
```python
# Email configuration
SMTP_SERVER: str = "smtp.gmail.com"
SMTP_PORT: int = 587
SMTP_USERNAME: str  # From environment variable
SMTP_PASSWORD: str  # From environment variable (app password)
SMTP_FROM_EMAIL: str  # From environment variable
SMTP_FROM_NAME: str = "TODO App Notifications"
EMAIL_NOTIFICATIONS_ENABLED: bool = True
```

**Environment Variables** (`.env`):
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=mathnj120@gmail.com
SMTP_PASSWORD=pbeo fvxw rerz drsb
SMTP_FROM_EMAIL=mathnj120@gmail.com
SMTP_FROM_NAME=TODO App Notifications
EMAIL_NOTIFICATIONS_ENABLED=true
```

### Integration Points

#### Task CRUD Endpoints

**File**: `backend/app/routers/tasks.py`

**Endpoints to Modify**:

1. **Create Task** (`POST /api/{user_id}/tasks`):
```python
@router.post("/{user_id}/tasks", response_model=TaskRead)
async def create_task(...):
    # ... existing logic ...
    session.commit()
    session.refresh(new_task)

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            await send_task_created_email(user, new_task)
        except Exception as e:
            logger.error(f"Failed to send task creation email: {e}")

    return new_task
```

2. **Update Task** (`PUT /api/{user_id}/tasks/{task_id}`):
```python
@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(...):
    # ... existing logic ...
    session.commit()
    session.refresh(task)

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            await send_task_updated_email(user, task)
        except Exception as e:
            logger.error(f"Failed to send task update email: {e}")

    return task
```

3. **Delete Task** (`DELETE /api/{user_id}/tasks/{task_id}`):
```python
@router.delete("/{user_id}/tasks/{task_id}")
async def delete_task(...):
    task_details = {
        "title": task.title,
        "description": task.description,
        "deleted_at": datetime.utcnow().isoformat()
    }

    session.delete(task)
    session.commit()

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            await send_task_deleted_email(user, task.title, task_details)
        except Exception as e:
            logger.error(f"Failed to send task deletion email: {e}")

    return {"message": "Task deleted"}
```

4. **Toggle Completion** (`PATCH /api/{user_id}/tasks/{task_id}/complete`):
```python
@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(...):
    # ... existing logic ...
    session.commit()
    session.refresh(task)

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            await send_task_updated_email(user, task)
        except Exception as e:
            logger.error(f"Failed to send task completion email: {e}")

    return task
```

#### Authentication Endpoint

**File**: `backend/app/routers/auth.py`

**Endpoint to Modify**:

**Login** (`POST /api/login`):
```python
@router.post("/login")
async def login(
    credentials: UserLogin,
    request: Request,  # Add to get IP and user agent
    session: Session = Depends(get_session)
):
    # ... existing auth logic ...

    # Send login notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent", "Unknown")
            await send_login_notification_email(user, ip_address, user_agent)
        except Exception as e:
            logger.error(f"Failed to send login notification: {e}")

    return {"access_token": token, "token_type": "bearer"}
```

---

## Email Content Specifications

### 1. Task Created Email

**Subject**: `Task Created: {task.title}`

**Content**:
```
Hi {user.name},

You've created a new task:

📋 {task.title}

Details:
- Description: {task.description or 'No description'}
- Due Date: {task.due_date or 'No due date'}
- Priority: {task.priority}
- Created: {task.created_at}

[View Task in App] (button/link)

---
TODO App Notifications
```

### 2. Task Updated Email

**Subject**: `Task Updated: {task.title}`

**Content**:
```
Hi {user.name},

Your task has been updated:

📋 {task.title}

What changed:
- Title: {old_title} → {new_title}
- Description: {old_description} → {new_description}
- Due Date: {old_due_date} → {new_due_date}
- Priority: {old_priority} → {new_priority}

Updated: {task.updated_at}

[View Task in App] (button/link)

---
TODO App Notifications
```

### 3. Task Deleted Email

**Subject**: `Task Deleted: {task.title}`

**Content**:
```
Hi {user.name},

The following task was deleted:

📋 {task.title}

Details (for your records):
- Description: {task.description}
- Due Date: {task.due_date}
- Priority: {task.priority}
- Deleted: {deleted_at}

This action cannot be undone.

---
TODO App Notifications
```

### 4. Task Completed Email

**Subject**: `Task Completed: {task.title}` or `Task Reopened: {task.title}`

**Content (Completed)**:
```
Hi {user.name},

Congratulations! You've completed a task:

✅ {task.title}

Completed: {task.updated_at}

[View Completed Tasks] (button/link)

---
TODO App Notifications
```

**Content (Reopened)**:
```
Hi {user.name},

A task has been reopened:

🔄 {task.title}

Reopened: {task.updated_at}

[View Task in App] (button/link)

---
TODO App Notifications
```

### 5. Login Notification Email

**Subject**: `New Login to Your TODO Account`

**Content**:
```
Hi {user.name},

We detected a new login to your TODO account:

🔐 Login Details:
- Time: {login_time}
- IP Address: {ip_address}
- Device/Browser: {user_agent}
- Location: {location (optional)}

If this was you, no action is needed.

If you don't recognize this activity:
[Secure Your Account] (button/link to change password)

---
TODO App Security Team
```

---

## Error Handling

### SMTP Connection Failures

```python
try:
    await send_email(...)
except smtplib.SMTPException as e:
    logger.error(f"SMTP error: {e}")
    # Don't raise - fail silently
    # Email failure should not block API response
except Exception as e:
    logger.error(f"Unexpected email error: {e}")
    # Log and continue
```

### Rate Limiting

Gmail limits: 500 emails/day

**Strategy**:
- Log email send count
- Warn if approaching limit (450/day)
- Consider alternative provider if exceeded

### Email Delivery Failures

**Not Delivered**:
- Log failure for monitoring
- Don't retry immediately (avoid spam)
- Consider queue for retry (Phase V)

**Bounced Emails**:
- Log invalid email addresses
- Don't send future emails to bounced addresses

---

## Security Considerations

### 1. Email Content
- ✅ No sensitive data (passwords, API keys)
- ✅ Task details only (user-owned data)
- ✅ All content escaped/sanitized
- ⚠️ Consider encrypting sensitive task descriptions (future)

### 2. SMTP Credentials
- ✅ Stored in environment variables
- ✅ Stored in Kubernetes secrets (encrypted)
- ✅ Not committed to git
- ✅ Rotated periodically (every 90 days)

### 3. Spam Prevention
- ✅ Rate limiting (Gmail: 500/day)
- ✅ Feature flag to disable if abused
- ✅ Proper email headers (SPF, DKIM)
- ✅ Unsubscribe link (optional, future)

### 4. Email Injection
- ✅ No user input in email headers
- ✅ All content parameterized
- ✅ Using secure SMTP library

---

## Performance

### Email Send Latency
- **SMTP Connection**: ~200-500ms
- **Email Send**: ~100-300ms
- **Total**: ~300-800ms per email

### Impact on API Response Time
- Task creation: +500ms (acceptable)
- Task update: +500ms (acceptable)
- Login: +500ms (acceptable)

### Optimization (Phase V)
- Move to async/background processing
- Use Dapr pub/sub for event-driven emails
- Separate email service microservice

---

## Testing

### Unit Tests

**File**: `backend/tests/test_email_service.py`

```python
def test_send_task_created_email():
    """Test task creation email content and delivery"""

def test_send_task_updated_email():
    """Test task update email content and delivery"""

def test_send_task_deleted_email():
    """Test task deletion email content and delivery"""

def test_send_login_notification_email():
    """Test login notification email content"""

def test_smtp_failure_handling():
    """Test graceful handling of SMTP errors"""

def test_email_disabled():
    """Test that emails are not sent when disabled"""
```

### Integration Tests

**File**: `backend/tests/test_task_notifications.py`

```python
def test_create_task_sends_email(mock_smtp):
    """Test that creating a task sends email"""
    response = client.post("/api/{user_id}/tasks", json=task_data)
    assert response.status_code == 201
    assert mock_smtp.send_email.called

def test_update_task_sends_email(mock_smtp):
    """Test that updating a task sends email"""

def test_delete_task_sends_email(mock_smtp):
    """Test that deleting a task sends email"""

def test_login_sends_email(mock_smtp):
    """Test that login sends security notification"""
```

### Manual Testing

1. **Local Development**:
   ```bash
   # Set up .env with Gmail credentials
   # Create/update/delete tasks via Swagger UI
   # Check Gmail inbox for notifications
   ```

2. **Kubernetes**:
   ```bash
   # Deploy with SMTP secrets
   # Test all notification types
   # Verify emails from cluster
   ```

---

## Monitoring

### Metrics
- `email_sent_total` - Counter of emails sent
- `email_failed_total` - Counter of email failures
- `email_send_duration_seconds` - Histogram of send latency

### Logging
```python
logger.info(f"Email sent to {user.email}: {subject}")
logger.error(f"Failed to send email to {user.email}: {error}")
```

### Alerts
- Alert if email success rate < 95%
- Alert if SMTP connection fails repeatedly
- Alert if approaching daily limit (450/500)

---

## Deployment

### Phase II: Local Development

**Environment Variables** (`.env`):
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=mathnj120@gmail.com
SMTP_PASSWORD=pbeo fvxw rerz drsb
SMTP_FROM_EMAIL=mathnj120@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=true
```

**Start Backend**:
```bash
cd backend
uvicorn app.main:app --reload
```

### Phase IV: Kubernetes

**Update Secrets**:
```bash
kubectl apply -f k8s/secrets/app-secrets.yaml
```

**Upgrade Helm Release**:
```bash
helm upgrade todo-app ./helm/todo-app
```

**Verify**:
```bash
kubectl exec <pod> -- printenv | grep SMTP
```

---

## Rollback Plan

### Option 1: Disable Feature Flag
```python
# In config.py or via env var
EMAIL_NOTIFICATIONS_ENABLED = False
```

### Option 2: Helm Rollback
```bash
helm rollback todo-app
```

### Option 3: Comment Out Code
```python
# Comment out email calls in endpoints
# if settings.EMAIL_NOTIFICATIONS_ENABLED:
#     await send_task_created_email(...)
```

---

## Future Enhancements (Phase V+)

### Email Preferences
- User can toggle notifications on/off
- User can choose which notifications to receive
- UI in settings page

### Async Email Sending
- Use Dapr pub/sub for event-driven emails
- Separate email service microservice
- Better scalability and reliability

### Email Analytics
- Track open rates
- Track click rates
- User engagement metrics

### Digest Emails
- Daily/weekly summary of tasks
- Upcoming due dates reminder
- Completed tasks summary

### Rich Notifications
- Inline images
- Custom branding
- User-configurable templates

---

## Acceptance Criteria

- [ ] Email service module implemented with error handling
- [ ] HTML email templates created and tested
- [ ] Task creation sends email with correct content
- [ ] Task update sends email with change details
- [ ] Task deletion sends email with confirmation
- [ ] Task completion sends email with status
- [ ] Login sends security alert with IP and browser
- [ ] SMTP errors logged but don't block API responses
- [ ] Feature flag allows disabling notifications
- [ ] Kubernetes secrets configured for SMTP
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Manual testing successful in local and Kubernetes
- [ ] Documentation updated
- [ ] Deployed to production successfully

---

## Dependencies

**Backend**:
- Python standard library: `smtplib`, `email.mime`
- Optional: `Jinja2>=3.1.2` (for template rendering)

**Infrastructure**:
- Gmail SMTP access
- Gmail app password configured
- Kubernetes secrets support

**Existing Components**:
- User model with email field ✅
- Task CRUD endpoints ✅
- Authentication endpoints ✅
- Kubernetes secrets infrastructure ✅

---

## Success Metrics

- Email delivery success rate: >95%
- Email send latency: <500ms (p95)
- Zero API failures due to email errors
- User satisfaction with notifications (future survey)
- Gmail rate limit not exceeded (<450 emails/day)

---

## References

- [Gmail SMTP Documentation](https://support.google.com/mail/answer/7126229)
- [Python smtplib Documentation](https://docs.python.org/3/library/smtplib.html)
- [Email Security Best Practices](https://www.cloudflare.com/learning/email-security/what-is-email-security/)
- Impact Analysis: `docs/EMAIL_NOTIFICATIONS_IMPACT_ANALYSIS.md`
