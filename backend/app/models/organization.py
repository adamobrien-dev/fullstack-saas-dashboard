from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    memberships = relationship("Membership", back_populates="organization", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")


class Membership(Base):
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # owner, admin, member
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", backref="memberships")
    
    # Unique constraint: user can only have one membership per org
    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uq_membership_org_user"),
    )


class Invitation(Base):
    __tablename__ = "invitations"
    
    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # owner, admin, member
    token = Column(String(36), unique=True, nullable=False, index=True)  # UUID
    status = Column(String(20), nullable=False, default="pending")  # pending, accepted, expired
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="invitations")

