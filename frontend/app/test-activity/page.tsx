'use client';

import { useState, useEffect } from 'react';
import { activityApi, orgApi } from '@/lib/api';
import { ActivityLogList } from '@/types/activity';

export default function TestActivityPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [organizations, setOrganizations] = useState<any[]>([]);

  useEffect(() => {
    // Load user's organizations on mount
    orgApi.listMine()
      .then((orgs) => setOrganizations(orgs))
      .catch(() => setOrganizations([]));
  }, []);

  const testGetLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await activityApi.getLogs({ page: 1, page_size: 10 });
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  const testGetMyLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await activityApi.getMyLogs(1, 10);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  const testGetOrgLogs = async (orgId?: number) => {
    setLoading(true);
    setError('');
    try {
      let id = orgId;
      if (!id) {
        const orgIdInput = prompt(`Enter organization ID:\n\nYour organizations:\n${organizations.map((o: any) => `  - ID: ${o.id}, Name: ${o.name}`).join('\n') || '  (none)'}`);
        if (!orgIdInput) {
          setLoading(false);
          return;
        }
        id = parseInt(orgIdInput);
      }
      const data = await activityApi.getOrgLogs(id!, { page: 1, page_size: 10 });
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  const testGetLog = async () => {
    setLoading(true);
    setError('');
    try {
      const logId = prompt('Enter log ID:');
      if (!logId) return;
      const data = await activityApi.getLog(parseInt(logId));
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Test Activity API</h1>

        {organizations.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h2 className="text-lg font-semibold mb-2">Your Organizations</h2>
            <ul className="list-disc list-inside">
              {organizations.map((org) => (
                <li key={org.id}>
                  ID: <strong>{org.id}</strong> - {org.name}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API Functions</h2>
          <div className="space-y-3">
            {organizations.length > 0 && (
              <div className="mb-4 p-3 bg-gray-50 rounded">
                <p className="text-sm font-semibold mb-2">Quick test with your organizations:</p>
                {organizations.map((org) => (
                  <button
                    key={org.id}
                    onClick={(e) => {
                      e.preventDefault();
                      testGetOrgLogs(org.id);
                    }}
                    disabled={loading}
                    className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 disabled:opacity-50 mr-2 mb-2"
                  >
                    Test Org {org.id} ({org.name})
                  </button>
                ))}
              </div>
            )}
            <button
              onClick={testGetLogs}
              disabled={loading}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 mr-2"
            >
              Test getLogs()
            </button>
            <button
              onClick={testGetMyLogs}
              disabled={loading}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 mr-2"
            >
              Test getMyLogs()
            </button>
            <button
              onClick={() => testGetOrgLogs()}
              disabled={loading}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 mr-2"
            >
              Test getOrgLogs()
            </button>
            <button
              onClick={testGetLog}
              disabled={loading}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
            >
              Test getLog()
            </button>
          </div>
        </div>

        {loading && (
          <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded mb-4">
            Loading...
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            Error: {error}
          </div>
        )}

        {result && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Response</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(result, null, 2)}
            </pre>
            {result.logs && (
              <div className="mt-4">
                <p className="font-semibold">Summary:</p>
                <ul className="list-disc list-inside mt-2">
                  <li>Total logs: {result.total}</li>
                  <li>Page: {result.page}</li>
                  <li>Page size: {result.page_size}</li>
                  <li>Logs on this page: {result.logs.length}</li>
                </ul>
                {result.logs.length > 0 && (
                  <div className="mt-4">
                    <p className="font-semibold mb-2">Sample log:</p>
                    <div className="bg-gray-50 p-3 rounded">
                      <p><strong>Action:</strong> {result.logs[0].action}</p>
                      <p><strong>User:</strong> {result.logs[0].user_name || result.logs[0].user_id || 'N/A'}</p>
                      <p><strong>Created:</strong> {new Date(result.logs[0].created_at).toLocaleString()}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

