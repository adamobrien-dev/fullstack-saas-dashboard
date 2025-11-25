'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { activityApi, orgApi } from '@/lib/api';
import { ActivityLog, ActivityLogList } from '@/types/activity';

function ActivityPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [organizations, setOrganizations] = useState<any[]>([]);

  // Filters
  const [filterAction, setFilterAction] = useState<string>('');
  const [filterResourceType, setFilterResourceType] = useState<string>('');
  const [filterOrgId, setFilterOrgId] = useState<number | null>(null);
  const [filterUserId, setFilterUserId] = useState<number | null>(null);

  useEffect(() => {
    // Load organizations for filter dropdown
    orgApi.listMine()
      .then((orgs) => setOrganizations(orgs))
      .catch(() => setOrganizations([]));

    // Load initial page from URL params
    const pageParam = searchParams.get('page');
    if (pageParam) {
      setPage(parseInt(pageParam));
    }
  }, [searchParams]);

  useEffect(() => {
    loadLogs();
  }, [page, pageSize, filterAction, filterResourceType, filterOrgId, filterUserId]);

  const loadLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const filters: any = {
        page,
        page_size: pageSize,
      };

      if (filterAction) filters.action = filterAction;
      if (filterResourceType) filters.resource_type = filterResourceType;
      if (filterOrgId) filters.organization_id = filterOrgId;
      if (filterUserId) filters.user_id = filterUserId;

      const data: ActivityLogList = await activityApi.getLogs(filters);
      setLogs(data.logs);
      setTotal(data.total);
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to load activity logs');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
    // Update URL without reload
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', newPage.toString());
    router.push(`/activity?${params.toString()}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleFilterChange = () => {
    setPage(1); // Reset to page 1 when filters change
    loadLogs();
  };

  const clearFilters = () => {
    setFilterAction('');
    setFilterResourceType('');
    setFilterOrgId(null);
    setFilterUserId(null);
    setPage(1);
  };

  const formatAction = (action: string): string => {
    const actionMap: Record<string, string> = {
      'user.login': 'Logged in',
      'user.logout': 'Logged out',
      'user.register': 'Registered',
      'user.profile.update': 'Updated profile',
      'user.password.change': 'Changed password',
      'user.password.reset': 'Reset password',
      'user.avatar.upload': 'Uploaded avatar',
      'organization.create': 'Created organization',
      'organization.update': 'Updated organization',
      'membership.create': 'Joined organization',
      'membership.update': 'Updated membership',
      'membership.delete': 'Left organization',
      'invitation.create': 'Created invitation',
      'invitation.accept': 'Accepted invitation',
    };
    return actionMap[action] || action.replace(/\./g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  };

  const formatTime = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const totalPages = Math.ceil(total / pageSize);

  if (loading && logs.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading activity logs...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">Activity Logs</h1>
            <p className="mt-2 text-sm text-gray-500">
              View and filter all activity logs you have access to
            </p>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Filters */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Action
                </label>
                <input
                  type="text"
                  value={filterAction}
                  onChange={(e) => setFilterAction(e.target.value)}
                  onBlur={handleFilterChange}
                  placeholder="e.g., user.login"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Resource Type
                </label>
                <select
                  value={filterResourceType}
                  onChange={(e) => {
                    setFilterResourceType(e.target.value);
                    handleFilterChange();
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">All</option>
                  <option value="user">User</option>
                  <option value="organization">Organization</option>
                  <option value="membership">Membership</option>
                  <option value="invitation">Invitation</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Organization
                </label>
                <select
                  value={filterOrgId || ''}
                  onChange={(e) => {
                    setFilterOrgId(e.target.value ? parseInt(e.target.value) : null);
                    handleFilterChange();
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">All</option>
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Page Size
                </label>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(parseInt(e.target.value));
                    setPage(1);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <button
                onClick={clearFilters}
                className="text-sm text-indigo-600 hover:text-indigo-800"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Results */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Results ({total} total)
                </h2>
              </div>

              {logs.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  No activity logs found
                </div>
              ) : (
                <>
                  <div className="space-y-4">
                    {logs.map((log) => (
                      <div
                        key={log.id}
                        className="border-b border-gray-200 pb-4 last:border-0"
                      >
                        <div className="flex items-start space-x-3">
                          <div className="flex-shrink-0">
                            <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                              <span className="text-indigo-600 text-sm font-semibold">
                                {log.user_name?.charAt(0).toUpperCase() || '?'}
                              </span>
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm font-medium text-gray-900">
                                  {log.user_name || `User ${log.user_id || 'Unknown'}`}
                                </p>
                                <p className="text-sm text-gray-600 mt-1">
                                  {formatAction(log.action)}
                                  {log.organization_name && (
                                    <> in <span className="font-medium">{log.organization_name}</span></>
                                  )}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                  {formatTime(log.created_at)}
                                </p>
                              </div>
                              <div className="text-right">
                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                  {log.action}
                                </span>
                              </div>
                            </div>
                            {log.details && Object.keys(log.details).length > 0 && (
                              <div className="mt-2 text-xs text-gray-400 bg-gray-50 p-2 rounded">
                                <pre className="whitespace-pre-wrap">
                                  {JSON.stringify(log.details, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Pagination */}
                  {totalPages > 1 && (
                    <div className="mt-6 flex items-center justify-between">
                      <div className="text-sm text-gray-500">
                        Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total} results
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handlePageChange(page - 1)}
                          disabled={page === 1}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Previous
                        </button>
                        <div className="flex space-x-1">
                          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            let pageNum;
                            if (totalPages <= 5) {
                              pageNum = i + 1;
                            } else if (page <= 3) {
                              pageNum = i + 1;
                            } else if (page >= totalPages - 2) {
                              pageNum = totalPages - 4 + i;
                            } else {
                              pageNum = page - 2 + i;
                            }
                            return (
                              <button
                                key={pageNum}
                                onClick={() => handlePageChange(pageNum)}
                                className={`px-3 py-2 border rounded-md text-sm font-medium ${
                                  page === pageNum
                                    ? 'bg-indigo-600 text-white border-indigo-600'
                                    : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                                }`}
                              >
                                {pageNum}
                              </button>
                            );
                          })}
                        </div>
                        <button
                          onClick={() => handlePageChange(page + 1)}
                          disabled={page === totalPages}
                          className="px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ActivityPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    }>
      <ActivityPageContent />
    </Suspense>
  );
}

