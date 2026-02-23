'use client';

import { useRouter } from 'next/navigation';
import { useCreateProject } from '@/hooks/useProjects';
import { ProjectWizard } from '@/components/projects/ProjectWizard';
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
    <div className="max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Create New Project</h1>
        <p className="text-gray-400">Configure your penetration testing project step by step</p>
      </div>

      <ProjectWizard
        onSubmit={handleSubmit}
        isLoading={createProject.isPending}
        error={(createProject.error as any)?.response?.data?.detail || (createProject.error as any)?.message}
      />
    </div>
  );
}
