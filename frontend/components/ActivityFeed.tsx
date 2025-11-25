'use client';

import { useState, useEffect } from 'react';
import { activityApi } from '@/lib/api';
import { ActivityLog } from '@/types/activity';

interface ActivityFeedProps {
  limit?: number;
  showHeader?: boolean;
}

export default function ActivityFeed({ limit = 10, showHeader = true }: ActivityFeedProps) {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadActivityLogs();
  }, [limit]);

  const loadActivityLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await activityApi.getLogs({ page: 1, page_size: limit });
      setLogs(data.logs);
    } catch (err: any) {
      if (err.response?.status !== 401) {
        setError('Failed to load activity logs');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatAction = (action: string): string => {
    // Convert action strings to readable format
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
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          {showHeader && <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>}
          <div className="text-gray-500 text-sm">Loading activity...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          {showHeader && <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>}
          <div className="text-red-500 text-sm">{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        {showHeader && (
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
            <a
              href="/activity"
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
            >
              View All →
            </a>
          </div>
        )}

        {logs.length === 0 ? (
          <div className="text-gray-500 text-sm py-4">No recent activity</div>
        ) : (
          <div className="space-y-3">
            {logs.map((log) => (
              <div key={log.id} className="flex items-start space-x-3 pb-3 border-b border-gray-100 last:border-0">
                <div className="flex-shrink-0">
                  <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center">
                    <span className="text-indigo-600 text-xs font-semibold">
                      {log.user_name?.charAt(0).toUpperCase() || '?'}
                    </span>
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-900">
                    <span className="font-medium">{log.user_name || 'Unknown user'}</span>
                    {' '}
                    <span>{formatAction(log.action)}</span>
                    {log.organization_name && (
                      <>
                        {' '}in{' '}
                        <span className="font-medium">{log.organization_name}</span>
                      </>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {formatTime(log.created_at)}
                  </div>
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="text-xs text-gray-400 mt-1">
                      {JSON.stringify(log.details)}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

