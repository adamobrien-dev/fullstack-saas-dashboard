from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func, and_
from typing import Optional
from datetime import datetime, timezone

from backend.app.deps.auth import get_current_user, get_db
from backend.app.models.user import User
from backend.app.models.notification import Notification
from backend.app.schema.notification import NotificationOut, NotificationList, MarkNotificationRead

router = APIRouter()


@router.get("/notifications", response_model=NotificationList)
def get_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get notifications for the current user.
    Users can only see their own notifications.
    """
    # Build query - only current user's notifications
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    # Apply filters
    if is_read is not None:
        query = query.where(Notification.is_read == is_read)
    
    if type:
        query = query.where(Notification.type == type)
    
    # Get total count before pagination
    total_query = select(func.count()).select_from(query.subquery())
    total = db.execute(total_query).scalar() or 0
    
    # Get unread count
    unread_count_query = select(func.count()).where(
        and_(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        )
    )
    unread_count = db.execute(unread_count_query.select_from(Notification)).scalar() or 0
    
    # Apply pagination and ordering (newest first)
    offset = (page - 1) * page_size
    query = query.order_by(desc(Notification.created_at)).offset(offset).limit(page_size)
    
    # Execute query
    notifications = db.execute(query).scalars().all()
    
    return NotificationList(
        notifications=[NotificationOut.model_validate(n) for n in notifications],
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size
    )


@router.get("/notifications/unread-count", response_model=dict)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the count of unread notifications for the current user."""
    unread_count = db.execute(
        select(func.count()).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        ).select_from(Notification)
    ).scalar() or 0
    
    return {"unread_count": unread_count}


@router.get("/notifications/{notification_id}", response_model=NotificationOut)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification by ID. User must own the notification."""
    notification = db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return NotificationOut.model_validate(notification)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read."""
    notification = db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(notification)
    
    return NotificationOut.model_validate(notification)


@router.post("/notifications/mark-read", response_model=dict)
def mark_notifications_read(
    data: MarkNotificationRead,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark multiple notifications as read."""
    # Verify all notifications belong to current user
    notifications = db.execute(
        select(Notification).where(
            and_(
                Notification.id.in_(data.notification_ids),
                Notification.user_id == current_user.id
            )
        )
    ).scalars().all()
    
    if len(notifications) != len(data.notification_ids):
        raise HTTPException(
            status_code=400,
            detail="Some notifications not found or do not belong to current user"
        )
    
    # Mark as read
    now = datetime.now(timezone.utc)
    count = 0
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = now
            count += 1
    
    db.commit()
    
    return {"marked_read": count, "total_requested": len(data.notification_ids)}


@router.post("/notifications/mark-all-read", response_model=dict)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all unread notifications as read for the current user."""
    notifications = db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False
            )
        )
    ).scalars().all()
    
    now = datetime.now(timezone.utc)
    count = 0
    for notification in notifications:
        notification.is_read = True
        notification.read_at = now
        count += 1
    
    db.commit()
    
    return {"marked_read": count}


@router.delete("/notifications/{notification_id}", response_model=dict)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific notification. User must own the notification."""
    notification = db.execute(
        select(Notification).where(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted successfully"}

