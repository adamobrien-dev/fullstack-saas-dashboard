from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from backend.app.deps.auth import get_current_user, get_db
from backend.app.models.user import User
from backend.app.models.organization import Organization, Membership, Invitation
from backend.app.schema.analytics import (
    DashboardAnalytics,
    UserGrowthMetrics,
    OrganizationStats,
    InvitationMetrics,
    RoleDistribution,
    ActivityMetrics,
    TimeSeriesDataPoint
)

router = APIRouter()


@router.get("/analytics/dashboard", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for the dashboard.
    Returns user growth, organization stats, invitation metrics, role distribution, and activity metrics.
    """
    
    # User Growth Metrics
    total_users = db.execute(select(func.count(User.id))).scalar() or 0
    
    # Get user growth over last 30 days
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    user_growth_query = db.execute(
        select(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        )
        .where(User.created_at >= thirty_days_ago)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
    ).all()
    
    # Fill in missing dates with 0
    growth_dict = {row.date.isoformat(): row.count for row in user_growth_query}
    growth_over_time = []
    for i in range(30):
        date = (datetime.now(timezone.utc) - timedelta(days=29-i)).date()
        date_str = date.isoformat()
        growth_over_time.append(TimeSeriesDataPoint(
            date=date_str,
            value=growth_dict.get(date_str, 0)
        ))
    
    user_growth = UserGrowthMetrics(
        total_users=total_users,
        growth_over_time=growth_over_time
    )
    
    # Organization Statistics
    total_orgs = db.execute(select(func.count(Organization.id))).scalar() or 0
    
    # Get member counts per organization
    member_counts = db.execute(
        select(
            Membership.org_id,
            func.count(Membership.id).label('member_count')
        )
        .group_by(Membership.org_id)
    ).all()
    
    if member_counts:
        member_count_list = [row.member_count for row in member_counts]
        avg_members = sum(member_count_list) / len(member_count_list)
        largest_org = max(member_count_list)
        
        # Distribution: count orgs by size ranges
        distribution = defaultdict(int)
        for count in member_count_list:
            if count == 1:
                distribution["1"] += 1
            elif count <= 5:
                distribution["2-5"] += 1
            elif count <= 10:
                distribution["6-10"] += 1
            else:
                distribution["11+"] += 1
        
        org_size_distribution = [
            {"size": size, "count": count}
            for size, count in sorted(distribution.items())
        ]
    else:
        avg_members = 0.0
        largest_org = 0
        org_size_distribution = []
    
    organization_stats = OrganizationStats(
        total_organizations=total_orgs,
        avg_members_per_org=round(avg_members, 2),
        largest_org_size=largest_org,
        org_size_distribution=org_size_distribution
    )
    
    # Invitation Metrics
    total_invitations = db.execute(select(func.count(Invitation.id))).scalar() or 0
    pending = db.execute(
        select(func.count(Invitation.id))
        .where(Invitation.status == "pending")
    ).scalar() or 0
    accepted = db.execute(
        select(func.count(Invitation.id))
        .where(Invitation.status == "accepted")
    ).scalar() or 0
    expired = db.execute(
        select(func.count(Invitation.id))
        .where(Invitation.status == "expired")
    ).scalar() or 0
    
    acceptance_rate = (accepted / total_invitations * 100) if total_invitations > 0 else 0.0
    
    invitation_metrics = InvitationMetrics(
        total_invitations=total_invitations,
        pending=pending,
        accepted=accepted,
        expired=expired,
        acceptance_rate=round(acceptance_rate, 2)
    )
    
    # Role Distribution
    owners = db.execute(
        select(func.count(Membership.id))
        .where(Membership.role == "owner")
    ).scalar() or 0
    admins = db.execute(
        select(func.count(Membership.id))
        .where(Membership.role == "admin")
    ).scalar() or 0
    members = db.execute(
        select(func.count(Membership.id))
        .where(Membership.role == "member")
    ).scalar() or 0
    
    role_distribution = RoleDistribution(
        owners=owners,
        admins=admins,
        members=members
    )
    
    # Activity Metrics (last 7 days)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    new_users_7d = db.execute(
        select(func.count(User.id))
        .where(User.created_at >= seven_days_ago)
    ).scalar() or 0
    
    new_orgs_7d = db.execute(
        select(func.count(Organization.id))
        .where(Organization.created_at >= seven_days_ago)
    ).scalar() or 0
    
    invitations_7d = db.execute(
        select(func.count(Invitation.id))
        .where(Invitation.created_at >= seven_days_ago)
    ).scalar() or 0
    
    activity_metrics = ActivityMetrics(
        new_users_last_7_days=new_users_7d,
        new_orgs_last_7_days=new_orgs_7d,
        invitations_sent_last_7_days=invitations_7d
    )
    
    return DashboardAnalytics(
        user_growth=user_growth,
        organization_stats=organization_stats,
        invitation_metrics=invitation_metrics,
        role_distribution=role_distribution,
        activity_metrics=activity_metrics
    )

