from fastapi import APIRouter, Depends, HTTPException, status, Path, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from datetime import datetime, timedelta, timezone
import uuid
from typing import List

from backend.app.deps.auth import get_current_user, get_db
from backend.app.deps.rbac import require_role
from backend.app.models.user import User
from backend.app.models.organization import Organization, Membership, Invitation
from backend.app.schema.organization import (
    OrgCreate, OrgOut, InviteIn, InviteAccept, InviteOut,
    MemberOut, UpdateMemberRole
)
from backend.app.utils.email import send_invitation_email
from backend.app.utils.activity import log_activity_from_request, ActivityAction, ResourceType

router = APIRouter()


@router.post("/orgs", response_model=OrgOut, status_code=201)
def create_organization(
    payload: OrgCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization. Creator becomes owner."""
    org = Organization(name=payload.name)
    db.add(org)
    db.flush()  # Get org.id
    
    # Create membership as owner
    membership = Membership(
        org_id=org.id,
        user_id=current_user.id,
        role="owner"
    )
    db.add(membership)
    db.commit()
    db.refresh(org)
    
    # Log activity
    log_activity_from_request(
        db=db,
        request=request,
        action=ActivityAction.ORG_CREATE,
        user_id=current_user.id,
        resource_type=ResourceType.ORGANIZATION,
        resource_id=org.id,
        organization_id=org.id,
        details={"name": org.name}
    )
    
    return org


@router.get("/orgs/mine", response_model=List[OrgOut])
def list_my_organizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all organizations the current user belongs to."""
    memberships = db.execute(
        select(Membership).where(Membership.user_id == current_user.id)
    ).scalars().all()
    
    org_ids = [m.org_id for m in memberships]
    if not org_ids:
        return []
    
    orgs = db.execute(
        select(Organization).where(Organization.id.in_(org_ids))
    ).scalars().all()
    
    return orgs


@router.post("/orgs/{org_id}/invite", response_model=InviteOut, status_code=201)
def create_invitation(
    org_id: int,
    payload: InviteIn,
    request: Request,
    background_tasks: BackgroundTasks,
    ctx: tuple = Depends(require_role({"owner", "admin"})),
    db: Session = Depends(get_db)
):
    """Create an invitation and send email notification. Only owner/admin can invite."""
    current_user, membership = ctx
    
    # Get organization
    org = db.execute(select(Organization).where(Organization.id == org_id)).scalars().first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Validate role
    if payload.role not in ["owner", "admin", "member"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: owner, admin, or member"
        )
    
    # Only owner can invite as owner
    if payload.role == "owner" and membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can invite as owner"
        )
    
    # Check if user is already a member
    existing_member = db.execute(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.user_id == select(User.id).where(User.email == payload.email).scalar_subquery()
        )
    ).scalars().first()
    
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member of this organization"
        )
    
    # Check for existing pending invitation
    existing_invite = db.execute(
        select(Invitation).where(
            and_(
                Invitation.org_id == org_id,
                Invitation.email == payload.email,
                Invitation.status == "pending"
            )
        )
    ).scalars().first()
    
    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation already sent to this email"
        )
    
    # Create invitation
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    invitation = Invitation(
        org_id=org_id,
        email=payload.email,
        role=payload.role,
        token=token,
        status="pending",
        expires_at=expires_at
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    
    # Log activity
    log_activity_from_request(
        db=db,
        request=request,
        action=ActivityAction.INVITATION_CREATE,
        user_id=current_user.id,
        resource_type=ResourceType.INVITATION,
        resource_id=invitation.id,
        organization_id=org_id,
        details={"email": payload.email, "role": payload.role}
    )
    
    # Send invitation email in background (don't fail invitation creation if email fails)
    try:
        send_invitation_email(
            email=payload.email,
            organization_name=org.name,
            inviter_name=current_user.name,
            role=payload.role,
            invitation_token=token,
            background_tasks=background_tasks
        )
    except Exception as e:
        # Log error but don't fail invitation creation
        print(f"[WARNING] Failed to send invitation email: {str(e)}")
        # Invitation is still created and can be accepted via UI
    
    return invitation


@router.get("/orgs/invitations/pending", response_model=List[InviteOut])
def list_pending_invitations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all pending invitations for the current user's email."""
    invitations = db.execute(
        select(Invitation)
        .where(
            and_(
                Invitation.email == current_user.email,
                Invitation.status == "pending",
                or_(
                    Invitation.expires_at.is_(None),
                    Invitation.expires_at > datetime.now(timezone.utc)
                )
            )
        )
    ).scalars().all()
    
    return invitations


@router.post("/orgs/accept", response_model=MemberOut, status_code=201)
def accept_invitation(
    payload: InviteAccept,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept an invitation and join the organization."""
    invitation = db.execute(
        select(Invitation).where(Invitation.token == payload.token)
    ).scalars().first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation already {invitation.status}"
        )
    
    if invitation.email != current_user.email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This invitation was sent to a different email address"
        )
    
    if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Check if already a member
    existing = db.execute(
        select(Membership).where(
            Membership.org_id == invitation.org_id,
            Membership.user_id == current_user.id
        )
    ).scalars().first()
    
    if existing:
        invitation.status = "accepted"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this organization"
        )
    
    # Create membership
    membership = Membership(
        org_id=invitation.org_id,
        user_id=current_user.id,
        role=invitation.role
    )
    db.add(membership)
    
    # Update invitation status
    invitation.status = "accepted"
    
    db.commit()
    db.refresh(membership)
    
    # Log activity
    log_activity_from_request(
        db=db,
        request=request,
        action=ActivityAction.INVITATION_ACCEPT,
        user_id=current_user.id,
        resource_type=ResourceType.MEMBERSHIP,
        resource_id=membership.id,
        organization_id=invitation.org_id,
        details={"role": invitation.role, "invitation_email": invitation.email}
    )
    
    # Also log membership creation
    log_activity_from_request(
        db=db,
        request=request,
        action=ActivityAction.MEMBERSHIP_CREATE,
        user_id=current_user.id,
        resource_type=ResourceType.MEMBERSHIP,
        resource_id=membership.id,
        organization_id=invitation.org_id,
        details={"role": invitation.role}
    )
    
    # Return member with user info (we already have current_user)
    return MemberOut(
        id=membership.id,
        user_id=membership.user_id,
        org_id=membership.org_id,
        role=membership.role,
        created_at=membership.created_at,
        user_email=current_user.email,
        user_name=current_user.name
    )


@router.get("/orgs/{org_id}/members", response_model=List[MemberOut])
def list_members(
    org_id: int,
    ctx: tuple = Depends(require_role()),
    db: Session = Depends(get_db)
):
    """List all members of an organization. Any member can view."""
    members = db.execute(
        select(Membership, User)
        .join(User, Membership.user_id == User.id)
        .where(Membership.org_id == org_id)
    ).all()
    
    return [
        MemberOut(
            id=m.Membership.id,
            user_id=m.Membership.user_id,
            org_id=m.Membership.org_id,
            role=m.Membership.role,
            created_at=m.Membership.created_at,
            user_email=m.User.email,
            user_name=m.User.name
        )
        for m in members
    ]


@router.patch("/orgs/{org_id}/members/{user_id}", response_model=MemberOut)
def update_member_role(
    org_id: int,
    user_id: int,
    payload: UpdateMemberRole,
    ctx: tuple = Depends(require_role({"owner", "admin"})),
    db: Session = Depends(get_db)
):
    """Update a member's role. Only owner/admin can update."""
    current_user, membership = ctx
    
    # Validate role
    if payload.role not in ["owner", "admin", "member"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: owner, admin, or member"
        )
    
    # Get target membership
    target_membership = db.execute(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.user_id == user_id
        )
    ).scalars().first()
    
    if not target_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Only owner can assign owner role
    if payload.role == "owner" and membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can assign owner role"
        )
    
    # Prevent changing own role if you're the only owner
    if target_membership.user_id == current_user.id and target_membership.role == "owner":
        # Check if there are other owners
        other_owners = db.execute(
            select(Membership).where(
                Membership.org_id == org_id,
                Membership.role == "owner",
                Membership.user_id != current_user.id
            )
        ).scalars().first()
        
        if not other_owners:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change role: you are the only owner"
            )
    
    # Update role
    target_membership.role = payload.role
    db.commit()
    db.refresh(target_membership)
    
    # Get user info
    user = db.execute(select(User).where(User.id == user_id)).scalars().first()
    
    return MemberOut(
        id=target_membership.id,
        user_id=target_membership.user_id,
        org_id=target_membership.org_id,
        role=target_membership.role,
        created_at=target_membership.created_at,
        user_email=user.email,
        user_name=user.name
    )


@router.delete("/orgs/{org_id}/members/{user_id}", status_code=204)
def remove_member(
    org_id: int,
    user_id: int,
    ctx: tuple = Depends(require_role({"owner", "admin"})),
    db: Session = Depends(get_db)
):
    """Remove a member from organization. Only owner/admin can remove."""
    current_user, membership = ctx
    
    # Get target membership
    target_membership = db.execute(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.user_id == user_id
        )
    ).scalars().first()
    
    if not target_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Only owner can remove owner
    if target_membership.role == "owner" and membership.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can remove owners"
        )
    
    # Prevent removing yourself if you're the only owner
    if target_membership.user_id == current_user.id and target_membership.role == "owner":
        other_owners = db.execute(
            select(Membership).where(
                Membership.org_id == org_id,
                Membership.role == "owner",
                Membership.user_id != current_user.id
            )
        ).scalars().first()
        
        if not other_owners:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove yourself: you are the only owner"
            )
    
    db.delete(target_membership)
    db.commit()
    return None

