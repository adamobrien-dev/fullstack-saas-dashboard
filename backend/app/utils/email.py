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
        
        # Provide helpful error message for Resend limitations
        if "only send testing emails to your own email address" in error_msg.lower():
            raise ValueError(
                f"Resend limitation: {error_msg}. "
                "Either send to your verified email address, or verify a domain at resend.com/domains"
            ) from e
        
        raise Exception(f"Error sending email: {error_msg}") from e


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
