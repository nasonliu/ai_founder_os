/**
 * AI Founder OS - API Client
 * 
 * Frontend API client for connecting to the Python backend.
 * 
 * Usage:
 *   import { api } from '@/lib/api'
 *   
 *   // Get all projects
 *   const projects = await api.projects.list()
 *   
 *   // Get specific project
 *   const project = await api.projects.get('proj_xxx')
 *   
 *   // Create a new task
 *   const task = await api.tasks.create({ project_id: 'proj_xxx', title: 'New Task' })
 */

// ============================================================================
// Types
// ============================================================================

export interface Idea {
  id: string
  title: string
  description: string
  tags: string[]
  priority: string
  value_hypothesis: string
  risk_level: string
  status: string
  links: Record<string, string[]>
  created_by: string
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  name: string
  one_sentence_goal: string
  kpis: Array<{
    name: string
    target: string
    validator: string
    priority: string
  }>
  definition_of_done: string[]
  constraints: Record<string, string[]>
  operating_mode: string
  execution_limits: Record<string, number>
  routing_policy: Record<string, unknown>
  governance: Record<string, unknown>
  status: string
  current_bottleneck: string
  next_3_tasks: string[]
  created_by: string
  created_at: string
  updated_at: string
}

export interface Task {
  id: string
  project_id: string
  title: string
  goal: string
  inputs: Record<string, unknown>
  expected_artifact: {
    type: string
    path_hint: string
    acceptance_criteria: string[]
  }
  validators: Array<{
    id: string
    type: string
    command: string
    success_criteria: string
    blocking: boolean
  }>
  risk_level: string
  required_capabilities: string[]
  routing_hints: Record<string, unknown>
  state: string
  retry_count: number
  depends_on: string[]
  created_by: string
  assigned_to: Record<string, unknown>
  timestamps: Record<string, string>
}

export interface Worker {
  worker_id: string
  worker_type: string
  model_source: string
  capability_tokens: string[]
  xp: {
    total: number
    success: number
    failure: number
    reused: number
  }
  status: string
  current_task_id: string
  reputation: {
    score: number
    success_rate: number
    avg_resolution_time: number
  }
}

export interface ReviewCard {
  id: string
  project_id: string
  type: string
  risk_level: string
  context: Record<string, unknown>
  proposal: Record<string, unknown>
  evidence_ids: string[]
  impact_preview: Record<string, unknown>
  status: string
  resolution: {
    by: string
    decision: string
    notes: string
    resolved_at: string
  } | null
  created_at: string
  updated_at: string
}

export interface Connection {
  connection_id: string
  provider: string
  name: string
  auth_type: string
  credentials: Record<string, unknown>
  scopes: string[]
  quota: Record<string, unknown>
  allowed_workers: string[]
  allowed_projects: string[]
  status: string
  last_used: string
  health_check: Record<string, unknown>
}

export interface SystemStatus {
  system_health: string
  system_status: string
  execution_mode: string
  stats: {
    total_ideas: number
    active_projects: number
    total_tasks: number
    pending_tasks: number
    total_workers: number
    idle_workers: number
    pending_reviews: number
  }
  last_updated: string
}

// ============================================================================
// API Client
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  
  if (!response.ok) {
    throw new ApiError(response.status, `API Error: ${response.statusText}`)
  }
  
  return response.json()
}

// ============================================================================
// API Methods
// ============================================================================

export const api = {
  // Ideas
  ideas: {
    list: (params?: { status?: string; priority?: string; limit?: number }) => 
      fetchApi<Idea[]>('/api/ideas', { 
        method: 'GET',
        ...(params && { 
          searchParams: new URLSearchParams(
            Object.entries(params).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)])
          ).toString() 
        })
      }),
    
    get: (id: string) => 
      fetchApi<Idea>(`/api/ideas/${id}`),
    
    create: (idea: Partial<Idea>) => 
      fetchApi<Idea>('/api/ideas', {
        method: 'POST',
        body: JSON.stringify(idea),
      }),
    
    update: (id: string, idea: Partial<Idea>) => 
      fetchApi<Idea>(`/api/ideas/${id}`, {
        method: 'PUT',
        body: JSON.stringify(idea),
      }),
  },

  // Projects
  projects: {
    list: (params?: { status?: string; limit?: number }) => 
      fetchApi<Project[]>('/api/projects', {
        method: 'GET',
      }),
    
    get: (id: string) => 
      fetchApi<Project>(`/api/projects/${id}`),
    
    create: (project: Partial<Project>) => 
      fetchApi<Project>('/api/projects', {
        method: 'POST',
        body: JSON.stringify(project),
      }),
    
    update: (id: string, project: Partial<Project>) => 
      fetchApi<Project>(`/api/projects/${id}`, {
        method: 'PUT',
        body: JSON.stringify(project),
      }),
  },

  // Tasks
  tasks: {
    list: (params?: { project_id?: string; state?: string; limit?: number }) => 
      fetchApi<Task[]>('/api/tasks', {
        method: 'GET',
      }),
    
    get: (id: string) => 
      fetchApi<Task>(`/api/tasks/${id}`),
    
    create: (task: Partial<Task>) => 
      fetchApi<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(task),
      }),
    
    update: (id: string, task: Partial<Task>) => 
      fetchApi<Task>(`/api/tasks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(task),
      }),
  },

  // Workers
  workers: {
    list: (params?: { worker_type?: string; status?: string }) => 
      fetchApi<Worker[]>('/api/workers', {
        method: 'GET',
      }),
    
    get: (id: string) => 
      fetchApi<Worker>(`/api/workers/${id}`),
    
    update: (id: string, worker: Partial<Worker>) => 
      fetchApi<Worker>(`/api/workers/${id}`, {
        method: 'PUT',
        body: JSON.stringify(worker),
      }),
  },

  // Reviews (Human Gate)
  reviews: {
    list: (params?: { project_id?: string; status?: string; gate_type?: string }) => 
      fetchApi<ReviewCard[]>('/api/reviews', {
        method: 'GET',
      }),
    
    get: (id: string) => 
      fetchApi<ReviewCard>(`/api/reviews/${id}`),
    
    create: (review: Partial<ReviewCard>) => 
      fetchApi<ReviewCard>('/api/reviews', {
        method: 'POST',
        body: JSON.stringify(review),
      }),
    
    approve: (id: string, notes: string = '') => 
      fetchApi<ReviewCard>(`/api/reviews/${id}/approve`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
    
    reject: (id: string, notes: string = '') => 
      fetchApi<ReviewCard>(`/api/reviews/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ notes }),
      }),
  },

  // Connections
  connections: {
    list: (params?: { provider?: string; status?: string }) => 
      fetchApi<Connection[]>('/api/connections', {
        method: 'GET',
      }),
    
    get: (id: string) => 
      fetchApi<Connection>(`/api/connections/${id}`),
    
    create: (connection: Partial<Connection>) => 
      fetchApi<Connection>('/api/connections', {
        method: 'POST',
        body: JSON.stringify(connection),
      }),
  },

  // System
  system: {
    status: () => fetchApi<SystemStatus>('/api/system/status'),
    
    setMode: (mode: string) => 
      fetchApi<{ execution_mode: string }>('/api/system/mode', {
        method: 'POST',
        body: JSON.stringify({ mode }),
      }),
  },

  // Health
  health: () => fetchApi<{ status: string; timestamp: string }>('/health'),
}

// ============================================================================
// Utility Hook (for React components)
// ============================================================================

import { useState, useEffect, useCallback } from 'react'

/**
 * Hook for fetching data with loading and error states
 */
export function useApi<T>(
  fetchFn: () => Promise<T>,
  deps: unknown[] = []
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  const refetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn()
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e : new Error('Unknown error'))
    } finally {
      setLoading(false)
    }
  }, deps)

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, loading, error, refetch }
}

/**
 * Hook for listing projects
 */
export function useProjects(status?: string) {
  return useApi(
    () => api.projects.list({ status }),
    [status]
  )
}

/**
 * Hook for listing tasks
 */
export function useTasks(projectId?: string, state?: string) {
  return useApi(
    () => api.tasks.list({ project_id: projectId, state }),
    [projectId, state]
  )
}

/**
 * Hook for listing workers
 */
export function useWorkers(workerType?: string, status?: string) {
  return useApi(
    () => api.workers.list({ worker_type: workerType, status }),
    [workerType, status]
  )
}

/**
 * Hook for listing review cards
 */
export function useReviews(projectId?: string, status?: string) {
  return useApi(
    () => api.reviews.list({ project_id: projectId, status }),
    [projectId, status]
  )
}

/**
 * Hook for system status
 */
export function useSystemStatus() {
  return useApi(() => api.system.status(), [])
}

export default api
