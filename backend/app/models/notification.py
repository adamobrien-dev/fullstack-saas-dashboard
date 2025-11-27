from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.base import Base


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Notification content
    type = Column(String(50), nullable=False, index=True)  # invitation, activity, system, etc.
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    link_url = Column(String(500), nullable=True)  # Optional URL to navigate when clicked
    
    # Read status
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Related resource (optional)
    related_resource_type = Column(String(50), nullable=True, index=True)  # invitation, organization, etc.
    related_resource_id = Column(Integer, nullable=True)
    
    # Extra data for additional information (JSON)
    extra_data = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", backref="notifications")

