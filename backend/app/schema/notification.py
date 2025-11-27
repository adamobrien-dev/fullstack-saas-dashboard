from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class NotificationOut(BaseModel):
    """Schema for notification output."""
    id: int
    user_id: int
    type: str
    title: str
    message: Optional[str] = None
    link_url: Optional[str] = None
    is_read: bool
    read_at: Optional[datetime] = None
    related_resource_type: Optional[str] = None
    related_resource_id: Optional[int] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    """Schema for paginated notification list."""
    notifications: List[NotificationOut]
    total: int
    unread_count: int
    page: int
    page_size: int


class MarkNotificationRead(BaseModel):
    """Schema for marking notification as read."""
    notification_ids: List[int]

