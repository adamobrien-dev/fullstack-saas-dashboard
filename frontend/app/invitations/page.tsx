'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { orgApi } from '@/lib/api';
import { useOrg } from '@/contexts/OrgContext';
import { Invitation } from '@/types/organization';

export default function InvitationsPage() {
  const router = useRouter();
  const { refreshOrgs } = useOrg();
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [accepting, setAccepting] = useState<string | null>(null);

  useEffect(() => {
    loadInvitations();
  }, []);

  const loadInvitations = async () => {
    try {
      setLoading(true);
      const data = await orgApi.listPendingInvitations();
      setInvitations(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load invitations');
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (token: string) => {
    setAccepting(token);
    setError('');

    try {
      await orgApi.acceptInvite(token);
      await refreshOrgs();
      await loadInvitations(); // Refresh list
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to accept invitation');
    } finally {
      setAccepting(null);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading invitations...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h1 className="text-2xl font-bold text-gray-900 mb-6">
                Pending Invitations
              </h1>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              {invitations.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">You have no pending invitations.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {invitations.map((invitation) => (
                    <div
                      key={invitation.id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {invitation.email}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            Invited to join as <span className="font-medium capitalize">{invitation.role}</span>
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Expires: {formatDate(invitation.expires_at)}
                          </p>
                        </div>
                        <button
                          onClick={() => handleAccept(invitation.token)}
                          disabled={accepting === invitation.token}
                          className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
                        >
                          {accepting === invitation.token ? 'Accepting...' : 'Accept'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

