from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Set, Tuple, Callable
from backend.app.deps.auth import get_current_user, get_db
from backend.app.models.user import User
from backend.app.models.organization import Membership


def require_role(allowed_roles: Set[str] = None):
    """
    Factory function that returns a dependency ensuring the current user has one of the allowed roles.
    Usage: Depends(require_role({"owner", "admin"}))
    """
    if allowed_roles is None:
        allowed_roles = {"owner", "admin", "member"}
    
    def dependency(
        org_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> Tuple[User, Membership]:
        # Get membership
        membership = db.execute(
            select(Membership).where(
                Membership.org_id == org_id,
                Membership.user_id == current_user.id
            )
        ).scalars().first()
        
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organization"
            )
        
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(allowed_roles)}. Your role: {membership.role}"
            )
        
        return (current_user, membership)
    
    return dependency



