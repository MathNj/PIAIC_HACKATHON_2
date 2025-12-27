"""
Test script for email service.

Tests:
1. SMTP connection to Gmail
2. Send test email
3. Template rendering
4. Error handling

Run: python test_email_service.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    os.system("chcp 65001 >nul")
    sys.stdout.reconfigure(encoding='utf-8')

# Add backend to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.email import email_service
from app.models.user import User
from app.models.task import Task
from datetime import datetime


async def test_smtp_connection():
    """Test SMTP connection to Gmail."""
    print("🔌 Testing SMTP connection...")

    try:
        smtp = email_service._get_smtp_connection()
        print("✅ SMTP connection successful!")
        print(f"   Server: {email_service.smtp_server}:{email_service.smtp_port}")
        print(f"   Username: {email_service.smtp_username}")
        smtp.quit()
        return True
    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False


async def test_send_simple_email():
    """Send a simple test email."""
    print("\n📧 Testing simple email send...")

    html_body = """
    <!DOCTYPE html>
    <html>
    <body>
        <h1>Test Email from TODO App</h1>
        <p>This is a test email to verify SMTP configuration.</p>
        <p>If you received this, email notifications are working! 🎉</p>
    </body>
    </html>
    """

    try:
        success = await email_service.send_email(
            to=email_service.smtp_username,  # Send to yourself
            subject="🧪 TODO App - Test Email",
            html_body=html_body,
            text_body="This is a test email from TODO App."
        )

        if success:
            print(f"✅ Test email sent successfully!")
            print(f"   To: {email_service.smtp_username}")
            print(f"   Check your inbox at {email_service.smtp_username}")
        else:
            print(f"❌ Email sending failed (email service disabled or error)")

        return success
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False


async def test_task_created_notification():
    """Test task created email template."""
    print("\n📋 Testing task created notification...")

    # Mock user and task
    mock_user = User(
        id="test-user-123",
        email=email_service.smtp_username,  # Send to yourself
        name="Test User",
        password_hash="not-used-in-test"
    )

    mock_task = Task(
        id=999,
        user_id="test-user-123",
        title="Test Task - Buy groceries",
        description="Get milk, eggs, and bread from the store",
        completed=False,
        priority="high",
        due_date=datetime(2025, 12, 31, 23, 59),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    try:
        await email_service.send_task_created_email(mock_user, mock_task)
        print(f"✅ Task created email sent!")
        print(f"   To: {mock_user.email}")
        print(f"   Task: {mock_task.title}")
        print(f"   Check your inbox for the formatted email")
        return True
    except Exception as e:
        print(f"❌ Task created email failed: {e}")
        return False


async def test_login_notification():
    """Test login notification email template."""
    print("\n🔐 Testing login notification...")

    # Mock user
    mock_user = User(
        id="test-user-123",
        email=email_service.smtp_username,  # Send to yourself
        name="Test User",
        password_hash="not-used-in-test"
    )

    try:
        await email_service.send_login_notification_email(
            user=mock_user,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        print(f"✅ Login notification sent!")
        print(f"   To: {mock_user.email}")
        print(f"   Check your inbox for the security alert")
        return True
    except Exception as e:
        print(f"❌ Login notification failed: {e}")
        return False


async def test_feature_flag():
    """Test EMAIL_NOTIFICATIONS_ENABLED feature flag."""
    print("\n🚩 Testing feature flag...")

    if email_service.enabled:
        print(f"✅ Email notifications ENABLED")
        print(f"   Feature flag: EMAIL_NOTIFICATIONS_ENABLED=true")
    else:
        print(f"⚠️ Email notifications DISABLED")
        print(f"   Feature flag: EMAIL_NOTIFICATIONS_ENABLED=false")
        print(f"   Emails will be skipped silently")

    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("📧 EMAIL SERVICE TEST SUITE")
    print("=" * 60)

    # Check configuration
    print(f"\n⚙️ Configuration:")
    print(f"   SMTP Server: {email_service.smtp_server}:{email_service.smtp_port}")
    print(f"   From: {email_service.from_name} <{email_service.from_email}>")
    print(f"   Enabled: {email_service.enabled}")

    # Run tests
    results = []

    results.append(await test_feature_flag())
    results.append(await test_smtp_connection())

    if email_service.enabled:
        results.append(await test_send_simple_email())
        results.append(await test_task_created_notification())
        results.append(await test_login_notification())
    else:
        print("\n⚠️ Skipping email tests (feature disabled)")

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"   Tests Passed: {passed}/{total}")

    if passed == total:
        print(f"   ✅ All tests passed!")
    else:
        print(f"   ❌ Some tests failed")

    print("\n💡 Next Steps:")
    print("   1. Check your inbox at", email_service.smtp_username)
    print("   2. Verify all test emails arrived")
    print("   3. Check email formatting and content")
    print("   4. If tests passed, proceed to T012 (integrate endpoints)")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
