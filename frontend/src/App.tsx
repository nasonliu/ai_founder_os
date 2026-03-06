import { useState, useEffect } from 'react'

// Types
interface Project {
  id: string
  name: string
  status: string
  tasks: number
  workers: number
}

interface Worker {
  id: string
  name: string
  type: string
  status: string
}

interface Task {
  id: string
  title: string
  project: string
  worker: string
  status: string
}

// Demo data
const demoProjects: Project[] = [
  { id: '1', name: 'AI Founder OS', status: 'active', tasks: 12, workers: 3 },
  { id: '2', name: 'Mobile App', status: 'planning', tasks: 5, workers: 2 },
  { id: '3', name: 'API Integration', status: 'active', tasks: 8, workers: 2 },
]

const demoWorkers: Worker[] = [
  { id: 'w1', name: 'Builder-01', type: 'builder', status: 'running' },
  { id: 'w2', name: 'Researcher-01', type: 'researcher', status: 'idle' },
  { id: 'w3', name: 'Verifier-01', type: 'verifier', status: 'running' },
  { id: 'w4', name: 'Documenter-01', type: 'documenter', status: 'idle' },
  { id: 'w5', name: 'Evaluator-01', type: 'evaluator', status: 'idle' },
]

const demoTasks: Task[] = [
  { id: 't1', title: 'Implement Planner Loop', project: 'AI Founder OS', worker: 'Builder-01', status: 'completed' },
  { id: 't2', title: 'Add Worker Registry', project: 'AI Founder OS', worker: 'Builder-01', status: 'running' },
  { id: 't3', title: 'Write Policy Engine Tests', project: 'AI Founder OS', worker: 'Verifier-01', status: 'pending' },
  { id: 't4', title: 'Research API Options', project: 'Mobile App', worker: 'Researcher-01', status: 'completed' },
]

type TabId = 'overview' | 'projects' | 'workers' | 'tasks'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')

  // Get tab from URL hash
  useEffect(() => {
    const hash = window.location.hash.slice(1) as TabId
    if (['overview', 'projects', 'workers', 'tasks'].includes(hash)) {
      setActiveTab(hash)
    }
  }, [])

  // Update URL when tab changes
  const handleTabChange = (tab: TabId) => {
    setActiveTab(tab)
    window.location.hash = tab
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPanel />
      case 'projects':
        return <ProjectsPanel projects={demoProjects} />
      case 'workers':
        return <WorkersPanel workers={demoWorkers} />
      case 'tasks':
        return <TasksPanel tasks={demoTasks} />
      default:
        return <OverviewPanel />
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f9fafb' }}>
      {/* Sidebar */}
      <aside style={{ width: '240px', background: 'white', borderRight: '1px solid #e5e7eb', padding: '16px' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827' }}>AI Founder OS</h1>
        <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>Dashboard</p>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'projects', label: 'Projects' },
            { id: 'workers', label: 'Workers' },
            { id: 'tasks', label: 'Tasks' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as TabId)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                textAlign: 'left',
                background: activeTab === tab.id ? '#eff6ff' : 'transparent',
                color: activeTab === tab.id ? '#2563eb' : '#374151',
                border: 'none',
                cursor: 'pointer',
                fontWeight: activeTab === tab.id ? '500' : '400',
              }}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'auto', padding: '24px' }}>
        {renderContent()}
      </main>
    </div>
  )
}

function OverviewPanel() {
  const stats = [
    { label: 'Active Projects', value: '3', color: '#3b82f6' },
    { label: 'Running Workers', value: '2', color: '#22c55e' },
    { label: 'Pending Reviews', value: '2', color: '#eab308' },
    { label: 'Completed Tasks', value: '28', color: '#a855f7' },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>System Overview</h2>
        <p style={{ color: '#6b7280' }}>Monitor your AI engineering organization</p>
      </div>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {stats.map((stat) => (
          <div key={stat.label} style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ width: '48px', height: '48px', background: stat.color, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '16px' }}>
              <span style={{ fontSize: '24px', fontWeight: 'bold', color: 'white' }}>{stat.value}</span>
            </div>
            <p style={{ color: '#6b7280', fontSize: '14px' }}>{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recent Activity</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {[
            { text: 'Task completed: Implement Planner Loop', time: '2m ago', color: '#22c55e' },
            { text: 'Worker assigned: builder_01', time: '5m ago', color: '#3b82f6' },
            { text: 'Review requested: Skill Installation', time: '10m ago', color: '#eab308' },
          ].map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: item.color }} />
              <span style={{ color: '#374151', flex: 1 }}>{item.text}</span>
              <span style={{ color: '#9ca3af', fontSize: '14px' }}>{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ProjectsPanel({ projects }: { projects: Project[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Projects</h2>
          <p style={{ color: '#6b7280' }}>Manage your projects</p>
        </div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>
          + New Project
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {projects.map((project) => (
          <div key={project.id} style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <h3 style={{ fontWeight: '600', color: '#111827' }}>{project.name}</h3>
              <span style={{ 
                padding: '4px 8px', 
                borderRadius: '12px', 
                fontSize: '12px',
                background: project.status === 'active' ? '#dcfce7' : '#fef3c7',
                color: project.status === 'active' ? '#16a34a' : '#d97706',
              }}>
                {project.status}
              </span>
            </div>
            <div style={{ display: 'flex', gap: '16px', color: '#6b7280', fontSize: '14px' }}>
              <span>{project.tasks} tasks</span>
              <span>{project.workers} workers</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function WorkersPanel({ workers }: { workers: Worker[] }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return '#22c55e'
      case 'idle': return '#9ca3af'
      case 'error': return '#ef4444'
      default: return '#9ca3af'
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Workers</h2>
        <p style={{ color: '#6b7280' }}>Monitor worker status</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
        {workers.map((worker) => (
          <div key={worker.id} style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: getStatusColor(worker.status) }} />
              <span style={{ fontWeight: '500', color: '#111827' }}>{worker.name}</span>
            </div>
            <p style={{ color: '#6b7280', fontSize: '14px', textTransform: 'capitalize' }}>{worker.type}</p>
            <p style={{ color: '#9ca3af', fontSize: '12px', marginTop: '4px', textTransform: 'capitalize' }}>{worker.status}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

function TasksPanel({ tasks }: { tasks: Task[] }) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#22c55e'
      case 'running': return '#3b82f6'
      case 'pending': return '#eab308'
      case 'failed': return '#ef4444'
      default: return '#9ca3af'
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Tasks</h2>
          <p style={{ color: '#6b7280' }}>View all tasks</p>
        </div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>
          + New Task
        </button>
      </div>

      <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Task</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Project</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Worker</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', color: '#111827' }}>{task.title}</td>
                <td style={{ padding: '12px 16px', color: '#6b7280' }}>{task.project}</td>
                <td style={{ padding: '12px 16px', color: '#6b7280' }}>{task.worker}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '12px', 
                    fontSize: '12px',
                    background: getStatusColor(task.status) + '20',
                    color: getStatusColor(task.status),
                  }}>
                    {task.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
