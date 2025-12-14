/**
 * TypeScript interfaces for analytics data.
 */

export interface TimeSeriesDataPoint {
  date: string;
  count: number;
  value?: number;
}

export interface UserStats {
  total_users: number;
  new_users_today: number;
  new_users_this_week: number;
  new_users_this_month: number;
  active_users_today: number;
  active_users_this_week: number;
  active_users_this_month: number;
}

export interface ActivityStats {
  total_activities: number;
  activities_today: number;
  activities_this_week: number;
  activities_this_month: number;
  activities_by_action: Record<string, number>;
  activities_by_resource_type: Record<string, number>;
}

export interface OrganizationStats {
  total_organizations: number;
  total_memberships: number;
  average_members_per_org: number;
  organizations_created_today: number;
  organizations_created_this_week: number;
  organizations_created_this_month: number;
}

export interface ActivityTimeSeries {
  period: string;
  data: TimeSeriesDataPoint[];
}

export interface UserGrowthTimeSeries {
  period: string;
  data: TimeSeriesDataPoint[];
}

export interface DashboardStats {
  user_stats: UserStats;
  activity_stats: ActivityStats;
  organization_stats: OrganizationStats;
  activity_timeline: ActivityTimeSeries;
}

