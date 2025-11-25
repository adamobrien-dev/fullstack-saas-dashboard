from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func, desc
from typing import Optional, List
from datetime import datetime, timedelta

from backend.app.deps.auth import get_current_user, get_db
from backend.app.deps.rbac import require_role
from backend.app.models.user import User
from backend.app.models.activity import ActivityLog
from backend.app.models.organization import Membership
from backend.app.schema.activity import ActivityLogOut, ActivityLogList

router = APIRouter()


@router.get("/activity/logs", response_model=ActivityLogList)
def get_activity_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    organization_id: Optional[int] = Query(None, description="Filter by organization ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get activity logs with filtering and pagination.
    Users can only see logs for organizations they belong to, or their own logs.
    """
    # Build query
    query = select(ActivityLog)
    conditions = []
    
    # If not filtering by organization, only show user's own logs or org logs they belong to
    if organization_id is None:
        # Get user's organization IDs
        user_orgs = db.execute(
            select(Membership.org_id).where(Membership.user_id == current_user.id)
        ).scalars().all()
        
        if user_orgs:
            conditions.append(
                or_(
                    ActivityLog.user_id == current_user.id,  # User's own actions
                    ActivityLog.organization_id.in_(user_orgs)  # Actions in user's orgs
                )
            )
        else:
            # User has no orgs, only show their own logs
            conditions.append(ActivityLog.user_id == current_user.id)
    else:
        # Filtering by specific organization - check membership
        membership = db.execute(
            select(Membership).where(
                Membership.org_id == organization_id,
                Membership.user_id == current_user.id
            )
        ).scalars().first()
        
        if not membership:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of this organization"
            )
        
        conditions.append(ActivityLog.organization_id == organization_id)
    
    # Apply filters
    if user_id is not None:
        conditions.append(ActivityLog.user_id == user_id)
    
    if action is not None:
        conditions.append(ActivityLog.action == action)
    
    if resource_type is not None:
        conditions.append(ActivityLog.resource_type == resource_type)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(ActivityLog)
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = db.execute(count_query).scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(desc(ActivityLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # Execute query
    logs = db.execute(query).scalars().all()
    
    # Load related data
    log_dicts = []
    for log in logs:
        log_dict = ActivityLogOut.model_validate(log)
        
        # Add user name if available
        if log.user_id:
            user = db.get(User, log.user_id)
            if user:
                log_dict.user_name = user.name
        
        # Add organization name if available
        if log.organization_id:
            from backend.app.models.organization import Organization
            org = db.get(Organization, log.organization_id)
            if org:
                log_dict.organization_name = org.name
        
        log_dicts.append(log_dict)
    
    return ActivityLogList(
        logs=log_dicts,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/activity/logs/me", response_model=ActivityLogList)
def get_my_activity_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity logs for the current user only."""
    query = select(ActivityLog).where(ActivityLog.user_id == current_user.id)
    
    if action is not None:
        query = query.where(ActivityLog.action == action)
    
    # Get total count
    count_query = select(func.count()).select_from(ActivityLog).where(
        ActivityLog.user_id == current_user.id
    )
    if action is not None:
        count_query = count_query.where(ActivityLog.action == action)
    total = db.execute(count_query).scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(desc(ActivityLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    logs = db.execute(query).scalars().all()
    
    log_dicts = [ActivityLogOut.model_validate(log) for log in logs]
    
    return ActivityLogList(
        logs=log_dicts,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/activity/logs/org/{org_id}", response_model=ActivityLogList)
def get_organization_activity_logs(
    org_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity logs for a specific organization. Requires membership."""
    # Check membership
    membership = db.execute(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.user_id == current_user.id
        )
    ).scalars().first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this organization"
        )
    
    # Build query
    query = select(ActivityLog).where(ActivityLog.organization_id == org_id)
    
    if user_id is not None:
        query = query.where(ActivityLog.user_id == user_id)
    
    if action is not None:
        query = query.where(ActivityLog.action == action)
    
    # Get total count
    count_query = select(func.count()).select_from(ActivityLog).where(
        ActivityLog.organization_id == org_id
    )
    if user_id is not None:
        count_query = count_query.where(ActivityLog.user_id == user_id)
    if action is not None:
        count_query = count_query.where(ActivityLog.action == action)
    total = db.execute(count_query).scalar() or 0
    
    # Apply pagination and ordering
    query = query.order_by(desc(ActivityLog.created_at))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    logs = db.execute(query).scalars().all()
    
    # Load related data
    log_dicts = []
    for log in logs:
        log_dict = ActivityLogOut.model_validate(log)
        
        if log.user_id:
            user = db.get(User, log.user_id)
            if user:
                log_dict.user_name = user.name
        
        from backend.app.models.organization import Organization
        org = db.get(Organization, org_id)
        if org:
            log_dict.organization_name = org.name
        
        log_dicts.append(log_dict)
    
    return ActivityLogList(
        logs=log_dicts,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/activity/logs/{log_id}", response_model=ActivityLogOut)
def get_activity_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific activity log by ID. User must have access to it."""
    log = db.get(ActivityLog, log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Activity log not found")
    
    # Check access: user must own the log or be a member of the organization
    has_access = False
    
    if log.user_id == current_user.id:
        has_access = True
    elif log.organization_id:
        membership = db.execute(
            select(Membership).where(
                Membership.org_id == log.organization_id,
                Membership.user_id == current_user.id
            )
        ).scalars().first()
        if membership:
            has_access = True
    
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this activity log"
        )
    
    log_dict = ActivityLogOut.model_validate(log)
    
    # Add user name if available
    if log.user_id:
        user = db.get(User, log.user_id)
        if user:
            log_dict.user_name = user.name
    
    # Add organization name if available
    if log.organization_id:
        from backend.app.models.organization import Organization
        org = db.get(Organization, log.organization_id)
        if org:
            log_dict.organization_name = org.name
    
    return log_dict

