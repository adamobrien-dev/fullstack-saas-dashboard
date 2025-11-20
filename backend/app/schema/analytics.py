from pydantic import BaseModel
from typing import List
from datetime import datetime


class TimeSeriesDataPoint(BaseModel):
    date: str  # ISO format date string
    value: int


class UserGrowthMetrics(BaseModel):
    total_users: int
    growth_over_time: List[TimeSeriesDataPoint]


class OrganizationStats(BaseModel):
    total_organizations: int
    avg_members_per_org: float
    largest_org_size: int
    org_size_distribution: List[dict]  # [{"size": 1, "count": 5}, ...]


class InvitationMetrics(BaseModel):
    total_invitations: int
    pending: int
    accepted: int
    expired: int
    acceptance_rate: float


class RoleDistribution(BaseModel):
    owners: int
    admins: int
    members: int


class ActivityMetrics(BaseModel):
    new_users_last_7_days: int
    new_orgs_last_7_days: int
    invitations_sent_last_7_days: int


class DashboardAnalytics(BaseModel):
    user_growth: UserGrowthMetrics
    organization_stats: OrganizationStats
    invitation_metrics: InvitationMetrics
    role_distribution: RoleDistribution
    activity_metrics: ActivityMetrics

