'use client';

import Link from 'next/link';
import type { Project } from '@/lib/api';
import { Calendar, Target, Trash2, Eye } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
  onDelete: (id: string) => void;
  isDeleting?: boolean;
}

const STATUS_CONFIG: Record<string, { color: string; dot: string }> = {
  draft:     { color: 'bg-gray-500/20 text-gray-400 border-gray-600',    dot: 'bg-gray-500' },
  queued:    { color: 'bg-yellow-500/20 text-yellow-400 border-yellow-700', dot: 'bg-yellow-500' },
  running:   { color: 'bg-blue-500/20 text-blue-400 border-blue-700',    dot: 'bg-blue-500 animate-pulse' },
  completed: { color: 'bg-green-500/20 text-green-400 border-green-700', dot: 'bg-green-500' },
  failed:    { color: 'bg-red-500/20 text-red-400 border-red-700',       dot: 'bg-red-500' },
  paused:    { color: 'bg-orange-500/20 text-orange-400 border-orange-700', dot: 'bg-orange-500' },
};

export function ProjectCard({ project, onDelete, isDeleting }: ProjectCardProps) {
  const statusCfg = STATUS_CONFIG[project.status] ?? STATUS_CONFIG.draft;
  const enabledModules = [
    project.enable_subdomain_enum && 'Subdomains',
    project.enable_port_scan && 'Ports',
    project.enable_web_crawl && 'Crawl',
    project.enable_tech_detection && 'Tech',
    project.enable_vuln_scan && 'Vulns',
    project.enable_nuclei && 'Nuclei',
    project.enable_auto_exploit && 'Exploit',
  ].filter(Boolean) as string[];

  return (
    <article
      className="bg-gray-800 border border-gray-700 rounded-lg p-5 hover:border-gray-600 transition-colors"
      aria-label={`Project: ${project.name}`}
    >
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1 min-w-0">
          {/* Header row */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-white truncate">{project.name}</h3>
            <span
              className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border ${statusCfg.color}`}
              aria-label={`Status: ${project.status}`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${statusCfg.dot}`} aria-hidden="true" />
              {project.status.toUpperCase()}
            </span>
          </div>

          {/* Target */}
          <div className="flex items-center gap-1.5 text-sm mb-1">
            <Target className="w-3.5 h-3.5 text-gray-500 flex-shrink-0" aria-hidden="true" />
            <span className="text-blue-400 truncate">{project.target}</span>
          </div>

          {/* Description */}
          {project.description && (
            <p className="text-gray-500 text-sm mt-1 line-clamp-2">{project.description}</p>
          )}

          {/* Modules chips */}
          {enabledModules.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3" aria-label="Enabled modules">
              {enabledModules.map((mod) => (
                <span
                  key={mod}
                  className="px-2 py-0.5 bg-gray-700 text-gray-300 rounded text-xs"
                >
                  {mod}
                </span>
              ))}
            </div>
          )}

          {/* Date */}
          <div className="flex items-center gap-1.5 mt-3 text-xs text-gray-600">
            <Calendar className="w-3 h-3" aria-hidden="true" />
            <time dateTime={project.created_at}>
              {new Date(project.created_at).toLocaleDateString()}
            </time>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 flex-shrink-0">
          <Link
            href={`/projects/${project.id}`}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
            aria-label={`View project ${project.name}`}
          >
            <Eye className="w-3.5 h-3.5" aria-hidden="true" />
            View
          </Link>
          <button
            onClick={() => onDelete(project.id)}
            disabled={isDeleting}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-red-600/80 hover:bg-red-700 disabled:opacity-50 text-white rounded-lg transition-colors text-sm"
            aria-label={`Delete project ${project.name}`}
          >
            <Trash2 className="w-3.5 h-3.5" aria-hidden="true" />
            Delete
          </button>
        </div>
      </div>
    </article>
  );
}
