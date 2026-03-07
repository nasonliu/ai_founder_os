/**
 * AI Founder OS - WorkerMonitor Component
 * 
 * Real-time worker status display with metrics and health indicators.
 */

import { useState } from 'react';
import { 
  Users, 
  Cpu, 
  Activity, 
  Zap, 
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Pause,
  Play,
  RefreshCw,
  ChevronDown,
  BarChart3,
  Clock,
  Target,
  TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface WorkerMetric {
  id: string;
  type: 'builder' | 'researcher' | 'documenter' | 'verifier' | 'evaluator';
  status: 'idle' | 'assigned' | 'running' | 'verifying' | 'completed' | 'failed' | 'paused' | 'error';
  currentTask?: string;
  successRate: number;
  xp: number;
  reputation: number;
  avgResolutionTime: number;
  totalTasks: number;
  successCount: number;
  failureCount: number;
  reusedCount: number;
  modelSource?: string;
  lastActive?: string;
}

interface WorkerMonitorProps {
  workers: WorkerMetric[];
  onWorkerClick?: (worker: WorkerMetric) => void;
  onWorkerAction?: (workerId: string, action: 'pause' | 'resume' | 'reset') => void;
  className?: string;
}

// Worker type configuration
const WORKER_TYPE_CONFIG = {
  builder: { 
    label: 'Builder', 
    color: 'bg-blue-500', 
    icon: Cpu,
    description: 'Code generation, implementation'
  },
  researcher: { 
    label: 'Researcher', 
    color: 'bg-purple-500', 
    icon: SearchIcon,
    description: 'Research, analysis'
  },
  documenter: { 
    label: 'Documenter', 
    color: 'bg-green-500', 
    icon: FileText,
    description: 'Documentation, PRDs'
  },
  verifier: { 
    label: 'Verifier', 
    color: 'bg-yellow-500', 
    icon: CheckCircle2,
    description: 'Testing, validation'
  },
  evaluator: { 
    label: 'Evaluator', 
    color: 'bg-red-500', 
    icon: BarChart3,
    description: 'Metrics, benchmarking'
  },
};

// Status configuration
const STATUS_CONFIG = {
  idle: { 
    label: 'Idle', 
    color: 'text-slate-500', 
    bg: 'bg-slate-100',
    icon: Pause 
  },
  assigned: { 
    label: 'Assigned', 
    color: 'text-blue-600', 
    bg: 'bg-blue-100',
    icon: Target
  },
  running: { 
    label: 'Running', 
    color: 'text-yellow-600', 
    bg: 'bg-yellow-100',
    icon: Activity
  },
  verifying: { 
    label: 'Verifying', 
    color: 'text-purple-600', 
    bg: 'bg-purple-100',
    icon: RefreshCw
  },
  completed: { 
    label: 'Completed', 
    color: 'text-green-600', 
    bg: 'bg-green-100',
    icon: CheckCircle2
  },
  failed: { 
    label: 'Failed', 
    color: 'text-red-600', 
    bg: 'bg-red-100',
    icon: XCircle
  },
  paused: { 
    label: 'Paused', 
    color: 'text-orange-600', 
    bg: 'bg-orange-100',
    icon: Pause
  },
  error: { 
    label: 'Error', 
    color: 'text-red-600', 
    bg: 'bg-red-100',
    icon: AlertTriangle
  },
};

// Helper icons (import replacements)
function SearchIcon({ size = 24 }: { size?: number }) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.3-4.3" />
    </svg>
  );
}

function FileText({ size = 24 }: { size?: number }) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      width={size} 
      height={size} 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    >
      <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" x2="8" y1="13" y2="13" />
      <line x1="16" x2="8" y1="17" y2="17" />
      <line x1="10" x2="8" y1="9" y2="9" />
    </svg>
  );
}

interface WorkerCardProps {
  worker: WorkerMetric;
  expanded?: boolean;
  onClick?: () => void;
}

function WorkerCard({ worker, expanded = false, onClick }: WorkerCardProps) {
  const typeConfig = WORKER_TYPE_CONFIG[worker.type];
  const statusConfig = STATUS_CONFIG[worker.status];
  const TypeIcon = typeConfig?.icon || Cpu;
  const StatusIcon = statusConfig?.icon || Pause;

  // Calculate success rate color
  const getSuccessRateColor = (rate: number) => {
    if (rate >= 0.9) return 'text-green-600';
    if (rate >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Format XP with K suffix
  const formatXP = (xp: number) => {
    if (xp >= 1000) return `${(xp / 1000).toFixed(1)}K`;
    return xp.toString();
  };

  return (
    <div 
      onClick={onClick}
      className={cn(
        "cursor-pointer rounded-lg border border-slate-200 bg-white transition-all hover:shadow-md",
        expanded && "col-span-2"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 p-3">
        <div className="flex items-center gap-2">
          <div className={cn("flex h-8 w-8 items-center justify-center rounded-lg", typeConfig?.color || 'bg-slate-500')}>
            <TypeIcon size={16} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-900">{worker.id}</p>
            <p className="text-xs text-slate-500">{typeConfig?.label || worker.type}</p>
          </div>
        </div>
        <span className={cn("flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium", statusConfig?.bg, statusConfig?.color)}>
          <StatusIcon size={12} />
          {statusConfig?.label || worker.status}
        </span>
      </div>

      {/* Current Task */}
      {worker.currentTask && (
        <div className="border-b border-slate-100 px-3 py-2">
          <p className="text-xs text-slate-500">Current Task</p>
          <p className="mt-0.5 truncate text-sm font-medium text-slate-700">{worker.currentTask}</p>
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-2 p-3">
        <div>
          <p className="flex items-center gap-1 text-xs text-slate-500">
            <TrendingUp size={12} /> Success Rate
          </p>
          <p className={cn("mt-0.5 text-lg font-bold", getSuccessRateColor(worker.successRate))}>
            {(worker.successRate * 100).toFixed(0)}%
          </p>
        </div>
        <div>
          <p className="flex items-center gap-1 text-xs text-slate-500">
            <Zap size={12} /> XP
          </p>
          <p className="mt-0.5 text-lg font-bold text-purple-600">{formatXP(worker.xp)}</p>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t border-slate-100 bg-slate-50 p-3">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <p className="text-slate-500">Avg Resolution</p>
              <p className="font-medium text-slate-700">{worker.avgResolutionTime.toFixed(1)} min</p>
            </div>
            <div>
              <p className="text-slate-500">Reputation</p>
              <p className="font-medium text-slate-700">{worker.reputation.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-slate-500">Tasks Completed</p>
              <p className="font-medium text-slate-700">{worker.successCount}</p>
            </div>
            <div>
              <p className="text-slate-500">Failed</p>
              <p className="font-medium text-slate-700">{worker.failureCount}</p>
            </div>
            {worker.modelSource && (
              <div className="col-span-2">
                <p className="text-slate-500">Model</p>
                <p className="font-medium text-slate-700 truncate">{worker.modelSource}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Stats summary component
interface WorkerStatsSummaryProps {
  workers: WorkerMetric[];
}

function WorkerStatsSummary({ workers }: WorkerStatsSummaryProps) {
  const total = workers.length;
  const idle = workers.filter(w => w.status === 'idle').length;
  const busy = workers.filter(w => ['running', 'assigned', 'verifying'].includes(w.status)).length;
  const paused = workers.filter(w => w.status === 'paused').length;
  const error = workers.filter(w => w.status === 'error').length;
  
  const avgSuccessRate = workers.length > 0 
    ? workers.reduce((sum, w) => sum + w.successRate, 0) / workers.length 
    : 0;
  
  const totalXP = workers.reduce((sum, w) => sum + w.xp, 0);

  return (
    <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-5">
      <div className="rounded-lg bg-slate-50 p-3">
        <div className="flex items-center gap-2 text-slate-500">
          <Users size={14} />
          <span className="text-xs">Total</span>
        </div>
        <p className="mt-1 text-xl font-bold text-slate-900">{total}</p>
      </div>
      <div className="rounded-lg bg-green-50 p-3">
        <div className="flex items-center gap-2 text-green-600">
          <Pause size={14} />
          <span className="text-xs">Idle</span>
        </div>
        <p className="mt-1 text-xl font-bold text-green-700">{idle}</p>
      </div>
      <div className="rounded-lg bg-yellow-50 p-3">
        <div className="flex items-center gap-2 text-yellow-600">
          <Activity size={14} />
          <span className="text-xs">Busy</span>
        </div>
        <p className="mt-1 text-xl font-bold text-yellow-700">{busy}</p>
      </div>
      <div className="rounded-lg bg-blue-50 p-3">
        <div className="flex items-center gap-2 text-blue-600">
          <TrendingUp size={14} />
          <span className="text-xs">Avg Success</span>
        </div>
        <p className="mt-1 text-xl font-bold text-blue-700">{(avgSuccessRate * 100).toFixed(0)}%</p>
      </div>
      <div className="rounded-lg bg-purple-50 p-3">
        <div className="flex items-center gap-2 text-purple-600">
          <Zap size={14} />
          <span className="text-xs">Total XP</span>
        </div>
        <p className="mt-1 text-xl font-bold text-purple-700">{totalXP}</p>
      </div>
    </div>
  );
}

// Worker Type Filter
interface WorkerTypeFilterProps {
  selectedType: string | null;
  onTypeSelect: (type: string | null) => void;
}

function WorkerTypeFilter({ selectedType, onTypeSelect }: WorkerTypeFilterProps) {
  const types = ['builder', 'researcher', 'documenter', 'verifier', 'evaluator'] as const;
  
  return (
    <div className="mb-4 flex flex-wrap gap-2">
      <button
        onClick={() => onTypeSelect(null)}
        className={cn(
          "rounded-full px-3 py-1 text-xs font-medium transition-colors",
          selectedType === null 
            ? "bg-slate-800 text-white" 
            : "bg-slate-100 text-slate-600 hover:bg-slate-200"
        )}
      >
        All
      </button>
      {types.map((type) => {
        const config = WORKER_TYPE_CONFIG[type];
        return (
          <button
            key={type}
            onClick={() => onTypeSelect(type)}
            className={cn(
              "flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-colors",
              selectedType === type 
                ? "bg-slate-800 text-white" 
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            )}
          >
            <div className={cn("h-2 w-2 rounded-full", config?.color)} />
            {config?.label}
          </button>
        );
      })}
    </div>
  );
}

export function WorkerMonitor({ 
  workers, 
  onWorkerClick, 
  onWorkerAction,
  className 
}: WorkerMonitorProps) {
  const [expandedWorker, setExpandedWorker] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'status' | 'xp' | 'successRate'>('status');

  // Filter workers by type
  const filteredWorkers = workers.filter(w => 
    selectedType ? w.type === selectedType : true
  );

  // Sort workers
  const sortedWorkers = [...filteredWorkers].sort((a, b) => {
    if (sortBy === 'xp') return b.xp - a.xp;
    if (sortBy === 'successRate') return b.successRate - a.successRate;
    // Default: sort by status (busy first)
    const statusOrder = ['running', 'assigned', 'verifying', 'idle', 'paused', 'error', 'completed', 'failed'];
    return statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status);
  });

  return (
    <div className={cn("rounded-xl border border-slate-200 bg-white", className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <h3 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <Users size={16} />
          Worker Pool
        </h3>
        <div className="flex items-center gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="h-7 rounded-lg border border-slate-200 bg-slate-50 px-2 text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="status">Sort by Status</option>
            <option value="xp">Sort by XP</option>
            <option value="successRate">Sort by Success</option>
          </select>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="border-b border-slate-200 px-4 py-3">
        <WorkerStatsSummary workers={filteredWorkers} />
      </div>

      {/* Type Filter */}
      <div className="border-b border-slate-200 px-4 pt-3">
        <WorkerTypeFilter 
          selectedType={selectedType} 
          onTypeSelect={setSelectedType} 
        />
      </div>

      {/* Worker Grid */}
      <div className="p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {sortedWorkers.map((worker) => (
            <WorkerCard
              key={worker.id}
              worker={worker}
              expanded={expandedWorker === worker.id}
              onClick={() => {
                setExpandedWorker(expandedWorker === worker.id ? null : worker.id);
                onWorkerClick?.(worker);
              }}
            />
          ))}
        </div>

        {sortedWorkers.length === 0 && (
          <div className="flex flex-col items-center justify-center py-8 text-slate-400">
            <Users size={32} />
            <p className="mt-2 text-sm">No workers found</p>
          </div>
        )}
      </div>
    </div>
  );
}

export type { WorkerMonitorProps };
