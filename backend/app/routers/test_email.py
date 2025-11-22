from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from backend.app.deps.auth import get_current_user, get_db
from backend.app.models.user import User
from backend.app.utils.email import send_email_background, send_email

router = APIRouter()


@router.post("/test-email")
async def test_email(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Test endpoint to send a test email using Resend.
    Only works when RESEND_API_KEY is configured.
    """
    from fastapi import HTTPException
    
    test_subject = "Test Email from SaaS Dashboard"
    test_body = """
    <h1>Test Email</h1>
    <p>This is a test email from your SaaS Dashboard.</p>
    <p>If you received this, the Resend email service is working correctly!</p>
    """
    
    try:
        # Send email to current user
        result = await send_email(
            recipients=[current_user.email],
            subject=test_subject,
            body=test_body
        )
        
        return {
            "message": "Test email sent successfully",
            "recipient": current_user.email,
            "email_id": result.get("id") if isinstance(result, dict) else None,
            "note": "Check your inbox (and spam folder)"
        }
    except ValueError as e:
        # API key not configured
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        # Other email sending errors
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/test-email-background")
async def test_email_background(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Test endpoint to send a test email in background.
    This demonstrates async background task processing.
    """
    test_subject = "Background Test Email from SaaS Dashboard"
    test_body = """
    <h1>Background Test Email</h1>
    <p>This email was sent as a background task.</p>
    <p>If you received this, background email processing is working!</p>
    """
    
    # Schedule email to be sent in background
    send_email_background(
        background_tasks=background_tasks,
        recipients=[current_user.email],
        subject=test_subject,
        body=test_body
    )
    
    return {
        "message": "Test email scheduled in background",
        "recipient": current_user.email,
        "note": "Check your inbox (and spam folder). Response returned immediately."
    }


@router.delete("/delete-user/{email}")
def delete_user_by_email(
    email: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test endpoint to delete a user by email address.
    WARNING: Only use for testing! This permanently deletes the user.
    """
    user = db.execute(select(User).where(User.email == email)).scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")
    
    user_email = user.email
    db.delete(user)
    db.commit()
    
    return {
        "message": f"User {user_email} deleted successfully",
        "deleted_email": user_email,
        "note": "This is a test endpoint. Use with caution!"
    }

