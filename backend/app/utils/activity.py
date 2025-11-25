"""
Activity logging utility functions for tracking user actions and system events.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request
from backend.app.models.activity import ActivityLog


def log_activity(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> ActivityLog:
    """
    Create an activity log entry.
    
    Args:
        db: Database session
        action: Action type (e.g., "user.login", "org.create", "member.add")
        user_id: ID of the user who performed the action (optional)
        resource_type: Type of resource affected (e.g., "user", "organization")
        resource_id: ID of the affected resource (optional)
        organization_id: ID of the organization (if applicable)
        details: Additional context as a dictionary (will be stored as JSON)
        ip_address: IP address of the client (optional)
        user_agent: User agent string (optional)
    
    Returns:
        The created ActivityLog instance
    """
    log = ActivityLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        organization_id=organization_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log


def log_activity_from_request(
    db: Session,
    request: Request,
    action: str,
    user_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
) -> ActivityLog:
    """
    Create an activity log entry with IP address and user agent extracted from the request.
    
    This is a convenience function that automatically extracts:
    - IP address from request.client.host
    - User agent from request.headers.get("user-agent")
    
    Args:
        db: Database session
        request: FastAPI Request object
        action: Action type (e.g., "user.login", "org.create")
        user_id: ID of the user who performed the action (optional)
        resource_type: Type of resource affected (e.g., "user", "organization")
        resource_id: ID of the affected resource (optional)
        organization_id: ID of the organization (if applicable)
        details: Additional context as a dictionary
    
    Returns:
        The created ActivityLog instance
    """
    # Extract IP address
    ip_address = None
    if request.client:
        ip_address = request.client.host
    
    # Extract user agent
    user_agent = request.headers.get("user-agent")
    
    return log_activity(
        db=db,
        action=action,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        organization_id=organization_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )


# Common action constants for consistency
class ActivityAction:
    """Standard action names for activity logging."""
    
    # User actions
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_REGISTER = "user.register"
    USER_PROFILE_UPDATE = "user.profile.update"
    USER_PASSWORD_CHANGE = "user.password.change"
    USER_PASSWORD_RESET_REQUEST = "user.password.reset.request"
    USER_PASSWORD_RESET = "user.password.reset"
    USER_AVATAR_UPLOAD = "user.avatar.upload"
    
    # Organization actions
    ORG_CREATE = "organization.create"
    ORG_UPDATE = "organization.update"
    ORG_DELETE = "organization.delete"
    
    # Membership actions
    MEMBERSHIP_CREATE = "membership.create"
    MEMBERSHIP_UPDATE = "membership.update"
    MEMBERSHIP_DELETE = "membership.delete"
    
    # Invitation actions
    INVITATION_CREATE = "invitation.create"
    INVITATION_ACCEPT = "invitation.accept"
    INVITATION_DECLINE = "invitation.decline"
    INVITATION_EXPIRE = "invitation.expire"


# Common resource types for consistency
class ResourceType:
    """Standard resource type names for activity logging."""
    USER = "user"
    ORGANIZATION = "organization"
    MEMBERSHIP = "membership"
    INVITATION = "invitation"

