# Email Notifications - Implementation Plan

**Feature**: Email Notifications for Task Operations and Security Alerts
**Spec**: `specs/009-email-notifications/spec.md`
**Estimated Time**: 5-7 hours
**Priority**: Medium
**Status**: Ready for Implementation

---

## Implementation Strategy

### Approach: Synchronous Email Sending

**Rationale**:
- ✅ Simple to implement (no additional infrastructure)
- ✅ Works immediately in all phases
- ✅ Acceptable performance impact (+500ms per operation)
- ✅ Can be refactored to async in Phase V if needed

**Trade-offs**:
- ⚠️ API responses wait for email to send
- ⚠️ Limited scalability (500 emails/day with Gmail)
- ✅ Mitigated by: Error handling prevents failures, feature flag allows disable

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                       │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  Task/Auth Routers                                         │
│  ├─ Task Created → EmailService.send_task_created_email  │
│  ├─ Task Updated → EmailService.send_task_updated_email  │
│  ├─ Task Deleted → EmailService.send_task_deleted_email  │
│  └─ User Login   → EmailService.send_login_notification  │
│                                                            │
│  EmailService Module                                       │
│  ├─ SMTP Connection (Gmail)                               │
│  ├─ Template Rendering                                    │
│  ├─ Error Handling                                        │
│  └─ Logging                                               │
│                                                            │
│  Email Templates (HTML)                                    │
│  ├─ base.html                                             │
│  ├─ task_created.html                                     │
│  ├─ task_updated.html                                     │
│  ├─ task_deleted.html                                     │
│  └─ login_notification.html                               │
│                                                            │
└──────────────────────────────────────────────────────────┘
                         ▼
           ┌─────────────────────────┐
           │    Gmail SMTP Server    │
           │   smtp.gmail.com:587    │
           └─────────────────────────┘
                         ▼
           ┌─────────────────────────┐
           │      User's Inbox       │
           └─────────────────────────┘
```

---

## Phase Breakdown

### Phase 1: Backend Email Service (3-4 hours)

**Goal**: Create reusable email service module with templates

#### Tasks:
1. **Create email service module** (`backend/app/services/email.py`)
   - EmailService class with SMTP connection
   - send_email() method (low-level)
   - High-level notification methods
   - Error handling with try-except
   - Logging for monitoring

2. **Update configuration** (`backend/app/config.py`)
   - Add SMTP settings (server, port, credentials)
   - Add feature flag (EMAIL_NOTIFICATIONS_ENABLED)
   - Load from environment variables

3. **Create email templates**
   - `backend/app/templates/email/base.html` - Base template
   - `backend/app/templates/email/task_created.html`
   - `backend/app/templates/email/task_updated.html`
   - `backend/app/templates/email/task_deleted.html`
   - `backend/app/templates/email/login_notification.html`

4. **Update .env file**
   - Add SMTP credentials
   - Test with local Gmail account

**Deliverables**:
- ✅ EmailService class functional
- ✅ All email templates created
- ✅ Configuration updated
- ✅ Local testing successful

**Testing**:
```python
# Manual test in Python console
from app.services.email import EmailService
from app.models.user import User
from app.models.task import Task

email_service = EmailService()
user = User(email="test@example.com", name="Test User")
task = Task(title="Test Task", description="Test")

await email_service.send_task_created_email(user, task)
# Check inbox for email
```

---

### Phase 2: Task Endpoint Integration (1 hour)

**Goal**: Add email notifications to all task CRUD operations

#### Tasks:
1. **Modify create_task endpoint** (`backend/app/routers/tasks.py`)
   - Add email service import
   - Call send_task_created_email after commit
   - Wrap in try-except with logging

2. **Modify update_task endpoint**
   - Call send_task_updated_email after commit
   - Include change details if available

3. **Modify delete_task endpoint**
   - Capture task details before deletion
   - Call send_task_deleted_email after commit

4. **Modify toggle_task_completion endpoint**
   - Call send_task_updated_email after commit
   - Indicate completion status change

**Code Pattern** (all endpoints):
```python
from app.services.email import email_service

# ... endpoint logic ...
session.commit()
session.refresh(task)

# Send email notification
if settings.EMAIL_NOTIFICATIONS_ENABLED:
    try:
        await email_service.send_task_created_email(user, task)
    except Exception as e:
        logger.error(f"Failed to send task creation email: {e}")
        # Don't raise - continue execution

return task
```

**Deliverables**:
- ✅ All 4 task endpoints send emails
- ✅ Error handling prevents API failures
- ✅ Logging captures successes and failures

**Testing**:
```bash
# Via Swagger UI or curl
# 1. Create task → check email
# 2. Update task → check email
# 3. Delete task → check email
# 4. Toggle completion → check email
```

---

### Phase 3: Auth Endpoint Integration (30 minutes)

**Goal**: Add login security notifications

#### Tasks:
1. **Modify login endpoint** (`backend/app/routers/auth.py`)
   - Add Request parameter to get IP and user agent
   - Call send_login_notification_email after auth
   - Extract IP from request.client.host
   - Extract user agent from request.headers

**Code**:
```python
from fastapi import Request
from app.services.email import email_service

@router.post("/login")
async def login(
    credentials: UserLogin,
    request: Request,  # Add this
    session: Session = Depends(get_session)
):
    # ... existing auth logic ...

    # Send login notification
    if settings.EMAIL_NOTIFICATIONS_ENABLED:
        try:
            ip_address = request.client.host
            user_agent = request.headers.get("user-agent", "Unknown")
            await email_service.send_login_notification_email(
                user, ip_address, user_agent
            )
        except Exception as e:
            logger.error(f"Failed to send login notification: {e}")

    return {"access_token": token, "token_type": "bearer"}
```

**Deliverables**:
- ✅ Login endpoint sends security alert
- ✅ IP address and user agent captured
- ✅ Email includes login details

**Testing**:
```bash
# Login via Swagger UI or frontend
# Check email for security notification
# Verify IP and browser info is correct
```

---

### Phase 4: Kubernetes Configuration (1 hour)

**Goal**: Deploy email notifications to Kubernetes cluster

#### Tasks:
1. **Update Kubernetes secrets** (`k8s/secrets/app-secrets.yaml`)
   - Add smtp-server, smtp-port, smtp-username, smtp-password
   - Add smtp-from-email, smtp-from-name
   - Apply to cluster

2. **Update secrets template** (`k8s/secrets/app-secrets.yaml.template`)
   - Add SMTP secret placeholders
   - Update documentation

3. **Update Helm values** (`helm/todo-app/values.yaml`)
   - Add SMTP environment variables in backend.env
   - Inject from secrets using secretKeyRef
   - Add EMAIL_NOTIFICATIONS_ENABLED=true

4. **Update secrets README** (`k8s/secrets/README.md`)
   - Add SMTP setup instructions
   - Add troubleshooting for email issues

**Deliverables**:
- ✅ Secrets configured in Kubernetes
- ✅ Helm chart updated
- ✅ Backend pods have SMTP env vars
- ✅ Documentation updated

**Deployment Steps**:
```bash
# 1. Update secrets
kubectl apply -f k8s/secrets/app-secrets.yaml

# 2. Upgrade Helm release
helm upgrade todo-app ./helm/todo-app

# 3. Verify pods restarted
kubectl rollout status deployment/todo-app-backend

# 4. Check environment variables
kubectl exec <pod> -- printenv | grep SMTP

# 5. Test email sending
# Create task via frontend → check email
```

---

### Phase 5: Testing & Documentation (1-2 hours)

**Goal**: Comprehensive testing and documentation

#### Tasks:
1. **Write unit tests**
   - `backend/tests/test_email_service.py` - Email service tests
   - Test all email methods
   - Test SMTP error handling
   - Test feature flag disable

2. **Write integration tests**
   - `backend/tests/test_task_notifications.py` - End-to-end tests
   - Mock SMTP connection
   - Test all task endpoints send emails
   - Test login endpoint sends email

3. **Manual testing**
   - Test in local development environment
   - Test in Kubernetes (Minikube)
   - Test all notification types
   - Verify email content and formatting

4. **Update documentation**
   - Update `backend/CLAUDE.md` with email service
   - Update deployment guides
   - Add troubleshooting section

**Deliverables**:
- ✅ All tests passing
- ✅ Manual testing successful
- ✅ Documentation complete
- ✅ Ready for production

---

## Dependencies

### Python Packages
**Required** (built-in):
- `smtplib` - SMTP client
- `email.mime` - Email message construction

**Optional** (recommended):
- `Jinja2>=3.1.2` - Template rendering
  ```bash
  pip install jinja2
  # Add to requirements.txt
  ```

### External Services
- Gmail SMTP access
- Gmail app password: `pbeo fvxw rerz drsb`
- Email account: `mathnj120@gmail.com`

### Existing Components
- ✅ User model with email field
- ✅ Task model with all fields
- ✅ Task CRUD endpoints
- ✅ Authentication endpoints
- ✅ Kubernetes secrets infrastructure
- ✅ Helm chart structure

---

## Risk Mitigation

### Risk 1: Email Sending Blocks API Responses
**Mitigation**:
- Wrap email calls in try-except (never raise)
- Set short SMTP timeout (5 seconds)
- Log errors but continue execution
- Feature flag allows instant disable

### Risk 2: Gmail Rate Limits (500/day)
**Mitigation**:
- Monitor email send count
- Alert when approaching limit (450/day)
- Document upgrade path to SendGrid/Mailgun
- Phase V: Implement async sending with queue

### Risk 3: SMTP Connection Failures
**Mitigation**:
- Graceful error handling
- Comprehensive logging
- Health check endpoint for SMTP status
- Fallback to no emails (app still works)

### Risk 4: Email Marked as Spam
**Mitigation**:
- Use proper email headers
- Avoid spammy language
- Include unsubscribe link (future)
- Test with multiple email providers

### Risk 5: Secret Exposure
**Mitigation**:
- ✅ Already handled with .gitignore
- ✅ Template file approach
- ✅ Kubernetes secrets encryption
- Rotate app password if exposed

---

## Testing Strategy

### Unit Tests
```python
# backend/tests/test_email_service.py

def test_send_email_success(mock_smtp):
    """Test successful email sending"""
    result = await email_service.send_email(
        to="test@example.com",
        subject="Test",
        html_body="<p>Test</p>",
        text_body="Test"
    )
    assert result == True
    assert mock_smtp.sendmail.called

def test_send_email_smtp_error(mock_smtp):
    """Test SMTP error handling"""
    mock_smtp.sendmail.side_effect = smtplib.SMTPException("Error")
    result = await email_service.send_email(...)
    assert result == False
    # Should log error but not raise

def test_task_created_email_content():
    """Test task creation email has correct content"""
    user = User(email="test@example.com", name="Test User")
    task = Task(title="Test Task", description="Test Description")

    html, text = email_service._render_task_created_template(user, task)

    assert "Test Task" in html
    assert "Test Description" in html
    assert user.name in html
```

### Integration Tests
```python
# backend/tests/test_task_notifications.py

def test_create_task_sends_email(client, mock_smtp):
    """Test creating task triggers email"""
    response = client.post("/api/{user_id}/tasks", json={
        "title": "Test Task",
        "description": "Test"
    })

    assert response.status_code == 201
    assert mock_smtp.send_email.called

    call_args = mock_smtp.send_email.call_args
    assert "Task Created" in call_args[0][1]  # subject

def test_update_task_sends_email(client, mock_smtp):
    """Test updating task triggers email"""
    # Similar pattern

def test_email_disabled_no_send(client, mock_smtp, monkeypatch):
    """Test emails not sent when disabled"""
    monkeypatch.setenv("EMAIL_NOTIFICATIONS_ENABLED", "false")

    response = client.post("/api/{user_id}/tasks", json={"title": "Test"})

    assert response.status_code == 201
    assert not mock_smtp.send_email.called
```

### Manual Testing Checklist
- [ ] Local: Create task → email received
- [ ] Local: Update task → email received with changes
- [ ] Local: Delete task → email received with details
- [ ] Local: Toggle completion → email received
- [ ] Local: Login → security alert received
- [ ] Kubernetes: All above tests repeated
- [ ] Email content formatted correctly (HTML)
- [ ] Email links work correctly
- [ ] SMTP errors logged properly
- [ ] Feature flag disables emails

---

## Rollout Strategy

### Phase 1: Local Development
1. Implement and test locally
2. Verify all emails work
3. Commit code without secrets

### Phase 2: Kubernetes Testing
1. Apply secrets to Minikube
2. Deploy via Helm
3. Test all notification types
4. Monitor logs for errors

### Phase 3: Production Deployment
1. Update production secrets
2. Helm upgrade with zero downtime
3. Monitor email delivery
4. Watch for SMTP errors

### Rollback Plan
If issues occur:
1. **Instant**: Set `EMAIL_NOTIFICATIONS_ENABLED=false` in env
2. **Quick**: `helm rollback todo-app`
3. **Emergency**: Comment out email calls, redeploy

---

## Success Criteria

### Functionality
- ✅ All 5 email notification types working
- ✅ Emails sent for task create/update/delete/complete
- ✅ Login security alerts sent
- ✅ Email content accurate and formatted
- ✅ Links in emails work correctly

### Performance
- ✅ API response time increase <500ms (p95)
- ✅ Email send success rate >95%
- ✅ Zero API failures due to email errors

### Reliability
- ✅ SMTP errors logged properly
- ✅ Error handling prevents app failures
- ✅ Feature flag allows instant disable
- ✅ Graceful degradation if SMTP unavailable

### Deployment
- ✅ Kubernetes secrets configured
- ✅ Helm chart updated and tested
- ✅ Zero downtime deployment
- ✅ Easy rollback if needed

### Testing
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Manual testing successful
- ✅ Documentation complete

---

## Monitoring & Alerts

### Metrics to Track
```python
# Prometheus metrics (future)
email_sent_total{status="success"}
email_sent_total{status="failure"}
email_send_duration_seconds
smtp_connection_errors_total
```

### Logs to Monitor
```python
# Success
logger.info(f"Email sent to {user.email}: {subject}")

# Failure
logger.error(f"Failed to send email to {user.email}: {error}")

# Rate limit warning
logger.warning(f"Approaching Gmail rate limit: {count}/500")
```

### Alerts to Configure
- Alert if email success rate < 95% (1 hour window)
- Alert if SMTP connection fails 3+ times (15 minutes)
- Alert if daily email count > 450

---

## Post-Implementation

### Documentation Updates
- [x] Create `specs/009-email-notifications/spec.md`
- [x] Create `specs/009-email-notifications/plan.md`
- [ ] Update `backend/CLAUDE.md` with email service
- [ ] Update `k8s/secrets/README.md` with SMTP setup
- [ ] Add troubleshooting guide for email issues

### Future Enhancements (Phase V)
1. **Async Email Sending**
   - Use Dapr pub/sub for events
   - Separate email service microservice
   - Queue with retry logic

2. **Email Preferences**
   - User can toggle notifications on/off
   - UI in settings page
   - Per-notification-type preferences

3. **Rich Notifications**
   - Email analytics (open rates, clicks)
   - Digest emails (daily/weekly summary)
   - Custom templates per user

---

## Timeline

**Total Estimated Time**: 5-7 hours

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Email service module | 2 hours | None |
| 1 | Email templates | 1 hour | None |
| 1 | Configuration | 30 min | Email service |
| 2 | Task endpoints | 1 hour | Email service |
| 3 | Auth endpoint | 30 min | Email service |
| 4 | Kubernetes config | 1 hour | All code complete |
| 5 | Testing | 1-2 hours | All phases complete |
| 5 | Documentation | 30 min | All phases complete |

**Parallelization Opportunities**:
- Email service and templates can be developed in parallel
- Testing can start while Kubernetes config is in progress

---

## Next Steps

1. **Review this plan** - Confirm approach and timeline
2. **Start Phase 1** - Create email service module
3. **Iterative testing** - Test each phase before moving to next
4. **Deploy to K8s** - After all code is complete
5. **Monitor** - Track email delivery and errors

**Ready to start implementation? Let's begin with Phase 1: Email Service Module!** 🚀
