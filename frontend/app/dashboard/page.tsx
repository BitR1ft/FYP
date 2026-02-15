'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await authApi.getCurrentUser();
        setUser(response.data);
      } catch (error) {
        // Not authenticated, redirect to login
        router.push('/auth/login');
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">
              AutoPenTest AI
            </h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-300">
                {user?.full_name || user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            Welcome back, {user?.username}! 👋
          </h2>
          <p className="text-gray-400">
            Your penetration testing command center
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="text-3xl mb-2">📊</div>
            <h3 className="text-lg font-semibold text-white mb-1">Projects</h3>
            <p className="text-3xl font-bold text-blue-500">0</p>
            <p className="text-sm text-gray-400 mt-2">Total projects</p>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="text-3xl mb-2">🎯</div>
            <h3 className="text-lg font-semibold text-white mb-1">Active Scans</h3>
            <p className="text-3xl font-bold text-green-500">0</p>
            <p className="text-sm text-gray-400 mt-2">Currently running</p>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <div className="text-3xl mb-2">🔍</div>
            <h3 className="text-lg font-semibold text-white mb-1">Findings</h3>
            <p className="text-3xl font-bold text-yellow-500">0</p>
            <p className="text-sm text-gray-400 mt-2">Total vulnerabilities</p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link href="/projects/new" className="flex items-center gap-3 p-4 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-left">
              <span className="text-2xl">➕</span>
              <div>
                <div className="font-semibold text-white">New Project</div>
                <div className="text-sm text-blue-100">Start a new penetration test</div>
              </div>
            </Link>

            <Link href="/projects" className="flex items-center gap-3 p-4 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-left">
              <span className="text-2xl">📋</span>
              <div>
                <div className="font-semibold text-white">View Projects</div>
                <div className="text-sm text-gray-300">See all your projects</div>
              </div>
            </Link>
          </div>
        </div>

        {/* Empty State */}
        <div className="mt-8 bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">🚀</div>
          <h3 className="text-2xl font-semibold text-white mb-2">
            Ready to Get Started?
          </h3>
          <p className="text-gray-400 mb-6 max-w-2xl mx-auto">
            Create your first penetration testing project and let our AI-powered framework
            autonomously discover vulnerabilities and generate professional reports.
          </p>
          <Link
            href="/projects/new"
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
          >
            Create Your First Project
          </Link>
        </div>
      </main>
    </div>
  );
}
