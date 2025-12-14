"""
Pydantic schemas for analytics and statistics data.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class TimeSeriesDataPoint(BaseModel):
    """Single data point in a time series."""
    date: str
    count: int
    value: Optional[float] = None


class UserStats(BaseModel):
    """User statistics."""
    total_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    active_users_today: int
    active_users_this_week: int
    active_users_this_month: int


class ActivityStats(BaseModel):
    """Activity statistics."""
    total_activities: int
    activities_today: int
    activities_this_week: int
    activities_this_month: int
    activities_by_action: Dict[str, int]
    activities_by_resource_type: Dict[str, int]


class OrganizationStats(BaseModel):
    """Organization statistics."""
    total_organizations: int
    total_memberships: int
    average_members_per_org: float
    organizations_created_today: int
    organizations_created_this_week: int
    organizations_created_this_month: int


class ActivityTimeSeries(BaseModel):
    """Time series data for activities."""
    period: str  # "day", "week", "month"
    data: List[TimeSeriesDataPoint]


class DashboardStats(BaseModel):
    """Combined dashboard statistics."""
    user_stats: UserStats
    activity_stats: ActivityStats
    organization_stats: OrganizationStats
    activity_timeline: ActivityTimeSeries


class UserGrowthTimeSeries(BaseModel):
    """Time series data for user growth."""
    period: str
    data: List[TimeSeriesDataPoint]
