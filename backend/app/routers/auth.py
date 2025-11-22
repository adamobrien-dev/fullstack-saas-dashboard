from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import uuid
from backend.app.models.user import User
from backend.app.schema.user import UserCreate, UserLogin, UserOut, PasswordResetRequest, PasswordReset
from backend.app.utils.password import hash_password, verify_password
from backend.app.utils.jwt import create_access_token, create_refresh_token, verify_token
from backend.app.deps.auth import get_current_user, get_db
from backend.app.utils.email import send_welcome_email, send_password_reset_email

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=201)
def register(
    payload: UserCreate,
    response: Response,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    existing = db.execute(select(User).where(User.email == payload.email)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    u = User(
        email=str(payload.email),
        name=payload.name,
        password_hash=hash_password(payload.password),
        role="member",
    )
    try:
        db.add(u)
        db.commit()
        db.refresh(u)
        
        # Automatically sign in after registration
        access_token = create_access_token(data={"sub": str(u.id)})
        refresh_token = create_refresh_token(data={"sub": str(u.id)})
        
        # Set HttpOnly cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=30 * 60  # 30 minutes
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/",
            max_age=7 * 24 * 60 * 60  # 7 days
        )
        
        # Send welcome email in background (don't fail registration if email fails)
        try:
            send_welcome_email(
                email=str(payload.email),
                user_name=payload.name,
                background_tasks=background_tasks
            )
        except Exception as e:
            # Log error but don't fail registration
            print(f"[WARNING] Failed to send welcome email: {str(e)}")
        
        return u
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")

@router.post("/login")
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    u = db.execute(select(User).where(User.email == payload.email)).scalars().first()
    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create tokens (sub must be a string)
    access_token = create_access_token(data={"sub": str(u.id)})
    refresh_token = create_refresh_token(data={"sub": str(u.id)})
    
    # Set HttpOnly cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        path="/",
        max_age=30 * 60  # 30 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    return {"message": "Login successful", "user": UserOut.model_validate(u)}

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/refresh")
def refresh_token_endpoint(response: Response, refresh_token_cookie: str = Cookie(None, alias="refresh_token")):
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    payload = verify_token(refresh_token_cookie)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Convert to int and back to string (sub is stored as string)
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID in token")
    
    # Issue new access token (sub must be a string)
    new_access_token = create_access_token(data={"sub": str(user_id)})
    
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=30 * 60
    )
    
    return {"message": "Token refreshed"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/", samesite="lax")
    response.delete_cookie(key="refresh_token", path="/", samesite="lax")
    return {"message": "Logged out successfully"}


@router.post("/password-reset-request")
def request_password_reset(
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request a password reset. Sends an email with a reset link.
    Always returns success to prevent email enumeration attacks.
    """
    user = db.execute(select(User).where(User.email == payload.email)).scalars().first()
    
    # Always return success message (even if user doesn't exist)
    # This prevents email enumeration attacks
    if not user:
        return {"message": "If that email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)  # Token valid for 1 hour
    
    # Store token and expiry in user record
    user.password_reset_token = reset_token
    user.password_reset_expires_at = expires_at
    db.commit()
    
    # Send password reset email in background
    try:
        send_password_reset_email(
            email=user.email,
            user_name=user.name,
            reset_token=reset_token,
            background_tasks=background_tasks
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"[WARNING] Failed to send password reset email: {str(e)}")
    
    return {"message": "If that email exists, a password reset link has been sent"}


@router.post("/password-reset")
def reset_password(
    payload: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset password using the token from the email.
    """
    # Find user by reset token
    user = db.execute(
        select(User).where(
            User.password_reset_token == payload.token
        )
    ).scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    # Check if token has expired
    if user.password_reset_expires_at and user.password_reset_expires_at < datetime.now(timezone.utc):
        # Clear expired token
        user.password_reset_token = None
        user.password_reset_expires_at = None
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Reset token has expired. Please request a new one."
        )
    
    # Update password
    user.password_hash = hash_password(payload.new_password)
    user.password_reset_token = None
    user.password_reset_expires_at = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now log in with your new password."}
