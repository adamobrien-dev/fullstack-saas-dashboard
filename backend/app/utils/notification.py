"""
Notification utility functions for creating user notifications.
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    type: str,
    title: str,
    message: Optional[str] = None,
    link_url: Optional[str] = None,
    related_resource_type: Optional[str] = None,
    related_resource_id: Optional[int] = None,
    extra_data: Optional[Dict[str, Any]] = None,
) -> Notification:
    """
    Create a notification for a user.
    
    Args:
        db: Database session
        user_id: ID of the user to notify
        type: Notification type (e.g., "invitation", "activity", "system")
        title: Notification title
        message: Notification message/content (optional)
        link_url: Optional URL to navigate when clicked
        related_resource_type: Type of related resource (e.g., "invitation", "organization")
        related_resource_id: ID of the related resource (optional)
        extra_data: Additional data as a dictionary (will be stored as JSON)
    
    Returns:
        The created Notification instance
    """
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link_url=link_url,
        related_resource_type=related_resource_type,
        related_resource_id=related_resource_id,
        extra_data=extra_data,
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


# Common notification types for consistency
class NotificationType:
    """Standard notification type names."""
    
    # Invitation notifications
    INVITATION_RECEIVED = "invitation.received"
    INVITATION_ACCEPTED = "invitation.accepted"
    INVITATION_EXPIRED = "invitation.expired"
    
    # Activity notifications
    ACTIVITY_MENTION = "activity.mention"
    ACTIVITY_UPDATE = "activity.update"
    
    # System notifications
    SYSTEM_ANNOUNCEMENT = "system.announcement"
    SYSTEM_WARNING = "system.warning"
    
    # Organization notifications
    ORG_MEMBER_ADDED = "organization.member.added"
    ORG_MEMBER_REMOVED = "organization.member.removed"
    ORG_ROLE_CHANGED = "organization.role.changed"
    ORG_INVITATION_SENT = "organization.invitation.sent"

