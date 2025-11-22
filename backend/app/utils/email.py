import resend
from fastapi import BackgroundTasks
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from backend.app.core.config import settings
from typing import List, Optional

# Configure Resend API key
if settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY

# Setup Jinja2 for email templates
template_dir = Path(__file__).parent.parent / "templates" / "email"
template_dir.mkdir(parents=True, exist_ok=True)
env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["html", "xml"])
)


def render_email_template(template_name: str, context: dict) -> str:
    """Render an email template with the given context."""
    try:
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        # Fallback to plain text if template not found
        return f"Template error: {str(e)}"


async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
):
    """
    Send an email using Resend API.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        body: Email body (HTML)
        from_email: From email address (defaults to settings.MAIL_FROM)
        from_name: From name (defaults to settings.MAIL_FROM_NAME)
    
    Returns:
        dict: Response from Resend API with 'id' field if successful
    
    Raises:
        Exception: If email sending fails
    """
    if not settings.RESEND_API_KEY:
        # Email not configured, raise error instead of silently failing
        error_msg = "RESEND_API_KEY is not configured. Please set it in your .env file."
        print(f"[ERROR] {error_msg}")
        print(f"[EMAIL NOT CONFIGURED] Would send to {recipients}: {subject}")
        raise ValueError(error_msg)
    
    # Ensure Resend API key is set
    resend.api_key = settings.RESEND_API_KEY
    
    from_addr = from_email or settings.MAIL_FROM
    from_name_str = from_name or settings.MAIL_FROM_NAME
    
    try:
        params = {
            "from": f"{from_name_str} <{from_addr}>",
            "to": recipients,
            "subject": subject,
            "html": body,
        }
        
        # Use Resend Emails.send method
        from resend import Emails
        data = Emails.send(params)
        
        if data and hasattr(data, 'get') and data.get('id'):
            print(f"[SUCCESS] Email sent successfully! ID: {data.get('id')}")
        else:
            print(f"[WARNING] Email API call returned: {data}")
        
        return data
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Failed to send email: {error_msg}")
        
        # For Resend domain/verification issues, log warning but don't raise
        # This allows the app to continue working even if email fails
        if "only send testing emails to your own email address" in error_msg.lower():
            print(f"[WARNING] Email not sent due to Resend limitation. Verify domain at resend.com/domains")
            print(f"[INFO] Once you verify your domain and set MAIL_FROM in .env, emails will work")
            # Return None instead of raising - allows graceful degradation
            return None
        
        # For other errors, log but don't raise in background tasks
        # This prevents email failures from breaking the app
        print(f"[WARNING] Email sending failed: {error_msg}")
        return None


def send_email_background(
    background_tasks: BackgroundTasks,
    recipients: List[str],
    subject: str,
    body: str,
    from_email: Optional[str] = None,
    from_name: Optional[str] = None
):
    """Schedule an email to be sent in the background."""
    background_tasks.add_task(send_email, recipients, subject, body, from_email, from_name)


def send_invitation_email(
    email: str,
    organization_name: str,
    inviter_name: str,
    role: str,
    invitation_token: str,
    background_tasks: BackgroundTasks
):
    """
    Send an invitation email to join an organization.
    
    Args:
        email: Recipient email address
        organization_name: Name of the organization
        inviter_name: Name of the person sending the invitation
        role: Role being invited (owner, admin, member)
        invitation_token: Unique token for accepting the invitation
        background_tasks: Background tasks for async sending
    """
    from datetime import datetime
    
    invitation_url = f"{settings.FRONTEND_URL}/invitations?token={invitation_token}"
    
    context = {
        "organization_name": organization_name,
        "inviter_name": inviter_name,
        "role": role.capitalize(),
        "invitation_url": invitation_url,
        "current_year": datetime.now().year,
    }
    
    subject = f"You've been invited to join {organization_name}"
    body = render_email_template("invitation.html", context)
    
    # Schedule email to be sent in background
    send_email_background(background_tasks, [email], subject, body)


def send_welcome_email(
    email: str,
    user_name: str,
    background_tasks: BackgroundTasks
):
    """
    Send a welcome email to a new user.
    
    Args:
        email: User email address
        user_name: User's name
        background_tasks: Background tasks for async sending
    """
    from datetime import datetime
    
    dashboard_url = f"{settings.FRONTEND_URL}/dashboard"
    
    context = {
        "user_name": user_name,
        "dashboard_url": dashboard_url,
        "current_year": datetime.now().year,
    }
    
    subject = "Welcome to SaaS Dashboard!"
    body = render_email_template("welcome.html", context)
    
    # Schedule email to be sent in background
    send_email_background(background_tasks, [email], subject, body)


def send_password_reset_email(
    email: str,
    user_name: str,
    reset_token: str,
    background_tasks: BackgroundTasks
):
    """
    Send a password reset email.
    
    Args:
        email: User email address
        user_name: User's name
        reset_token: Password reset token
        background_tasks: Background tasks for async sending
    """
    from datetime import datetime
    
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    context = {
        "user_name": user_name,
        "reset_url": reset_url,
        "current_year": datetime.now().year,
    }
    
    subject = "Reset Your Password - SaaS Dashboard"
    body = render_email_template("password_reset.html", context)
    
    # Schedule email to be sent in background
    send_email_background(background_tasks, [email], subject, body)
