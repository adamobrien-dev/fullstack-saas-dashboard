'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, orgApi, analyticsApi } from '@/lib/api';
import { User } from '@/types/user';
import { useOrg } from '@/contexts/OrgContext';
import ActivityFeed from '@/components/ActivityFeed';
import { DashboardStats } from '@/types/analytics';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [orgName, setOrgName] = useState('');
  const [creatingOrg, setCreatingOrg] = useState(false);
  const [orgError, setOrgError] = useState('');
  const [summaryStats, setSummaryStats] = useState<DashboardStats | null>(null);
  const { organizations, refreshOrgs } = useOrg();

  useEffect(() => {
    authApi
      .getCurrentUser()
      .then((data) => {
        setUser(data);
        // Load summary stats
        analyticsApi.getDashboard()
          .then((stats) => setSummaryStats(stats))
          .catch(() => {
            // Silently fail - analytics is optional
          });
      })
      .catch(() => {
        router.push('/login');
      })
      .finally(() => {
        setLoading(false);
      });
  }, [router]);

  const handleCreateOrg = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreatingOrg(true);
    setOrgError('');

    try {
      await orgApi.create(orgName);
      setOrgName('');
      await refreshOrgs();
    } catch (err: any) {
      setOrgError(err.response?.data?.detail || 'Failed to create organization');
    } finally {
      setCreatingOrg(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0 space-y-6">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">
                Welcome, {user.name}!
              </h1>
              <div className="mt-5 space-y-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h2 className="text-lg font-semibold text-gray-900 mb-2">
                    Your Account
                  </h2>
                  <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Email</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user.email}</dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Role</dt>
                      <dd className="mt-1 text-sm text-gray-900 capitalize">
                        {user.role}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm font-medium text-gray-500">User ID</dt>
                      <dd className="mt-1 text-sm text-gray-900">{user.id}</dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Summary Stats */}
          {summaryStats && (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0"></div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Users</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {summaryStats.user_stats.total_users}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0"></div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Total Activities</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {summaryStats.activity_stats.total_activities}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0"></div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Organizations</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {summaryStats.organization_stats.total_organizations}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0"></div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Active Today</dt>
                        <dd className="text-2xl font-semibold text-gray-900">
                          {summaryStats.user_stats.active_users_today}
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Analytics Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-2">
                    Analytics Dashboard
                  </h2>
                  <p className="text-sm text-gray-500">
                    View comprehensive metrics, charts, and insights about your platform usage.
                  </p>
                </div>
                <a
                  href="/analytics"
                  className="ml-4 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
                >
                  View Analytics
                </a>
              </div>
            </div>
          </div>

          {/* Activity Feed */}
          <ActivityFeed limit={10} />

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Organizations
              </h2>
              
              {organizations.length > 0 ? (
                <div className="space-y-2 mb-4">
                  {organizations.map((org) => (
                    <div
                      key={org.id}
                      className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                    >
                      <span className="text-gray-900 font-medium">{org.name}</span>
                      <a
                        href={`/orgs/${org.id}/members`}
                        className="text-indigo-600 hover:text-indigo-800 text-sm"
                      >
                        Manage Members
                      </a>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 mb-4">You don't belong to any organizations yet.</p>
              )}

              <div className="border-t border-gray-200 pt-4">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  Create New Organization
                </h3>
                <form onSubmit={handleCreateOrg} className="space-y-3">
                  {orgError && (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                      {orgError}
                    </div>
                  )}
                  <div>
                    <input
                      type="text"
                      value={orgName}
                      onChange={(e) => setOrgName(e.target.value)}
                      placeholder="Organization name"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={creatingOrg}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {creatingOrg ? 'Creating...' : 'Create Organization'}
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

