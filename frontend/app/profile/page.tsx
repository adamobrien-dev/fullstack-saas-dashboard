'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { User } from '@/types/user';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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
          setError('Failed to load profile');
        }
      })
      .finally(() => {
        setLoading(false);
      });
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  // Get avatar URL - if it's a relative path, prepend API URL
  const avatarUrl = user.avatar_url
    ? user.avatar_url.startsWith('http')
      ? user.avatar_url
      : `${API_URL}${user.avatar_url}`
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
                <a
                  href="/settings"
                  className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                >
                  Settings →
                </a>
              </div>

              <div className="flex flex-col sm:flex-row gap-6">
                {/* Avatar Section */}
                <div className="flex-shrink-0">
                  <div className="flex flex-col items-center">
                    <div className="relative">
                      {avatarUrl ? (
                        <img
                          src={avatarUrl}
                          alt={`${user.name}'s avatar`}
                          className="h-32 w-32 rounded-full object-cover border-4 border-gray-200"
                        />
                      ) : (
                        <div className="h-32 w-32 rounded-full bg-indigo-100 flex items-center justify-center border-4 border-gray-200">
                          <span className="text-4xl font-bold text-indigo-600">
                            {user.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                      )}
                    </div>
                    <h2 className="mt-4 text-xl font-semibold text-gray-900">
                      {user.name}
                    </h2>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                </div>

                {/* User Information Section */}
                <div className="flex-1">
                  <div className="bg-gray-50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Account Information
                    </h3>
                    <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Full Name</dt>
                        <dd className="mt-1 text-sm text-gray-900">{user.name}</dd>
                      </div>
                      <div>
                        <dt className="text-sm font-medium text-gray-500">Email Address</dt>
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

                  <div className="mt-6 flex gap-3">
                    <a
                      href="/profile/edit"
                      className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
                    >
                      Edit Profile
                    </a>
                    <a
                      href="/settings"
                      className="bg-white text-gray-700 px-4 py-2 rounded-md text-sm font-medium border border-gray-300 hover:bg-gray-50 transition-colors"
                    >
                      Account Settings
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

