"""
Email notification service for task operations and security alerts.

Uses Gmail SMTP to send HTML emails for:
- Task creation, update, deletion, completion
- Login security notifications

This module provides a centralized EmailService class that handles all email
sending operations with proper error handling and logging.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
import logging
from pathlib import Path
from datetime import datetime

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

        logger.info(f"EmailService initialized (enabled={self.enabled})")

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

            # Create SMTP connection with timeout
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)

            # Start TLS encryption
            smtp.starttls()

            # Login with credentials
            smtp.login(self.smtp_username, self.smtp_password)

            logger.info("SMTP connection established successfully")
            return smtp

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to SMTP: {e}")
            raise

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

            # Attach text version (if provided)
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

    def _render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render email template with variables.

        Args:
            template_name: Name of template file (without .html)
            variables: Dictionary of template variables

        Returns:
            str: Rendered HTML content
        """
        template_path = self.template_dir / f"{template_name}.html"

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Simple variable replacement (can be enhanced with Jinja2)
            for key, value in variables.items():
                placeholder = f"{{{{ {key} }}}}"
                # Handle None values
                if value is None:
                    value = ""
                template_content = template_content.replace(placeholder, str(value))

            return template_content

        except FileNotFoundError:
            logger.error(f"Template not found: {template_path}")
            raise
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            raise

    async def send_task_created_email(self, user: User, task: Task) -> None:
        """
        Send notification for task creation.

        Args:
            user: User who created the task
            task: Created task object
        """
        try:
            # Prepare template variables
            variables = {
                "user_name": user.name,
                "task_title": task.title,
                "task_description": task.description or "No description",
                "task_due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else "No due date",
                "task_priority": task.priority.upper() if task.priority else "NORMAL",
                "task_created_at": task.created_at.strftime("%Y-%m-%d %H:%M UTC"),
                "task_id": str(task.id),
                "app_url": settings.FRONTEND_URL
            }

            # Render template
            html_body = self._render_template("task_created", variables)

            # Send email
            subject = f"Task Created: {task.title}"
            await self.send_email(
                to=user.email,
                subject=subject,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Failed to send task creation email: {e}")
            # Don't raise - email failures should not break the app

    async def send_task_updated_email(
        self,
        user: User,
        task: Task,
        changes: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Send notification for task update.

        Args:
            user: User who updated the task
            task: Updated task object
            changes: Optional dictionary of changes (before/after)
        """
        try:
            # Prepare template variables
            variables = {
                "user_name": user.name,
                "task_title": task.title,
                "task_updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M UTC") if task.updated_at else datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                "task_id": str(task.id),
                "app_url": settings.FRONTEND_URL,
                "changes_html": self._format_changes(changes) if changes else "Task details have been modified."
            }

            # Render template
            html_body = self._render_template("task_updated", variables)

            # Send email
            subject = f"Task Updated: {task.title}"
            await self.send_email(
                to=user.email,
                subject=subject,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Failed to send task update email: {e}")

    async def send_task_deleted_email(
        self,
        user: User,
        task_title: str,
        task_details: Dict[str, Any]
    ) -> None:
        """
        Send notification for task deletion.

        Args:
            user: User who deleted the task
            task_title: Title of deleted task
            task_details: Dictionary with task details for records
        """
        try:
            # Prepare template variables
            variables = {
                "user_name": user.name,
                "task_title": task_title,
                "task_description": task_details.get("description") or "No description",
                "task_due_date": task_details.get("due_date") or "No due date",
                "task_priority": task_details.get("priority", "normal").upper(),
                "deleted_at": task_details.get("deleted_at", datetime.utcnow().isoformat())
            }

            # Render template
            html_body = self._render_template("task_deleted", variables)

            # Send email
            subject = f"Task Deleted: {task_title}"
            await self.send_email(
                to=user.email,
                subject=subject,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Failed to send task deletion email: {e}")

    async def send_login_notification_email(
        self,
        user: User,
        ip_address: str,
        user_agent: str
    ) -> None:
        """
        Send security alert for login event.

        Args:
            user: User who logged in
            ip_address: IP address of login
            user_agent: Browser/device user agent string
        """
        try:
            # Prepare template variables
            variables = {
                "user_name": user.name,
                "login_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "app_url": settings.FRONTEND_URL
            }

            # Render template
            html_body = self._render_template("login_notification", variables)

            # Send email
            subject = "New Login to Your TODO Account"
            await self.send_email(
                to=user.email,
                subject=subject,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Failed to send login notification email: {e}")

    def _format_changes(self, changes: Dict[str, Any]) -> str:
        """
        Format changes dictionary into HTML list.

        Args:
            changes: Dictionary with field: {old, new} structure

        Returns:
            str: Formatted HTML list of changes
        """
        if not changes:
            return "Task details have been modified."

        html = "<ul>"
        for field, change in changes.items():
            old_value = change.get("old", "")
            new_value = change.get("new", "")
            html += f"<li><strong>{field}:</strong> {old_value} → {new_value}</li>"
        html += "</ul>"

        return html


# Global email service instance
email_service = EmailService()
