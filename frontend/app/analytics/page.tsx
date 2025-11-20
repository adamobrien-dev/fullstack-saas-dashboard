'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { authApi, analyticsApi } from '@/lib/api';

interface DashboardAnalytics {
  user_growth: {
    total_users: number;
    growth_over_time: Array<{ date: string; value: number }>;
  };
  organization_stats: {
    total_organizations: number;
    avg_members_per_org: number;
    largest_org_size: number;
    org_size_distribution: Array<{ size: string; count: number }>;
  };
  invitation_metrics: {
    total_invitations: number;
    pending: number;
    accepted: number;
    expired: number;
    acceptance_rate: number;
  };
  role_distribution: {
    owners: number;
    admins: number;
    members: number;
  };
  activity_metrics: {
    new_users_last_7_days: number;
    new_orgs_last_7_days: number;
    invitations_sent_last_7_days: number;
  };
}

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

export default function AnalyticsPage() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check authentication
    authApi
      .getCurrentUser()
      .catch(() => {
        router.push('/login');
      });

    // Load analytics
    analyticsApi
      .getDashboard()
      .then((data) => {
        setAnalytics(data);
      })
      .catch((err: any) => {
        setError(err.response?.data?.detail || 'Failed to load analytics');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  if (!analytics) {
    return null;
  }

  // Format dates for display (show month/day)
  const formattedGrowthData = analytics.user_growth.growth_over_time.map((item) => ({
    ...item,
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
  }));

  // Role distribution data for pie chart
  const roleData = [
    { name: 'Owners', value: analytics.role_distribution.owners },
    { name: 'Admins', value: analytics.role_distribution.admins },
    { name: 'Members', value: analytics.role_distribution.members },
  ].filter((item) => item.value > 0);

  // Invitation status data
  const invitationData = [
    { name: 'Accepted', value: analytics.invitation_metrics.accepted },
    { name: 'Pending', value: analytics.invitation_metrics.pending },
    { name: 'Expired', value: analytics.invitation_metrics.expired },
  ].filter((item) => item.value > 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Analytics Dashboard</h1>

          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl font-bold text-indigo-600">
                      {analytics.user_growth.total_users}
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                      <dd className="text-xs text-gray-400">
                        {analytics.activity_metrics.new_users_last_7_days} new this week
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl font-bold text-green-600">
                      {analytics.organization_stats.total_organizations}
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Organizations
                      </dt>
                      <dd className="text-xs text-gray-400">
                        {analytics.activity_metrics.new_orgs_last_7_days} new this week
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl font-bold text-purple-600">
                      {analytics.invitation_metrics.total_invitations}
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Invitations</dt>
                      <dd className="text-xs text-gray-400">
                        {analytics.invitation_metrics.acceptance_rate}% acceptance rate
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl font-bold text-orange-600">
                      {analytics.organization_stats.avg_members_per_org.toFixed(1)}
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Avg Members/Org
                      </dt>
                      <dd className="text-xs text-gray-400">
                        Largest: {analytics.organization_stats.largest_org_size} members
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* User Growth Chart */}
            <div className="bg-white p-6 shadow rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">User Growth (30 Days)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={formattedGrowthData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    interval="preserveStartEnd"
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#4F46E5"
                    strokeWidth={2}
                    name="New Users"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Role Distribution Chart */}
            <div className="bg-white p-6 shadow rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Role Distribution</h2>
              {roleData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={roleData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {roleData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-400">
                  No data available
                </div>
              )}
            </div>

            {/* Organization Size Distribution */}
            <div className="bg-white p-6 shadow rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Organization Size Distribution
              </h2>
              {analytics.organization_stats.org_size_distribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={analytics.organization_stats.org_size_distribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="size" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#10B981" name="Organizations" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-400">
                  No data available
                </div>
              )}
            </div>

            {/* Invitation Status */}
            <div className="bg-white p-6 shadow rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Invitation Status</h2>
              {invitationData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={invitationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {invitationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-[300px] text-gray-400">
                  No invitations yet
                </div>
              )}
            </div>
          </div>

          {/* Activity Metrics */}
          <div className="bg-white p-6 shadow rounded-lg">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity (Last 7 Days)</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-indigo-50 rounded-lg">
                <div className="text-3xl font-bold text-indigo-600">
                  {analytics.activity_metrics.new_users_last_7_days}
                </div>
                <div className="text-sm text-gray-600 mt-1">New Users</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-3xl font-bold text-green-600">
                  {analytics.activity_metrics.new_orgs_last_7_days}
                </div>
                <div className="text-sm text-gray-600 mt-1">New Organizations</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-3xl font-bold text-purple-600">
                  {analytics.activity_metrics.invitations_sent_last_7_days}
                </div>
                <div className="text-sm text-gray-600 mt-1">Invitations Sent</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

