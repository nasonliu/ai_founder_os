/**
 * AI Founder OS - ProjectCard Component
 * 
 * Project information card with progress, tasks, and quick actions.
 */

import { useState } from 'react';
import { 
  FolderKanban, 
  MoreHorizontal, 
  Play, 
  Pause, 
  CheckCircle2, 
  Clock,
  Users,
  ListTodo,
  ChevronRight,
  AlertTriangle,
  ArrowUpRight,
  Calendar,
  Target
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface ProjectCardProps {
  project: {
    id: string;
    name: string;
    status: 'active' | 'paused' | 'completed' | 'archived';
    progress: number;
    taskCount: number;
    completedTasks: number;
    description?: string;
    owner?: string;
    createdAt?: string;
    deadline?: string;
    priority?: 'low' | 'medium' | 'high' | 'critical';
    tags?: string[];
  };
  onClick?: () => void;
  onAction?: (action: 'pause' | 'resume' | 'archive' | 'view') => void;
  className?: string;
}

// Status configuration
const STATUS_CONFIG = {
  active: { 
    label: 'Active', 
    color: 'bg-green-100 text-green-700',
    icon: Play 
  },
  paused: { 
    label: 'Paused', 
    color: 'bg-yellow-100 text-yellow-700',
    icon: Pause 
  },
  completed: { 
    label: 'Completed', 
    color: 'bg-blue-100 text-blue-700',
    icon: CheckCircle2 
  },
  archived: { 
    label: 'Archived', 
    color: 'bg-slate-100 text-slate-700',
    icon: FolderKanban 
  },
};

// Priority configuration
const PRIORITY_CONFIG = {
  low: { label: 'Low', color: 'text-slate-500' },
  medium: { label: 'Medium', color: 'text-blue-600' },
  high: { label: 'High', color: 'text-orange-600' },
  critical: { label: 'Critical', color: 'text-red-600' },
};

interface ProgressBarProps {
  progress: number;
  status?: ProjectCardProps['project']['status'];
  className?: string;
}

function ProgressBar({ progress, status = 'active', className }: ProgressBarProps) {
  // Color based on progress and status
  const getColor = () => {
    if (status === 'completed') return 'bg-blue-500';
    if (status === 'paused') return 'bg-yellow-500';
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 25) return 'bg-yellow-500';
    return 'bg-slate-300';
  };

  return (
    <div className={cn("h-2 w-full overflow-hidden rounded-full bg-slate-100", className)}>
      <div
        className={cn("h-full transition-all duration-500", getColor())}
        style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
      />
    </div>
  );
}

interface ProjectStatsProps {
  taskCount: number;
  completedTasks: number;
}

function ProjectStats({ taskCount, completedTasks }: ProjectStatsProps) {
  const pending = taskCount - completedTasks;
  
  return (
    <div className="flex items-center gap-4 text-xs text-slate-500">
      <div className="flex items-center gap-1">
        <ListTodo size={14} />
        <span>{taskCount} tasks</span>
      </div>
      <div className="flex items-center gap-1">
        <CheckCircle2 size={14} className="text-green-500" />
        <span>{completedTasks} done</span>
      </div>
      <div className="flex items-center gap-1">
        <Clock size={14} className="text-slate-400" />
        <span>{pending} pending</span>
      </div>
    </div>
  );
}

export function ProjectCard({ 
  project, 
  onClick, 
  onAction,
  className 
}: ProjectCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const statusConfig = STATUS_CONFIG[project.status];
  const StatusIcon = statusConfig?.icon || FolderKanban;
  const priority = project.priority ? PRIORITY_CONFIG[project.priority] : null;

  // Handle menu click
  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setMenuOpen(!menuOpen);
  };

  // Handle action
  const handleAction = (action: ProjectCardProps['project']) => {
    onAction?.(action);
    setMenuOpen(false);
  };

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setMenuOpen(false);
      }}
      className={cn(
        "group relative cursor-pointer rounded-xl border border-slate-200 bg-white transition-all hover:shadow-lg",
        isHovered && "border-blue-200",
        className
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between p-4">
        <div className="flex items-start gap-3">
          <div className={cn(
            "flex h-10 w-10 items-center justify-center rounded-lg",
            project.status === 'active' && "bg-green-100",
            project.status === 'paused' && "bg-yellow-100",
            project.status === 'completed' && "bg-blue-100",
            project.status === 'archived' && "bg-slate-100"
          )}>
            <FolderKanban 
              size={20} 
              className={cn(
                project.status === 'active' && "text-green-600",
                project.status === 'paused' && "text-yellow-600",
                project.status === 'completed' && "text-blue-600",
                project.status === 'archived' && "text-slate-600"
              )} 
            />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">
              {project.name}
            </h3>
            <p className="mt-0.5 text-xs text-slate-500 line-clamp-1">
              {project.description || `Project ${project.id}`}
            </p>
          </div>
        </div>

        {/* Menu */}
        <div className="relative">
          <button
            onClick={handleMenuClick}
            className={cn(
              "rounded-lg p-1.5 transition-colors",
              menuOpen ? "bg-slate-100" : "opacity-0 group-hover:opacity-100 hover:bg-slate-100"
            )}
          >
            <MoreHorizontal size={16} className="text-slate-500" />
          </button>

          {/* Dropdown Menu */}
          {menuOpen && (
            <div className="absolute right-0 top-full z-10 mt-1 w-36 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
              {project.status === 'active' && (
                <button
                  onClick={() => handleAction('pause')}
                  className="flex w-full items-center gap-2 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50"
                >
                  <Pause size={14} />
                  Pause
                </button>
              )}
              {project.status === 'paused' && (
                <button
                  onClick={() => handleAction('resume')}
                  className="flex w-full items-center gap-2 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50"
                >
                  <Play size={14} />
                  Resume
                </button>
              )}
              {project.status !== 'archived' && (
                <button
                  onClick={() => handleAction('archive')}
                  className="flex w-full items-center gap-2 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50"
                >
                  <FolderKanban size={14} />
                  Archive
                </button>
              )}
              <button
                onClick={() => handleAction('view')}
                className="flex w-full items-center gap-2 px-3 py-2 text-xs text-slate-700 hover:bg-slate-50"
              >
                <ArrowUpRight size={14} />
                View Details
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Status & Priority */}
      <div className="flex items-center gap-2 px-4">
        <span className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium", statusConfig?.color)}>
          <StatusIcon size={12} />
          {statusConfig?.label}
        </span>
        {priority && (
          <span className={cn("text-xs font-medium", priority.color)}>
            {priority.label} Priority
          </span        )}
        {project.tags?.slice(0, 2).map((tag) => (
          <span 
            key={tag} 
            className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Progress */}
      <div className="mt-4 px-4">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500">Progress</span>
          <span className="font-medium text-slate-700">{project.progress}%</span>
        </div>
        <ProgressBar 
          progress={project.progress} 
          status={project.status}
          className="mt-1.5" 
        />
      </div>

      {/* Stats */}
      <div className="mt-4 border-t border-slate-100 px-4 py-3">
        <ProjectStats 
          taskCount={project.taskCount} 
          completedTasks={project.completedTasks} 
        />
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-slate-100 bg-slate-50 px-4 py-2.5">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          {project.owner && (
            <div className="flex items-center gap-1">
              <Users size={12} />
              <span>{project.owner}</span>
            </div>
          )}
          {project.deadline && (
            <div className="flex items-center gap-1">
              <Calendar size={12} />
              <span>{project.deadline}</span>
            </div>
          )}
        </div>
        <ChevronRight 
          size={16} 
          className={cn(
            "text-slate-400 transition-transform",
            isHovered && "translate-x-1 text-blue-500"
          )} 
        />
      </div>
    </div>
  );
}

// Compact version for lists
interface ProjectCardCompactProps {
  project: ProjectCardProps['project'];
  onClick?: () => void;
}

export function ProjectCardCompact({ project, onClick }: ProjectCardCompactProps) {
  const statusConfig = STATUS_CONFIG[project.status];
  
  return (
    <div
      onClick={onClick}
      className="flex cursor-pointer items-center justify-between rounded-lg border border-slate-200 bg-white p-3 transition-colors hover:bg-slate-50"
    >
      <div className="flex items-center gap-3">
        <div className={cn(
          "flex h-8 w-8 items-center justify-center rounded",
          project.status === 'active' && "bg-green-100",
          project.status === 'paused' && "bg-yellow-100",
          project.status === 'completed' && "bg-blue-100",
          project.status === 'archived' && "bg-slate-100"
        )}>
          <FolderKanban 
            size={16} 
            className={cn(
              project.status === 'active' && "text-green-600",
              project.status === 'paused' && "text-yellow-600",
              project.status === 'completed' && "text-blue-600",
              project.status === 'archived' && "text-slate-600"
            )} 
          />
        </div>
        <div>
          <p className="text-sm font-medium text-slate-900">{project.name}</p>
          <p className="text-xs text-slate-500">
            {project.completedTasks}/{project.taskCount} tasks
          </p>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <ProgressBar progress={project.progress} className="w-16" />
        <span className={cn("rounded-full px-2 py-0.5 text-xs font-medium", statusConfig?.color)}>
          {statusConfig?.label}
        </span>
      </div>
    </div>
  );
}

export { ProjectCard };
export type { ProjectCardProps };
