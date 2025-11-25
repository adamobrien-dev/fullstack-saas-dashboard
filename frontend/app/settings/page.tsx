'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { User } from '@/types/user';

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Password change form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);
  const [passwordErrors, setPasswordErrors] = useState<{
    current?: string;
    new?: string;
    confirm?: string;
  }>({});

  useEffect(() => {
    authApi
      .getCurrentUser()
      .then((data) => {
        setUser(data);
      })
      .catch((err) => {
        if (err.response?.status === 401) {
          router.push('/login');
        } else {
          setError('Failed to load settings');
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, [router]);

  const validatePasswordForm = () => {
    const errors: {
      current?: string;
      new?: string;
      confirm?: string;
    } = {};

    if (!currentPassword) {
      errors.current = 'Current password is required';
    }

    if (!newPassword) {
      errors.new = 'New password is required';
    } else if (newPassword.length < 8) {
      errors.new = 'Password must be at least 8 characters';
    }

    if (!confirmPassword) {
      errors.confirm = 'Please confirm your new password';
    } else if (newPassword !== confirmPassword) {
      errors.confirm = 'Passwords do not match';
    }

    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setPasswordErrors({});

    if (!validatePasswordForm()) {
      return;
    }

    setChangingPassword(true);

    try {
      await authApi.changePassword(currentPassword, newPassword);
      setSuccess('Password changed successfully!');
      // Clear form
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to change password';
      setError(errorMessage);
      
      // If it's a current password error, highlight that field
      if (errorMessage.toLowerCase().includes('current password')) {
        setPasswordErrors({ current: errorMessage });
      }
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Account Settings</h1>
                <a
                  href="/profile"
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  ← Back to Profile
                </a>
              </div>

              {success && (
                <div className="mb-4 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
                  {success}
                </div>
              )}

              {error && (
                <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              <div className="space-y-8">
                {/* Password Change Section */}
                <div className="border-b border-gray-200 pb-8">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h2>
                  <p className="text-sm text-gray-500 mb-6">
                    Update your password to keep your account secure. Your new password must be at least 8 characters long.
                  </p>
                  
                  <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
                    <div>
                      <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700">
                        Current Password
                      </label>
                      <input
                        type="password"
                        id="currentPassword"
                        name="currentPassword"
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                          passwordErrors.current ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                      {passwordErrors.current && (
                        <p className="mt-1 text-sm text-red-600">{passwordErrors.current}</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
                        New Password
                      </label>
                      <input
                        type="password"
                        id="newPassword"
                        name="newPassword"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                          passwordErrors.new ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                      {passwordErrors.new && (
                        <p className="mt-1 text-sm text-red-600">{passwordErrors.new}</p>
                      )}
                      <p className="mt-1 text-xs text-gray-500">Must be at least 8 characters</p>
                    </div>

                    <div>
                      <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm ${
                          passwordErrors.confirm ? 'border-red-300' : 'border-gray-300'
                        }`}
                      />
                      {passwordErrors.confirm && (
                        <p className="mt-1 text-sm text-red-600">{passwordErrors.confirm}</p>
                      )}
                    </div>

                    <div>
                      <button
                        type="submit"
                        disabled={changingPassword}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {changingPassword ? 'Changing Password...' : 'Change Password'}
                      </button>
                    </div>
                  </form>
                </div>

                {/* Account Information Section */}
                <div className="border-b border-gray-200 pb-8">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h2>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Email Address</dt>
                        <dd className="mt-1 text-sm text-gray-900">{user.email}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Role</dt>
                        <dd className="mt-1 text-sm text-gray-900 capitalize">{user.role}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">User ID</dt>
                        <dd className="mt-1 text-sm text-gray-900">{user.id}</dd>
                      </div>
                    </dl>
                  </div>
                  <div className="mt-4">
                    <a
                      href="/profile/edit"
                      className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    >
                      Edit Profile Information →
                    </a>
                  </div>
                </div>

                {/* Security Section */}
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">Security</h2>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600 mb-4">
                      For additional security, you can reset your password via email if you forget it.
                    </p>
                    <a
                      href="/forgot-password"
                      className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                    >
                      Reset Password via Email →
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

