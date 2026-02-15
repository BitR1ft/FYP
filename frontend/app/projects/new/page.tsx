'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useCreateProject } from '@/hooks/useProjects';
import { ProjectForm } from '@/components/forms/ProjectForm';
import type { ProjectFormData } from '@/lib/validations';

export default function NewProjectPage() {
  const router = useRouter();
  const createProject = useCreateProject();

  const handleSubmit = async (data: ProjectFormData) => {
    try {
      await createProject.mutateAsync(data);
      router.push('/projects');
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/auth/login');
      }
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

        <ProjectForm
          onSubmit={handleSubmit}
          isLoading={createProject.isPending}
          error={(createProject.error as any)?.response?.data?.detail || createProject.error?.message}
        />
      </main>
    </div>
  );
}
