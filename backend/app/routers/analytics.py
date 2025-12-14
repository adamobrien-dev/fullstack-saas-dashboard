"""
Analytics API endpoints for dashboard statistics and metrics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy import Date
from sqlalchemy.sql import cast
from datetime import datetime, timedelta, timezone
from typing import Optional

from backend.app.deps.auth import get_current_user, get_db
from backend.app.models.user import User
from backend.app.models.organization import Organization, Membership
from backend.app.models.activity import ActivityLog
from backend.app.schema.analytics import (
    UserStats, ActivityStats, OrganizationStats,
    DashboardStats, ActivityTimeSeries, TimeSeriesDataPoint,
    UserGrowthTimeSeries
)

router = APIRouter()


def get_start_of_day(dt: datetime) -> datetime:
    """Get the start of the day for a given datetime."""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_start_of_week(dt: datetime) -> datetime:
    """Get the start of the week (Monday) for a given datetime."""
    days_since_monday = dt.weekday()
    start = dt - timedelta(days=days_since_monday)
    return get_start_of_day(start)


def get_start_of_month(dt: datetime) -> datetime:
    """Get the start of the month for a given datetime."""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


@router.get("/analytics/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard statistics including user, activity, and organization stats.
    """
    now = datetime.now(timezone.utc)
    start_of_today = get_start_of_day(now)
    start_of_week = get_start_of_week(now)
    start_of_month = get_start_of_month(now)
    
    # User Statistics
    total_users = db.execute(select(func.count(User.id))).scalar() or 0
    new_users_today = db.execute(
        select(func.count(User.id)).where(User.created_at >= start_of_today)
    ).scalar() or 0
    new_users_this_week = db.execute(
        select(func.count(User.id)).where(User.created_at >= start_of_week)
    ).scalar() or 0
    new_users_this_month = db.execute(
        select(func.count(User.id)).where(User.created_at >= start_of_month)
    ).scalar() or 0
    
    # Active users (users who have activity logs)
    active_users_today = db.execute(
        select(func.count(func.distinct(ActivityLog.user_id)))
        .where(ActivityLog.created_at >= start_of_today)
    ).scalar() or 0
    active_users_this_week = db.execute(
        select(func.count(func.distinct(ActivityLog.user_id)))
        .where(ActivityLog.created_at >= start_of_week)
    ).scalar() or 0
    active_users_this_month = db.execute(
        select(func.count(func.distinct(ActivityLog.user_id)))
        .where(ActivityLog.created_at >= start_of_month)
    ).scalar() or 0
    
    user_stats = UserStats(
        total_users=total_users,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        new_users_this_month=new_users_this_month,
        active_users_today=active_users_today,
        active_users_this_week=active_users_this_week,
        active_users_this_month=active_users_this_month
    )
    
    # Activity Statistics
    total_activities = db.execute(select(func.count(ActivityLog.id))).scalar() or 0
    activities_today = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= start_of_today)
    ).scalar() or 0
    activities_this_week = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= start_of_week)
    ).scalar() or 0
    activities_this_month = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= start_of_month)
    ).scalar() or 0
    
    # Activities by action
    activities_by_action_raw = db.execute(
        select(ActivityLog.action, func.count(ActivityLog.id))
        .group_by(ActivityLog.action)
    ).all()
    activities_by_action = {action: count for action, count in activities_by_action_raw}
    
    # Activities by resource type
    activities_by_resource_type_raw = db.execute(
        select(ActivityLog.resource_type, func.count(ActivityLog.id))
        .where(ActivityLog.resource_type.isnot(None))
        .group_by(ActivityLog.resource_type)
    ).all()
    activities_by_resource_type = {rtype: count for rtype, count in activities_by_resource_type_raw}
    
    activity_stats = ActivityStats(
        total_activities=total_activities,
        activities_today=activities_today,
        activities_this_week=activities_this_week,
        activities_this_month=activities_this_month,
        activities_by_action=activities_by_action,
        activities_by_resource_type=activities_by_resource_type
    )
    
    # Organization Statistics
    total_organizations = db.execute(select(func.count(Organization.id))).scalar() or 0
    total_memberships = db.execute(select(func.count(Membership.id))).scalar() or 0
    average_members_per_org = (
        total_memberships / total_organizations if total_organizations > 0 else 0.0
    )
    
    organizations_created_today = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= start_of_today)
    ).scalar() or 0
    organizations_created_this_week = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= start_of_week)
    ).scalar() or 0
    organizations_created_this_month = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= start_of_month)
    ).scalar() or 0
    
    organization_stats = OrganizationStats(
        total_organizations=total_organizations,
        total_memberships=total_memberships,
        average_members_per_org=round(average_members_per_org, 2),
        organizations_created_today=organizations_created_today,
        organizations_created_this_week=organizations_created_this_week,
        organizations_created_this_month=organizations_created_this_month
    )
    
    # Activity Timeline (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    timeline_data = db.execute(
        select(
            cast(ActivityLog.created_at, Date).label('date'),
            func.count(ActivityLog.id).label('count')
        )
        .where(ActivityLog.created_at >= thirty_days_ago)
        .group_by(cast(ActivityLog.created_at, Date))
        .order_by('date')
    ).all()
    
    timeline_points = [
        TimeSeriesDataPoint(
            date=row.date.isoformat(),
            count=row.count
        )
        for row in timeline_data
    ]
    
    activity_timeline = ActivityTimeSeries(
        period="day",
        data=timeline_points
    )
    
    return DashboardStats(
        user_stats=user_stats,
        activity_stats=activity_stats,
        organization_stats=organization_stats,
        activity_timeline=activity_timeline
    )


@router.get("/analytics/users/stats", response_model=UserStats)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    now = datetime.now(timezone.utc)
    start_of_today = get_start_of_day(now)
    start_of_week = get_start_of_week(now)
    start_of_month = get_start_of_month(now)
    
    total_users = db.execute(select(func.count(User.id))).scalar() or 0
    new_users_today = db.execute(
        select(func.count(User.id)).where(User.created_at >= start_of_today)
    ).scalar() or 0
    new_users_this_week = db.execute(
        select(func.count(User.id)).where(User.created_at >= start_of_week)
    ).scalar() or 0
    new_users_this_month = db.execute(
        select(func.count(User.id)).where(User.created_at >= start_of_month)
    ).scalar() or 0
    
    active_users_today = db.execute(
        select(func.count(func.distinct(ActivityLog.user_id)))
        .where(ActivityLog.created_at >= start_of_today)
    ).scalar() or 0
    active_users_this_week = db.execute(
        select(func.count(func.distinct(ActivityLog.user_id)))
        .where(ActivityLog.created_at >= start_of_week)
    ).scalar() or 0
    active_users_this_month = db.execute(
        select(func.count(func.distinct(ActivityLog.user_id)))
        .where(ActivityLog.created_at >= start_of_month)
    ).scalar() or 0
    
    return UserStats(
        total_users=total_users,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        new_users_this_month=new_users_this_month,
        active_users_today=active_users_today,
        active_users_this_week=active_users_this_week,
        active_users_this_month=active_users_this_month
    )


@router.get("/analytics/users/growth", response_model=UserGrowthTimeSeries)
def get_user_growth(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user growth time series data."""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    growth_data = db.execute(
        select(
            cast(User.created_at, Date).label('date'),
            func.count(User.id).label('count')
        )
        .where(User.created_at >= start_date)
        .group_by(cast(User.created_at, Date))
        .order_by('date')
    ).all()
    
    data_points = [
        TimeSeriesDataPoint(
            date=row.date.isoformat(),
            count=row.count
        )
        for row in growth_data
    ]
    
    return UserGrowthTimeSeries(
        period="day",
        data=data_points
    )


@router.get("/analytics/activities/stats", response_model=ActivityStats)
def get_activity_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity statistics."""
    now = datetime.now(timezone.utc)
    start_of_today = get_start_of_day(now)
    start_of_week = get_start_of_week(now)
    start_of_month = get_start_of_month(now)
    
    total_activities = db.execute(select(func.count(ActivityLog.id))).scalar() or 0
    activities_today = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= start_of_today)
    ).scalar() or 0
    activities_this_week = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= start_of_week)
    ).scalar() or 0
    activities_this_month = db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.created_at >= start_of_month)
    ).scalar() or 0
    
    activities_by_action_raw = db.execute(
        select(ActivityLog.action, func.count(ActivityLog.id))
        .group_by(ActivityLog.action)
    ).all()
    activities_by_action = {action: count for action, count in activities_by_action_raw}
    
    activities_by_resource_type_raw = db.execute(
        select(ActivityLog.resource_type, func.count(ActivityLog.id))
        .where(ActivityLog.resource_type.isnot(None))
        .group_by(ActivityLog.resource_type)
    ).all()
    activities_by_resource_type = {rtype: count for rtype, count in activities_by_resource_type_raw}
    
    return ActivityStats(
        total_activities=total_activities,
        activities_today=activities_today,
        activities_this_week=activities_this_week,
        activities_this_month=activities_this_month,
        activities_by_action=activities_by_action,
        activities_by_resource_type=activities_by_resource_type
    )


@router.get("/analytics/activities/timeline", response_model=ActivityTimeSeries)
def get_activity_timeline(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    period: str = Query("day", regex="^(day|week|month)$", description="Aggregation period"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity timeline data."""
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    if period == "day":
        date_func = cast(ActivityLog.created_at, Date)
    elif period == "week":
        # Group by week (Monday as start)
        date_func = func.date_trunc('week', ActivityLog.created_at)
    else:  # month
        date_func = func.date_trunc('month', ActivityLog.created_at)
    
    timeline_data = db.execute(
        select(
            date_func.label('date'),
            func.count(ActivityLog.id).label('count')
        )
        .where(ActivityLog.created_at >= start_date)
        .group_by(date_func)
        .order_by('date')
    ).all()
    
    data_points = [
        TimeSeriesDataPoint(
            date=str(row.date) if isinstance(row.date, datetime) else row.date.isoformat(),
            count=row.count
        )
        for row in timeline_data
    ]
    
    return ActivityTimeSeries(
        period=period,
        data=data_points
    )


@router.get("/analytics/organizations/stats", response_model=OrganizationStats)
def get_organization_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get organization statistics."""
    now = datetime.now(timezone.utc)
    start_of_today = get_start_of_day(now)
    start_of_week = get_start_of_week(now)
    start_of_month = get_start_of_month(now)
    
    total_organizations = db.execute(select(func.count(Organization.id))).scalar() or 0
    total_memberships = db.execute(select(func.count(Membership.id))).scalar() or 0
    average_members_per_org = (
        total_memberships / total_organizations if total_organizations > 0 else 0.0
    )
    
    organizations_created_today = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= start_of_today)
    ).scalar() or 0
    organizations_created_this_week = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= start_of_week)
    ).scalar() or 0
    organizations_created_this_month = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= start_of_month)
    ).scalar() or 0
    
    return OrganizationStats(
        total_organizations=total_organizations,
        total_memberships=total_memberships,
        average_members_per_org=round(average_members_per_org, 2),
        organizations_created_today=organizations_created_today,
        organizations_created_this_week=organizations_created_this_week,
        organizations_created_this_month=organizations_created_this_month
    )
