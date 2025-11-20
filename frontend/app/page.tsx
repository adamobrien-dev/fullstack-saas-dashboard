'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in, redirect to dashboard if so
    authApi
      .getCurrentUser()
      .then(() => {
        router.push('/dashboard');
      })
      .catch(() => {
        // Not logged in, stay on landing page
      });
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Full-Stack SaaS Dashboard
          </h1>
          <p className="mt-4 text-xl text-gray-600">
            Build powerful dashboards with authentication and real-time data
          </p>
          <div className="mt-10 flex justify-center space-x-4">
            <Link
              href="/login"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="inline-flex items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
