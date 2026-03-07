/**
 * AI Founder OS - TaskBoard Component
 * 
 * Kanban-style task board with columns for different task states.
 */

import { useState } from 'react';
import { 
  MoreHorizontal, 
  Plus, 
  Clock, 
  User,
  AlertCircle,
  CheckCircle2,
  Circle,
  XCircle,
  Ban
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface TaskBoardTask {
  id: string;
  title: string;
  status: 'pending' | 'queued' | 'running' | 'verifying' | 'completed' | 'failed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | 'critical';
  assignee?: string;
  projectId: string;
  projectName?: string;
  goal?: string;
  createdAt?: string;
  updatedAt?: string;
}

interface TaskBoardProps {
  tasks: TaskBoardTask[];
  onTaskClick?: (task: TaskBoardTask) => void;
  onStatusChange?: (taskId: string, newStatus: TaskBoardTask['status']) => void;
  className?: string;
}

// Column configuration
const COLUMNS: { id: TaskBoardTask['status']; label: string; color: string }[] = [
  { id: 'pending', label: 'Pending', color: 'bg-slate-100' },
  { id: 'queued', label: 'Queued', color: 'bg-blue-50' },
  { id: 'running', label: 'Running', color: 'bg-yellow-50' },
  { id: 'verifying', label: 'Verifying', color: 'bg-purple-50' },
  { id: 'completed', label: 'Completed', color: 'bg-green-50' },
  { id: 'failed', label: 'Failed', color: 'bg-red-50' },
  { id: 'blocked', label: 'Blocked', color: 'bg-orange-50' },
];

// Priority configuration
const PRIORITY_CONFIG = {
  low: { label: 'Low', color: 'text-slate-500', bg: 'bg-slate-100' },
  medium: { label: 'Medium', color: 'text-blue-600', bg: 'bg-blue-100' },
  high: { label: 'High', color: 'text-orange-600', bg: 'bg-orange-100' },
  critical: { label: 'Critical', color: 'text-red-600', bg: 'bg-red-100' },
};

// Status icon mapping
const STATUS_ICONS = {
  pending: Circle,
  queued: Clock,
  running: Clock,
  verifying: Clock,
  completed: CheckCircle2,
  failed: XCircle,
  blocked: Ban,
};

interface TaskCardProps {
  task: TaskBoardTask;
  onClick?: () => void;
}

function TaskCard({ task, onClick }: TaskCardProps) {
  const StatusIcon = STATUS_ICONS[task.status];
  const priority = PRIORITY_CONFIG[task.priority];

  return (
    <div
      onClick={onClick}
      className="group cursor-pointer rounded-lg border border-slate-200 bg-white p-3 shadow-sm transition-all hover:shadow-md"
    >
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <StatusIcon 
            size={16} 
            className={cn(
              "flex-shrink-0",
              task.status === 'completed' && "text-green-500",
              task.status === 'failed' && "text-red-500",
              task.status === 'running' && "text-yellow-500",
              task.status === 'blocked' && "text-orange-500",
              task.status === 'pending' && "text-slate-400",
              task.status === 'queued' && "text-blue-400",
              task.status === 'verifying' && "text-purple-400"
            )} 
          />
          <span className={cn("text-xs font-medium", priority.color, priority.bg, "rounded px-1.5 py-0.5")}>
            {priority.label}
          </span>
        </div>
        <button 
          onClick={(e) => e.stopPropagation()}
          className="opacity-0 group-hover:opacity-100 rounded p-1 hover:bg-slate-100"
        >
          <MoreHorizontal size={14} className="text-slate-400" />
        </button>
      </div>

      {/* Title */}
      <h4 className="mt-2 text-sm font-medium text-slate-900 line-clamp-2">
        {task.title}
      </h4>

      {/* Project */}
      {task.projectName && (
        <p className="mt-1 text-xs text-slate-500">
          {task.projectName}
        </p>
      )}

      {/* Footer */}
      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-slate-400 font-mono">
          {task.id}
        </span>
        {task.assignee && (
          <div className="flex items-center gap-1 text-xs text-slate-500">
            <User size={12} />
            <span className="truncate max-w-[80px]">{task.assignee}</span>
          </div>
        )}
      </div>
    </div>
  );
}

interface ColumnProps {
  id: TaskBoardTask['status'];
  label: string;
  color: string;
  tasks: TaskBoardTask[];
  onTaskClick?: (task: TaskBoardTask) => void;
}

function Column({ id, label, color, tasks, onTaskClick }: ColumnProps) {
  const taskCount = tasks.length;
  
  // Get accent color based on column
  const accentColors: Record<string, string> = {
    pending: 'border-slate-300',
    queued: 'border-blue-400',
    running: 'border-yellow-400',
    verifying: 'border-purple-400',
    completed: 'border-green-400',
    failed: 'border-red-400',
    blocked: 'border-orange-400',
  };

  return (
    <div className="flex flex-col min-w-[280px] max-w-[320px]">
      {/* Column Header */}
      <div className={cn("flex items-center justify-between rounded-t-lg px-3 py-2", color)}>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-700">{label}</span>
          <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-white text-xs font-medium text-slate-600">
            {taskCount}
          </span>
        </div>
        <button className="rounded p-1 hover:bg-white/50">
          <Plus size={14} className="text-slate-600" />
        </button>
      </div>

      {/* Column Content */}
      <div 
        className={cn(
          "flex-1 space-y-2 rounded-b-lg border-2 border-t-0 p-2 bg-slate-50/50",
          accentColors[id]
        )}
        style={{ minHeight: '200px' }}
      >
        {tasks.length === 0 ? (
          <div className="flex h-[180px] items-center justify-center">
            <p className="text-sm text-slate-400">No tasks</p>
          </div>
        ) : (
          tasks.map((task) => (
            <TaskCard 
              key={task.id} 
              task={task} 
              onClick={() => onTaskClick?.(task)}
            />
          ))
        )}
      </div>
    </div>
  );
}

export function TaskBoard({ tasks, onTaskClick, onStatusChange, className }: TaskBoardProps) {
  const [viewMode, setViewMode] = useState<'board' | 'list'>('board');
  const [filterPriority, setFilterPriority] = useState<TaskBoardTask['priority'] | 'all'>('all');
  const [filterProject, setFilterProject] = useState<string>('all');

  // Group tasks by status
  const tasksByStatus = COLUMNS.reduce((acc, col) => {
    acc[col.id] = tasks.filter(task => {
      if (task.status !== col.id) return false;
      if (filterPriority !== 'all' && task.priority !== filterPriority) return false;
      if (filterProject !== 'all' && task.projectId !== filterProject) return false;
      return true;
    });
    return acc;
  }, {} as Record<TaskBoardTask['status'], TaskBoardTask[]>);

  // Get unique projects for filter
  const projects = [...new Set(tasks.map(t => t.projectId))];

  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white", className)}>
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div className="flex items-center gap-3">
          {/* Priority Filter */}
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value as TaskBoardTask['priority'] | 'all')}
            className="h-8 rounded-lg border border-slate-200 bg-slate-50 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          {/* Project Filter */}
          <select
            value={filterProject}
            onChange={(e) => setFilterProject(e.target.value)}
            className="h-8 rounded-lg border border-slate-200 bg-slate-50 px-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Projects</option>
            {projects.map(projectId => (
              <option key={projectId} value={projectId}>{projectId}</option>
            ))}
          </select>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 rounded-lg border border-slate-200 p-1">
          <button
            onClick={() => setViewMode('board')}
            className={cn(
              "rounded px-2 py-1 text-xs font-medium transition-colors",
              viewMode === 'board' ? "bg-slate-800 text-white" : "text-slate-600 hover:bg-slate-100"
            )}
          >
            Board
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={cn(
              "rounded px-2 py-1 text-xs font-medium transition-colors",
              viewMode === 'list' ? "bg-slate-800 text-white" : "text-slate-600 hover:bg-slate-100"
            )}
          >
            List
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="overflow-x-auto p-4">
        {viewMode === 'board' ? (
          <div className="flex gap-3">
            {COLUMNS.map((col) => (
              <Column
                key={col.id}
                {...col}
                tasks={tasksByStatus[col.id]}
                onTaskClick={onTaskClick}
              />
            ))}
          </div>
        ) : (
          // List View
          <div className="space-y-2">
            <div className="grid grid-cols-12 gap-2 rounded-lg bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600">
              <div className="col-span-1">Status</div>
              <div className="col-span-5">Task</div>
              <div className="col-span-2">Priority</div>
              <div className="col-span-2">Project</div>
              <div className="col-span-2">Assignee</div>
            </div>
            {tasks.map((task) => {
              const StatusIcon = STATUS_ICONS[task.status];
              const priority = PRIORITY_CONFIG[task.priority];
              return (
                <div
                  key={task.id}
                  onClick={() => onTaskClick?.(task)}
                  className="grid cursor-pointer grid-cols-12 gap-2 rounded-lg border border-slate-100 bg-white px-3 py-2 text-sm transition-colors hover:bg-slate-50"
                >
                  <div className="col-span-1 flex items-center">
                    <StatusIcon size={16} className="text-slate-400" />
                  </div>
                  <div className="col-span-5 truncate font-medium text-slate-900">
                    {task.title}
                  </div>
                  <div className="col-span-2 flex items-center">
                    <span className={cn("rounded px-1.5 py-0.5 text-xs font-medium", priority.color, priority.bg)}>
                      {priority.label}
                    </span>
                  </div>
                  <div className="col-span-2 truncate text-slate-500">
                    {task.projectId}
                  </div>
                  <div className="col-span-2 truncate text-slate-500">
                    {task.assignee || 'Unassigned'}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
