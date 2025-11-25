from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class ActivityLogOut(BaseModel):
    """Schema for activity log output."""
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    organization_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    # Optional user/organization info
    user_name: Optional[str] = None
    organization_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ActivityLogList(BaseModel):
    """Schema for paginated activity log list."""
    logs: List[ActivityLogOut]
    total: int
    page: int
    page_size: int

