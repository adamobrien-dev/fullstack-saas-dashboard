'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi, orgApi } from '@/lib/api';
import { User } from '@/types/user';
import { useOrg } from '@/contexts/OrgContext';

export default function Navbar() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOrgDropdown, setShowOrgDropdown] = useState(false);
  const [pendingInviteCount, setPendingInviteCount] = useState(0);
  const { organizations, currentOrg, setCurrentOrg, loading: orgLoading } = useOrg();

  useEffect(() => {
    authApi
      .getCurrentUser()
      .then((data) => {
        setUser(data);
        // Load pending invitations count
        orgApi.listPendingInvitations()
          .then((invites) => setPendingInviteCount(invites.length))
          .catch(() => setPendingInviteCount(0));
      })
      .catch(() => {
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showOrgDropdown && !target.closest('.org-dropdown')) {
        setShowOrgDropdown(false);
      }
    };

    if (showOrgDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showOrgDropdown]);

  const handleLogout = async () => {
    try {
      await authApi.logout();
      setUser(null);
      router.push('/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-4">
            <a href="/" className="text-xl font-bold text-indigo-600">
              SaaS Dashboard
            </a>
            {user && currentOrg && (
              <div className="relative org-dropdown">
                <button
                  onClick={() => setShowOrgDropdown(!showOrgDropdown)}
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium border border-gray-300"
                >
                  {currentOrg.name} ▼
                </button>
                {showOrgDropdown && organizations.length > 0 && (
                  <div className="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200 org-dropdown">
                    <div className="py-1">
                      {organizations.map((org) => (
                        <button
                          key={org.id}
                          onClick={() => {
                            setCurrentOrg(org);
                            setShowOrgDropdown(false);
                          }}
                          className={`block w-full text-left px-4 py-2 text-sm ${
                            org.id === currentOrg.id
                              ? 'bg-indigo-50 text-indigo-700'
                              : 'text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          {org.name}
                        </button>
                      ))}
                      <a
                        href="/dashboard"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 border-t border-gray-200"
                      >
                        Create Organization
                      </a>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center space-x-4">
            {loading ? (
              <span className="text-gray-500">Loading...</span>
            ) : user ? (
              <>
                <a
                  href="/analytics"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Analytics
                </a>
                <a
                  href="/invitations"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium relative"
                >
                  Invitations
                  {pendingInviteCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {pendingInviteCount}
                    </span>
                  )}
                </a>
                {currentOrg && (
                  <a
                    href={`/orgs/${currentOrg.id}/members`}
                    className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Members
                  </a>
                )}
                <a
                  href="/profile"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Profile
                </a>
                <span className="text-gray-700">Welcome, {user.name}</span>
                <button
                  onClick={handleLogout}
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <a
                  href="/login"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Login
                </a>
                <a
                  href="/register"
                  className="bg-indigo-600 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                >
                  Register
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

