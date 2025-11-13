from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class OrgCreate(BaseModel):
    name: str


class OrgOut(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InviteIn(BaseModel):
    email: EmailStr
    role: str  # owner, admin, member


class InviteAccept(BaseModel):
    token: str


class InviteOut(BaseModel):
    id: int
    org_id: int
    email: str
    role: str
    token: str
    status: str
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MemberOut(BaseModel):
    id: int
    user_id: int
    org_id: int
    role: str
    created_at: datetime
    user_email: str
    user_name: str
    
    class Config:
        from_attributes = True


class UpdateMemberRole(BaseModel):
    role: str  # owner, admin, member

