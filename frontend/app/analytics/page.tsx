'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { analyticsApi } from '@/lib/api';
import { DashboardStats, UserStats, ActivityStats, OrganizationStats } from '@/types/analytics';

export default function AnalyticsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsApi.getDashboard();
      setStats(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to load analytics');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const StatCard = ({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) => (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0"></div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-semibold text-gray-900">{value}</div>
                {subtitle && (
                  <div className="ml-2 text-sm font-medium text-gray-500">{subtitle}</div>
                )}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="mt-2 text-sm text-gray-600">
              Comprehensive metrics and insights about your platform
            </p>
          </div>

          {/* User Statistics */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">User Statistics</h2>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="Total Users"
                value={stats.user_stats.total_users}
              />
              <StatCard
                title="New Users Today"
                value={stats.user_stats.new_users_today}
              />
              <StatCard
                title="New Users This Week"
                value={stats.user_stats.new_users_this_week}
              />
              <StatCard
                title="New Users This Month"
                value={stats.user_stats.new_users_this_month}
              />
            </div>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 mt-5">
              <StatCard
                title="Active Users Today"
                value={stats.user_stats.active_users_today}
              />
              <StatCard
                title="Active Users This Week"
                value={stats.user_stats.active_users_this_week}
              />
              <StatCard
                title="Active Users This Month"
                value={stats.user_stats.active_users_this_month}
              />
            </div>
          </div>

          {/* Activity Statistics */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Activity Statistics</h2>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="Total Activities"
                value={stats.activity_stats.total_activities}
              />
              <StatCard
                title="Activities Today"
                value={stats.activity_stats.activities_today}
              />
              <StatCard
                title="Activities This Week"
                value={stats.activity_stats.activities_this_week}
              />
              <StatCard
                title="Activities This Month"
                value={stats.activity_stats.activities_this_month}
              />
            </div>
          </div>

          {/* Organization Statistics */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Organization Statistics</h2>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="Total Organizations"
                value={stats.organization_stats.total_organizations}
              />
              <StatCard
                title="Total Memberships"
                value={stats.organization_stats.total_memberships}
              />
              <StatCard
                title="Avg Members per Org"
                value={stats.organization_stats.average_members_per_org.toFixed(2)}
              />
              <StatCard
                title="Orgs Created This Month"
                value={stats.organization_stats.organizations_created_this_month}
              />
            </div>
          </div>

          {/* Activity Breakdown */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Activity Breakdown</h2>
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              {/* Activities by Action */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">By Action Type</h3>
                  <div className="space-y-2">
                    {Object.entries(stats.activity_stats.activities_by_action)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 10)
                      .map(([action, count]) => (
                        <div key={action} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">{action}</span>
                          <span className="text-sm font-semibold text-gray-900">{count}</span>
                        </div>
                      ))}
                    {Object.keys(stats.activity_stats.activities_by_action).length === 0 && (
                      <p className="text-sm text-gray-500">No activity data available</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Activities by Resource Type */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">By Resource Type</h3>
                  <div className="space-y-2">
                    {Object.entries(stats.activity_stats.activities_by_resource_type)
                      .sort(([, a], [, b]) => b - a)
                      .slice(0, 10)
                      .map(([resourceType, count]) => (
                        <div key={resourceType} className="flex justify-between items-center">
                          <span className="text-sm text-gray-600">{resourceType}</span>
                          <span className="text-sm font-semibold text-gray-900">{count}</span>
                        </div>
                      ))}
                    {Object.keys(stats.activity_stats.activities_by_resource_type).length === 0 && (
                      <p className="text-sm text-gray-500">No activity data available</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Activity Timeline Info */}
          <div className="mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  Activity Timeline (Last 30 Days)
                </h3>
                <p className="text-sm text-gray-600">
                  {stats.activity_timeline.data.length} data points collected
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  Total activities in period: {stats.activity_timeline.data.reduce((sum, point) => sum + point.count, 0)}
                </p>
                <p className="text-sm text-gray-500 mt-4">
                  <em>Charts and visualizations coming in Day 12!</em>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
