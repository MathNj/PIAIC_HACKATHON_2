# Email Notifications - Implementation Tasks

**Feature**: Email Notifications
**Spec**: `specs/009-email-notifications/spec.md`
**Plan**: `specs/009-email-notifications/plan.md`
**Status**: Ready for Implementation

---

## Task Summary

| ID | Task | Estimated Time | Status |
|----|------|----------------|--------|
| T001 | Create email service module structure | 30 min | ⏸️ Pending |
| T002 | Implement SMTP connection | 30 min | ⏸️ Pending |
| T003 | Implement send_email method | 30 min | ⏸️ Pending |
| T004 | Create base email template | 30 min | ⏸️ Pending |
| T005 | Create task_created template | 20 min | ⏸️ Pending |
| T006 | Create task_updated template | 20 min | ⏸️ Pending |
| T007 | Create task_deleted template | 20 min | ⏸️ Pending |
| T008 | Create login_notification template | 20 min | ⏸️ Pending |
| T009 | Update config.py with SMTP settings | 15 min | ⏸️ Pending |
| T010 | Update .env with SMTP credentials | 10 min | ⏸️ Pending |
| T011 | Test email service locally | 20 min | ⏸️ Pending |
| T012 | Integrate create_task endpoint | 10 min | ⏸️ Pending |
| T013 | Integrate update_task endpoint | 10 min | ⏸️ Pending |
| T014 | Integrate delete_task endpoint | 10 min | ⏸️ Pending |
| T015 | Integrate toggle_completion endpoint | 10 min | ⏸️ Pending |
| T016 | Integrate login endpoint | 15 min | ⏸️ Pending |
| T017 | Update Kubernetes secrets | 15 min | ⏸️ Pending |
| T018 | Update secrets template | 10 min | ⏸️ Pending |
| T019 | Update Helm values.yaml | 20 min | ⏸️ Pending |
| T020 | Update secrets README | 15 min | ⏸️ Pending |
| T021 | Deploy to Kubernetes | 20 min | ⏸️ Pending |
| T022 | Write email service unit tests | 30 min | ⏸️ Pending |
| T023 | Write integration tests | 30 min | ⏸️ Pending |
| T024 | Manual testing | 30 min | ⏸️ Pending |
| T025 | Update backend documentation | 15 min | ⏸️ Pending |

**Total Estimated Time**: 6 hours 30 minutes

---

## Detailed Task Breakdown

### Phase 1: Backend Email Service

---

#### T001: Create Email Service Module Structure

**File**: `backend/app/services/email.py` (NEW)

**Objective**: Create the foundational EmailService class

**Implementation**:
```python
"""
Email notification service for task operations and security alerts.

Uses Gmail SMTP to send HTML emails for:
- Task creation, update, deletion, completion
- Login security notifications
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from pathlib import Path

from app.config import settings
from app.models.user import User
from app.models.task import Task

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications via SMTP."""

    def __init__(self):
        """Initialize SMTP connection settings from configuration."""
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.enabled = settings.EMAIL_NOTIFICATIONS_ENABLED

        # Template directory
        self.template_dir = Path(__file__).parent.parent / "templates" / "email"

    # Methods to be implemented in subsequent tasks
```

**Test Criteria**:
- [ ] File created at correct location
- [ ] Class imports successfully
- [ ] Configuration loaded from settings
- [ ] No syntax errors

**Dependencies**: None

**Estimated Time**: 30 minutes

---

#### T002: Implement SMTP Connection

**File**: `backend/app/services/email.py`

**Objective**: Add method to establish SMTP connection

**Implementation**:
```python
def _get_smtp_connection(self) -> smtplib.SMTP:
    """
    Establish SMTP connection to Gmail.

    Returns:
        smtplib.SMTP: Connected SMTP client

    Raises:
        smtplib.SMTPException: If connection fails
    """
    try:
        logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")

        # Create SMTP connection
        smtp = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)

        # Start TLS encryption
        smtp.starttls()

        # Login
        smtp.login(self.smtp_username, self.smtp_password)

        logger.info("SMTP connection established successfully")
        return smtp

    except smtplib.SMTPException as e:
        logger.error(f"SMTP connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to SMTP: {e}")
        raise
```

**Test Criteria**:
- [ ] Connection establishes successfully
- [ ] TLS encryption enabled
- [ ] Authentication successful
- [ ] Errors logged properly
- [ ] Connection can be closed

**Dependencies**: T001

**Estimated Time**: 30 minutes

---

#### T003: Implement send_email Method

**File**: `backend/app/services/email.py`

**Objective**: Create low-level email sending method

**Implementation**:
```python
async def send_email(
    self,
    to: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """
    Send email via SMTP.

    Args:
        to: Recipient email address
        subject: Email subject line
        html_body: HTML email body
        text_body: Plain text fallback (optional)

    Returns:
        bool: True if sent successfully, False otherwise
    """
    if not self.enabled:
        logger.info("Email notifications disabled, skipping send")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{self.from_name} <{self.from_email}>"
        message["To"] = to
        message["Subject"] = subject

        # Attach text version
        if text_body:
            part1 = MIMEText(text_body, "plain")
            message.attach(part1)

        # Attach HTML version
        part2 = MIMEText(html_body, "html")
        message.attach(part2)

        # Send email
        with self._get_smtp_connection() as smtp:
            smtp.sendmail(self.from_email, to, message.as_string())

        logger.info(f"Email sent successfully to {to}: {subject}")
        return True

    except smtplib.SMTPException as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to}: {e}")
        return False
```

**Test Criteria**:
- [ ] Email sent successfully
- [ ] HTML and text versions attached
- [ ] Headers set correctly
- [ ] SMTP errors handled gracefully
- [ ] Returns False on failure (doesn't raise)
- [ ] Logging includes success and failure

**Dependencies**: T002

**Estimated Time**: 30 minutes

---

#### T004: Create Base Email Template

**File**: `backend/app/templates/email/base.html` (NEW)

**Objective**: Create reusable base HTML template

**Implementation**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #4F46E5;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #4F46E5;
            font-size: 24px;
            margin: 0;
        }
        .header .emoji {
            font-size: 32px;
            margin-right: 10px;
        }
        .content {
            margin-bottom: 30px;
        }
        .content h2 {
            color: #1f2937;
            font-size: 20px;
            margin-bottom: 15px;
        }
        .content p {
            margin: 10px 0;
            color: #4b5563;
        }
        .task-details {
            background-color: #f9fafb;
            border-left: 4px solid #4F46E5;
            padding: 15px;
            margin: 20px 0;
        }
        .task-details p {
            margin: 8px 0;
        }
        .task-details strong {
            color: #1f2937;
        }
        .button {
            display: inline-block;
            padding: 12px 24px;
            background-color: #4F46E5;
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            text-align: center;
            margin: 20px 0;
        }
        .button:hover {
            background-color: #4338CA;
        }
        .footer {
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            margin-top: 30px;
            color: #6b7280;
            font-size: 14px;
        }
        .footer a {
            color: #4F46E5;
            text-decoration: none;
        }
        .security-badge {
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="emoji">📋</span>TODO App</h1>
        </div>

        <div class="content">
            {{ content }}
        </div>

        <div class="footer">
            <p>Sent from TODO App</p>
            <p><a href="#">Manage Email Preferences</a></p>
        </div>
    </div>
</body>
</html>
```

**Test Criteria**:
- [ ] Template renders correctly
- [ ] Responsive design works
- [ ] Colors and fonts appropriate
- [ ] Placeholder {{ content }} works

**Dependencies**: None

**Estimated Time**: 30 minutes

---

#### T005: Create Task Created Template

**File**: `backend/app/templates/email/task_created.html` (NEW)

**Objective**: Template for task creation notifications

**Implementation**:
```html
<h2>Task Created</h2>
<p>Hi {{ user_name }},</p>
<p>You've successfully created a new task:</p>

<div class="task-details">
    <p><strong>📋 Title:</strong> {{ task_title }}</p>
    {% if task_description %}
    <p><strong>📝 Description:</strong> {{ task_description }}</p>
    {% endif %}
    {% if task_due_date %}
    <p><strong>📅 Due Date:</strong> {{ task_due_date }}</p>
    {% endif %}
    <p><strong>⭐ Priority:</strong> {{ task_priority }}</p>
    <p><strong>🕐 Created:</strong> {{ task_created_at }}</p>
</div>

<a href="{{ app_url }}/tasks/{{ task_id }}" class="button">View Task in App</a>

<p>Stay organized and productive!</p>
```

**Template Variables**:
- `user_name`: User's display name
- `task_title`: Task title
- `task_description`: Task description (optional)
- `task_due_date`: Due date (optional)
- `task_priority`: Priority level
- `task_created_at`: Creation timestamp
- `task_id`: Task ID for link
- `app_url`: Frontend URL

**Test Criteria**:
- [ ] All variables render correctly
- [ ] Optional fields handled properly
- [ ] Link works correctly
- [ ] Formatting is clean

**Dependencies**: T004

**Estimated Time**: 20 minutes

---

#### T006: Create Task Updated Template

**File**: `backend/app/templates/email/task_updated.html` (NEW)

**Objective**: Template for task update notifications

**Implementation**:
```html
<h2>Task Updated</h2>
<p>Hi {{ user_name }},</p>
<p>Your task has been updated:</p>

<div class="task-details">
    <p><strong>📋 Task:</strong> {{ task_title }}</p>

    {% if changes %}
    <p><strong>What changed:</strong></p>
    <ul>
        {% for field, change in changes.items() %}
        <li><strong>{{ field }}:</strong> {{ change.old }} → {{ change.new }}</li>
        {% endfor %}
    </ul>
    {% else %}
    <p>Task details have been modified.</p>
    {% endif %}

    <p><strong>🕐 Updated:</strong> {{ task_updated_at }}</p>
</div>

<a href="{{ app_url }}/tasks/{{ task_id }}" class="button">View Updated Task</a>
```

**Test Criteria**:
- [ ] Shows what changed (if available)
- [ ] Handles no-changes case
- [ ] Formatting clear and readable

**Dependencies**: T004

**Estimated Time**: 20 minutes

---

#### T007: Create Task Deleted Template

**File**: `backend/app/templates/email/task_deleted.html` (NEW)

**Objective**: Template for task deletion notifications

**Implementation**:
```html
<h2>Task Deleted</h2>
<p>Hi {{ user_name }},</p>
<p>The following task has been deleted from your TODO list:</p>

<div class="task-details">
    <p><strong>📋 Title:</strong> {{ task_title }}</p>
    {% if task_description %}
    <p><strong>📝 Description:</strong> {{ task_description }}</p>
    {% endif %}
    {% if task_due_date %}
    <p><strong>📅 Due Date:</strong> {{ task_due_date }}</p>
    {% endif %}
    <p><strong>⭐ Priority:</strong> {{ task_priority }}</p>
    <p><strong>🗑️ Deleted:</strong> {{ deleted_at }}</p>
</div>

<p><em>This action cannot be undone. These details are for your records.</em></p>
```

**Test Criteria**:
- [ ] Shows deleted task details
- [ ] Timestamp accurate
- [ ] Confirmation message clear

**Dependencies**: T004

**Estimated Time**: 20 minutes

---

#### T008: Create Login Notification Template

**File**: `backend/app/templates/email/login_notification.html` (NEW)

**Objective**: Template for login security alerts

**Implementation**:
```html
<h2>New Login Detected</h2>
<p>Hi {{ user_name }},</p>
<p>We detected a new login to your TODO account:</p>

<div class="security-badge">
    <p><strong>🔐 Login Details:</strong></p>
    <p><strong>Time:</strong> {{ login_time }}</p>
    <p><strong>IP Address:</strong> {{ ip_address }}</p>
    <p><strong>Device/Browser:</strong> {{ user_agent }}</p>
</div>

<p>If this was you, no action is needed.</p>

<p><strong>If you don't recognize this activity:</strong></p>
<p>Your account may be compromised. Please secure it immediately.</p>

<a href="{{ app_url }}/settings/security" class="button">Secure Your Account</a>

<p style="color: #6b7280; font-size: 14px; margin-top: 20px;">
    <em>This is an automated security notification. We send these alerts to help protect your account.</em>
</p>
```

**Test Criteria**:
- [ ] Security message clear
- [ ] Login details accurate
- [ ] Action button prominent

**Dependencies**: T004

**Estimated Time**: 20 minutes

---

#### T009: Update config.py with SMTP Settings

**File**: `backend/app/config.py`

**Objective**: Add SMTP configuration to settings

**Implementation**:
```python
class Settings:
    def __init__(self):
        # ... existing settings ...

        # SMTP Configuration (Email Notifications)
        self.SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
        self.SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "")
        self.SMTP_FROM_NAME = os.environ.get("SMTP_FROM_NAME", "TODO App Notifications")
        self.EMAIL_NOTIFICATIONS_ENABLED = os.environ.get(
            "EMAIL_NOTIFICATIONS_ENABLED", "true"
        ).lower() in ("true", "1", "yes")

# Update validate_settings to check SMTP config
def validate_settings() -> None:
    """Validate that all critical settings are present and valid."""
    # ... existing validations ...

    # SMTP validation (only if notifications enabled)
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        if not settings.SMTP_USERNAME:
            logger.warning("SMTP_USERNAME not set - email notifications will fail")
        if not settings.SMTP_PASSWORD:
            logger.warning("SMTP_PASSWORD not set - email notifications will fail")
        if not settings.SMTP_FROM_EMAIL:
            logger.warning("SMTP_FROM_EMAIL not set - email notifications will fail")

        print(f"  - Email Notifications: {'ENABLED' if settings.EMAIL_NOTIFICATIONS_ENABLED else 'DISABLED'}")
        if settings.EMAIL_NOTIFICATIONS_ENABLED:
            print(f"  - SMTP Server: {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
            print(f"  - SMTP From: {settings.SMTP_FROM_EMAIL}")
```

**Test Criteria**:
- [ ] All SMTP settings loaded from environment
- [ ] Defaults set appropriately
- [ ] Validation checks SMTP config
- [ ] Startup logs show email status

**Dependencies**: None

**Estimated Time**: 15 minutes

---

#### T010: Update .env with SMTP Credentials

**File**: `backend/.env`

**Objective**: Add SMTP credentials to local environment

**Implementation**:
```env
# ... existing settings ...

# SMTP Configuration (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=mathnj120@gmail.com
SMTP_PASSWORD=pbeo fvxw rerz drsb
SMTP_FROM_EMAIL=mathnj120@gmail.com
SMTP_FROM_NAME=TODO App Notifications
EMAIL_NOTIFICATIONS_ENABLED=true
```

**Test Criteria**:
- [ ] Settings loaded on backend startup
- [ ] No syntax errors
- [ ] Credentials valid

**Dependencies**: T009

**Estimated Time**: 10 minutes

---

#### T011: Test Email Service Locally

**Objective**: Verify email service works in local development

**Test Steps**:
1. Start backend: `uvicorn app.main:app --reload`
2. Open Python console
3. Test email sending:

```python
from app.services.email import EmailService
from app.models.user import User
from app.models.task import Task
from datetime import datetime

email_service = EmailService()

# Create test user
user = User(
    email="your-test-email@example.com",
    name="Test User"
)

# Create test task
task = Task(
    id=1,
    title="Test Task",
    description="This is a test task",
    priority="high",
    created_at=datetime.utcnow()
)

# Send test email
await email_service.send_task_created_email(user, task)
```

4. Check inbox for email
5. Verify email content and formatting

**Test Criteria**:
- [ ] Email received in inbox
- [ ] HTML formatting correct
- [ ] All variables populated
- [ ] Links work (if applicable)
- [ ] No SMTP errors

**Dependencies**: T001-T010

**Estimated Time**: 20 minutes

---

### Phase 2: Task Endpoint Integration

---

#### T012: Integrate create_task Endpoint

**File**: `backend/app/routers/tasks.py`

**Objective**: Add email notification to task creation

**Implementation**:
```python
# Add import at top
from app.services.email import EmailService

# Initialize email service
email_service = EmailService()

# In create_task endpoint (after session.commit()):
@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(...):
    # ... existing logic ...
    session.commit()
    session.refresh(new_task)

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            # Get user for email
            user_statement = select(User).where(User.id == current_user)
            user = session.exec(user_statement).first()

            if user:
                await email_service.send_task_created_email(user, new_task)
            else:
                logger.warning(f"User {current_user} not found for email notification")

        except Exception as e:
            logger.error(f"Failed to send task creation email: {e}")
            # Don't raise - continue execution

    return new_task
```

**Test Criteria**:
- [ ] Email sent on task creation
- [ ] API response time acceptable (<1s)
- [ ] SMTP errors don't break endpoint
- [ ] Logging shows success/failure

**Dependencies**: T001-T011

**Estimated Time**: 10 minutes

---

#### T013: Integrate update_task Endpoint

**File**: `backend/app/routers/tasks.py`

**Objective**: Add email notification to task updates

**Implementation**:
```python
# In update_task endpoint (after session.commit()):
@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
async def update_task(...):
    # ... existing logic ...
    session.commit()
    session.refresh(task)

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            user_statement = select(User).where(User.id == current_user)
            user = session.exec(user_statement).first()

            if user:
                await email_service.send_task_updated_email(user, task)

        except Exception as e:
            logger.error(f"Failed to send task update email: {e}")

    return task
```

**Test Criteria**:
- [ ] Email sent on task update
- [ ] Shows what changed
- [ ] Errors handled gracefully

**Dependencies**: T001-T011

**Estimated Time**: 10 minutes

---

#### T014: Integrate delete_task Endpoint

**File**: `backend/app/routers/tasks.py`

**Objective**: Add email notification to task deletion

**Implementation**:
```python
# In delete_task endpoint (before session.delete()):
@router.delete("/{user_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(...):
    # ... existing logic ...

    # Capture task details before deletion
    task_details = {
        "title": task.title,
        "description": task.description,
        "due_date": str(task.due_date) if task.due_date else None,
        "priority": task.priority,
        "deleted_at": datetime.utcnow().isoformat()
    }

    # Delete task
    session.delete(task)
    session.commit()

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            user_statement = select(User).where(User.id == current_user)
            user = session.exec(user_statement).first()

            if user:
                await email_service.send_task_deleted_email(
                    user,
                    task_details["title"],
                    task_details
                )

        except Exception as e:
            logger.error(f"Failed to send task deletion email: {e}")

    return {"message": "Task deleted successfully"}
```

**Test Criteria**:
- [ ] Email sent on task deletion
- [ ] Task details captured before deletion
- [ ] Deletion still works if email fails

**Dependencies**: T001-T011

**Estimated Time**: 10 minutes

---

#### T015: Integrate toggle_completion Endpoint

**File**: `backend/app/routers/tasks.py`

**Objective**: Add email notification to completion toggle

**Implementation**:
```python
# In toggle_task_completion endpoint (after session.commit()):
@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
async def toggle_task_completion(...):
    # ... existing logic ...
    session.commit()
    session.refresh(task)

    # Send email notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            user_statement = select(User).where(User.id == current_user)
            user = session.exec(user_statement).first()

            if user:
                # Send as task update email (or create separate template)
                await email_service.send_task_updated_email(user, task)

        except Exception as e:
            logger.error(f"Failed to send task completion email: {e}")

    return task
```

**Test Criteria**:
- [ ] Email sent on completion toggle
- [ ] Shows completion status change
- [ ] Works for both complete and uncomplete

**Dependencies**: T001-T011

**Estimated Time**: 10 minutes

---

#### T016: Integrate login Endpoint

**File**: `backend/app/routers/auth.py`

**Objective**: Add login security notification

**Implementation**:
```python
# Add imports at top
from fastapi import Request
from app.services.email import EmailService

# Initialize email service
email_service = EmailService()

# Modify login endpoint signature:
@router.post("/login")
async def login(
    credentials: UserLogin,
    request: Request,  # Add this to get IP and user agent
    session: Session = Depends(get_session)
):
    # ... existing auth logic ...

    # Send login notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent", "Unknown")

            await email_service.send_login_notification_email(
                user,
                ip_address,
                user_agent
            )

        except Exception as e:
            logger.error(f"Failed to send login notification email: {e}")

    return {"access_token": access_token, "token_type": "bearer"}
```

**Test Criteria**:
- [ ] Email sent on login
- [ ] IP address captured correctly
- [ ] User agent captured correctly
- [ ] Login still works if email fails

**Dependencies**: T001-T011

**Estimated Time**: 15 minutes

---

### Phase 3: Kubernetes Configuration

---

#### T017: Update Kubernetes Secrets

**File**: `k8s/secrets/app-secrets.yaml`

**Objective**: Add SMTP credentials to Kubernetes secrets

**Implementation**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  # ... existing secrets ...

  # SMTP Configuration (Gmail)
  smtp-server: "smtp.gmail.com"
  smtp-port: "587"
  smtp-username: "mathnj120@gmail.com"
  smtp-password: "pbeo fvxw rerz drsb"
  smtp-from-email: "mathnj120@gmail.com"
  smtp-from-name: "TODO App Notifications"
```

**Apply**:
```bash
kubectl apply -f k8s/secrets/app-secrets.yaml
```

**Test Criteria**:
- [ ] Secret created/updated successfully
- [ ] All keys present
- [ ] Values base64 encoded (if using data:)

**Dependencies**: None

**Estimated Time**: 15 minutes

---

#### T018: Update Secrets Template

**File**: `k8s/secrets/app-secrets.yaml.template`

**Objective**: Add SMTP placeholders to template

**Implementation**:
```yaml
  # ... existing secrets ...

  # SMTP Configuration (Gmail)
  smtp-server: "smtp.gmail.com"
  smtp-port: "587"
  smtp-username: "your-gmail-address@gmail.com"
  smtp-password: "your-gmail-app-password"
  smtp-from-email: "your-gmail-address@gmail.com"
  smtp-from-name: "TODO App Notifications"
```

**Test Criteria**:
- [ ] Template shows correct structure
- [ ] Placeholders clear
- [ ] Instructions in README updated

**Dependencies**: None

**Estimated Time**: 10 minutes

---

#### T019: Update Helm values.yaml

**File**: `helm/todo-app/values.yaml`

**Objective**: Add SMTP environment variables to backend pods

**Implementation**:
```yaml
backend:
  env:
    # ... existing env vars ...

    # SMTP Configuration
    - name: SMTP_SERVER
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: smtp-server
    - name: SMTP_PORT
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: smtp-port
    - name: SMTP_USERNAME
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: smtp-username
    - name: SMTP_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: smtp-password
    - name: SMTP_FROM_EMAIL
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: smtp-from-email
    - name: SMTP_FROM_NAME
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: smtp-from-name
    - name: EMAIL_NOTIFICATIONS_ENABLED
      value: "true"
```

**Test Criteria**:
- [ ] All environment variables defined
- [ ] References correct secret keys
- [ ] Helm lint passes

**Dependencies**: T017, T018

**Estimated Time**: 20 minutes

---

#### T020: Update Secrets README

**File**: `k8s/secrets/README.md`

**Objective**: Document SMTP setup and troubleshooting

**Add Section**:
```markdown
### SMTP Configuration (Email Notifications)

**Required for**: Email notifications on task CRUD and login

**Setup**:
1. Get Gmail app password from https://myaccount.google.com/apppasswords
2. Add to `app-secrets.yaml`:
   ```yaml
   smtp-username: "your-email@gmail.com"
   smtp-password: "your-16-char-app-password"
   ```
3. Apply: `kubectl apply -f app-secrets.yaml`
4. Verify: `kubectl exec <pod> -- printenv | grep SMTP`

**Troubleshooting**:
- "SMTP Authentication Failed": Check app password is correct
- "Connection Refused": Check firewall allows port 587
- "Emails not sending": Check EMAIL_NOTIFICATIONS_ENABLED=true
```

**Test Criteria**:
- [ ] Documentation clear and complete
- [ ] Setup steps accurate
- [ ] Troubleshooting helpful

**Dependencies**: T017-T019

**Estimated Time**: 15 minutes

---

#### T021: Deploy to Kubernetes

**Objective**: Deploy email notifications to cluster

**Steps**:
```bash
# 1. Apply updated secrets
kubectl apply -f k8s/secrets/app-secrets.yaml

# 2. Verify secrets
kubectl get secret app-secrets
kubectl describe secret app-secrets

# 3. Upgrade Helm release
helm upgrade todo-app ./helm/todo-app

# 4. Wait for rollout
kubectl rollout status deployment/todo-app-backend

# 5. Verify environment variables
POD=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -- printenv | grep SMTP

# 6. Check logs
kubectl logs -l app=todo-backend --tail=50

# 7. Test email sending
# Create a task via frontend/API and check email
```

**Test Criteria**:
- [ ] Pods restarted successfully
- [ ] Environment variables injected
- [ ] No errors in logs
- [ ] Email sent on task creation
- [ ] All notification types working

**Dependencies**: T001-T020

**Estimated Time**: 20 minutes

---

### Phase 4: Testing & Documentation

---

#### T022: Write Email Service Unit Tests

**File**: `backend/tests/test_email_service.py` (NEW)

**Objective**: Test email service in isolation

**Implementation**:
```python
import pytest
from unittest.mock import Mock, patch
from app.services.email import EmailService
from app.models.user import User
from app.models.task import Task

@pytest.fixture
def email_service():
    return EmailService()

@pytest.fixture
def mock_user():
    return User(email="test@example.com", name="Test User")

@pytest.fixture
def mock_task():
    return Task(
        id=1,
        title="Test Task",
        description="Test Description",
        priority="high"
    )

def test_send_email_success(email_service, mock_smtp):
    """Test successful email sending"""
    result = await email_service.send_email(
        to="test@example.com",
        subject="Test",
        html_body="<p>Test</p>",
        text_body="Test"
    )
    assert result == True
    assert mock_smtp.sendmail.called

def test_send_email_smtp_error(email_service, mock_smtp):
    """Test SMTP error handling"""
    mock_smtp.sendmail.side_effect = smtplib.SMTPException("Error")
    result = await email_service.send_email(...)
    assert result == False

def test_send_email_disabled(email_service, monkeypatch):
    """Test emails not sent when disabled"""
    monkeypatch.setenv("EMAIL_NOTIFICATIONS_ENABLED", "false")
    result = await email_service.send_email(...)
    assert result == False

def test_task_created_email(email_service, mock_user, mock_task):
    """Test task creation email content"""
    # Test implementation
    pass
```

**Test Criteria**:
- [ ] All tests passing
- [ ] Code coverage >80%
- [ ] Edge cases covered

**Dependencies**: T001-T016

**Estimated Time**: 30 minutes

---

#### T023: Write Integration Tests

**File**: `backend/tests/test_task_notifications.py` (NEW)

**Objective**: Test end-to-end email sending

**Implementation**:
```python
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_create_task_sends_email(client: TestClient, auth_headers, mock_smtp):
    """Test creating task triggers email"""
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task"},
        headers=auth_headers
    )

    assert response.status_code == 201
    assert mock_smtp.send_email.called

def test_update_task_sends_email(client, auth_headers, mock_smtp):
    """Test updating task triggers email"""
    # Test implementation
    pass

def test_login_sends_email(client, mock_smtp):
    """Test login sends security notification"""
    # Test implementation
    pass
```

**Test Criteria**:
- [ ] All integration tests passing
- [ ] Mocking SMTP correctly
- [ ] API responses unaffected by email

**Dependencies**: T001-T021

**Estimated Time**: 30 minutes

---

#### T024: Manual Testing

**Objective**: Comprehensive manual testing

**Test Checklist**:
- [ ] **Local Development**
  - [ ] Create task → email received
  - [ ] Update task → email received with changes
  - [ ] Delete task → email received with details
  - [ ] Toggle completion → email received
  - [ ] Login → security alert received
  - [ ] Email HTML formatting correct
  - [ ] All links work

- [ ] **Kubernetes (Minikube)**
  - [ ] Deploy to cluster successfully
  - [ ] All notification types work
  - [ ] Check logs for errors
  - [ ] Verify email delivery
  - [ ] Test with multiple users

- [ ] **Error Scenarios**
  - [ ] SMTP disabled → no emails sent
  - [ ] Invalid SMTP credentials → logged, API works
  - [ ] Network error → logged, API works
  - [ ] Feature flag off → no emails sent

**Test Criteria**:
- [ ] All scenarios tested
- [ ] Issues documented
- [ ] Performance acceptable

**Dependencies**: T001-T023

**Estimated Time**: 30 minutes

---

#### T025: Update Backend Documentation

**File**: `backend/CLAUDE.md`

**Objective**: Document email service in backend guide

**Add Section**:
```markdown
## Email Notifications

### Email Service

**Location**: `backend/app/services/email.py`

**Purpose**: Send email notifications for task operations and security alerts

**Usage**:
\`\`\`python
from app.services.email import EmailService

email_service = EmailService()

# In task endpoint:
await email_service.send_task_created_email(user, task)
\`\`\`

**Configuration** (`.env`):
\`\`\`env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
EMAIL_NOTIFICATIONS_ENABLED=true
\`\`\`

**Error Handling**:
- All email sending wrapped in try-except
- Failures logged but don't break API responses
- Feature flag allows instant disable
```

**Test Criteria**:
- [ ] Documentation accurate
- [ ] Examples work
- [ ] Clear and helpful

**Dependencies**: T001-T024

**Estimated Time**: 15 minutes

---

## Summary

**Total Tasks**: 25
**Estimated Total Time**: 6.5 hours

**Completion Checklist**:
- [ ] All 25 tasks completed
- [ ] Email service functional
- [ ] All templates created
- [ ] All endpoints integrated
- [ ] Kubernetes configured
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Deployed and verified

**Success Criteria**:
- ✅ Email sent for all 5 notification types
- ✅ API performance acceptable (<500ms overhead)
- ✅ Error handling prevents failures
- ✅ Tests passing (unit + integration)
- ✅ Deployed to Kubernetes successfully
- ✅ Documentation complete

---

**Ready to start implementation!** 🚀
