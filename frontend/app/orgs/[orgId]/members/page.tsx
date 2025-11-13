'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { orgApi } from '@/lib/api';
import { useOrg } from '@/contexts/OrgContext';
import { Member } from '@/types/organization';

export default function MembersPage() {
  const params = useParams();
  const router = useRouter();
  const orgId = parseInt(params.orgId as string);
  const { currentOrg } = useOrg();
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<'member' | 'admin'>('member');
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteToken, setInviteToken] = useState<string | null>(null);

  useEffect(() => {
    if (orgId) {
      loadMembers();
    }
  }, [orgId]);

  const loadMembers = async () => {
    try {
      setLoading(true);
      const data = await orgApi.listMembers(orgId);
      setMembers(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteLoading(true);
    setError('');

    try {
      const invitation = await orgApi.invite(orgId, inviteEmail, inviteRole);
      setInviteToken(invitation.token);
      setInviteEmail('');
      setInviteRole('member');
      // Refresh members list
      await loadMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setInviteLoading(false);
    }
  };

  const handleUpdateRole = async (userId: number, newRole: string) => {
    try {
      await orgApi.updateMemberRole(orgId, userId, newRole);
      await loadMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update role');
    }
  };

  const handleRemoveMember = async (userId: number) => {
    if (!confirm('Are you sure you want to remove this member?')) {
      return;
    }

    try {
      await orgApi.removeMember(orgId, userId);
      await loadMembers();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to remove member');
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'bg-purple-100 text-purple-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading members...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">
                  Members - {currentOrg?.name}
                </h1>
                <button
                  onClick={() => setShowInviteModal(true)}
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                >
                  Invite Member
                </button>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              {inviteToken && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
                  <p className="font-semibold">Invitation created!</p>
                  <p className="text-sm mt-1">Token: <code className="bg-green-100 px-2 py-1 rounded">{inviteToken}</code></p>
                  <p className="text-sm mt-1">Share this token with the invitee to accept the invitation.</p>
                </div>
              )}

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Role
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {members.map((member) => (
                      <tr key={member.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {member.user_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {member.user_email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getRoleBadgeColor(
                              member.role
                            )}`}
                          >
                            {member.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          {member.role !== 'owner' && (
                            <>
                              <select
                                value={member.role}
                                onChange={(e) => handleUpdateRole(member.user_id, e.target.value)}
                                className="text-sm border border-gray-300 rounded px-2 py-1"
                              >
                                <option value="member">Member</option>
                                <option value="admin">Admin</option>
                                <option value="owner">Owner</option>
                              </select>
                              <button
                                onClick={() => handleRemoveMember(member.user_id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                Remove
                              </button>
                            </>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      {showInviteModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Invite Member</h3>
              <form onSubmit={handleInvite}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    required
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="user@example.com"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as 'member' | 'admin')}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="member">Member</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowInviteModal(false);
                      setInviteEmail('');
                      setInviteToken(null);
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={inviteLoading}
                    className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                  >
                    {inviteLoading ? 'Sending...' : 'Send Invite'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

