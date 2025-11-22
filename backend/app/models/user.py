from sqlalchemy import Column, Integer, String, DateTime, func
from backend.app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="member")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Password reset fields
    password_reset_token = Column(String(255), nullable=True, index=True)
    password_reset_expires_at = Column(DateTime(timezone=True), nullable=True)
