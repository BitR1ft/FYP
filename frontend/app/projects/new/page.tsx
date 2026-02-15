'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { projectsApi } from '@/lib/api';

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target: '',
    enable_subdomain_enum: true,
    enable_port_scan: true,
    enable_web_crawl: true,
    enable_tech_detection: true,
    enable_vuln_scan: true,
    enable_nuclei: true,
    enable_auto_exploit: false,
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await projectsApi.create(formData);
      router.push('/projects');
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/auth/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to create project');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link href="/dashboard" className="text-2xl font-bold text-white hover:text-blue-400">
              AutoPenTest AI
            </Link>
            <Link
              href="/projects"
              className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              Back to Projects
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Create New Project</h1>
          <p className="text-gray-400">Configure your penetration testing project</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                  Project Name *
                </label>
                <input
                  id="name"
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="My Penetration Test"
                />
              </div>

              <div>
                <label htmlFor="target" className="block text-sm font-medium text-gray-300 mb-2">
                  Target *
                </label>
                <input
                  id="target"
                  type="text"
                  required
                  value={formData.target}
                  onChange={(e) => setFormData({ ...formData, target: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="example.com or 192.168.1.1"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Domain, IP address, or URL to test
                </p>
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  id="description"
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Optional project description..."
                />
              </div>
            </div>
          </div>

          {/* Reconnaissance Settings */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Reconnaissance</h2>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_subdomain_enum}
                  onChange={(e) => setFormData({ ...formData, enable_subdomain_enum: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-300">Enable subdomain enumeration</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_port_scan}
                  onChange={(e) => setFormData({ ...formData, enable_port_scan: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-300">Enable port scanning</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_web_crawl}
                  onChange={(e) => setFormData({ ...formData, enable_web_crawl: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-300">Enable web crawling</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_tech_detection}
                  onChange={(e) => setFormData({ ...formData, enable_tech_detection: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-300">Enable technology detection</span>
              </label>
            </div>
          </div>

          {/* Scanning Settings */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Vulnerability Scanning</h2>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_vuln_scan}
                  onChange={(e) => setFormData({ ...formData, enable_vuln_scan: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-300">Enable vulnerability scanning</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_nuclei}
                  onChange={(e) => setFormData({ ...formData, enable_nuclei: e.target.checked })}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-3 text-gray-300">Enable Nuclei scanner</span>
              </label>
            </div>
          </div>

          {/* Exploitation Settings */}
          <div className="bg-gray-800 border border-red-900 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-2">
              ⚠️ Exploitation (Advanced)
            </h2>
            <p className="text-yellow-500 text-sm mb-4">
              Only enable for authorized targets. Disabled by default for safety.
            </p>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.enable_auto_exploit}
                  onChange={(e) => setFormData({ ...formData, enable_auto_exploit: e.target.checked })}
                  className="w-4 h-4 text-red-600 rounded focus:ring-red-500"
                />
                <span className="ml-3 text-gray-300">Enable automated exploitation</span>
              </label>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-semibold py-3 px-6 rounded-lg transition-colors"
            >
              {isSubmitting ? 'Creating...' : 'Create Project'}
            </button>
            <Link
              href="/projects"
              className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors text-center"
            >
              Cancel
            </Link>
          </div>
        </form>
      </main>
    </div>
  );
}
