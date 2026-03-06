import { useState, useEffect } from 'react'

// Types
interface Project {
  id: string
  name: string
  status: string
  tasks: number
  workers: number
  progress: number
}

interface Worker {
  id: string
  name: string
  type: string
  status: string
  xp: number
}

interface Task {
  id: string
  title: string
  project: string
  worker: string
  status: string
  priority: string
}

interface Review {
  id: string
  title: string
  type: string
  status: string
  requester: string
  date: string
}

// Demo data
const demoProjects: Project[] = [
  { id: '1', name: 'AI Founder OS', status: 'active', tasks: 12, workers: 3, progress: 75 },
  { id: '2', name: 'Mobile App', status: 'planning', tasks: 5, workers: 2, progress: 20 },
  { id: '3', name: 'API Integration', status: 'active', tasks: 8, workers: 2, progress: 60 },
]

const demoWorkers: Worker[] = [
  { id: 'w1', name: 'Builder-01', type: 'builder', status: 'running', xp: 1250 },
  { id: 'w2', name: 'Researcher-01', type: 'researcher', status: 'idle', xp: 890 },
  { id: 'w3', name: 'Verifier-01', type: 'verifier', status: 'running', xp: 2100 },
  { id: 'w4', name: 'Documenter-01', type: 'documenter', status: 'idle', xp: 560 },
  { id: 'w5', name: 'Evaluator-01', type: 'evaluator', status: 'idle', xp: 720 },
]

const demoTasks: Task[] = [
  { id: 't1', title: 'Implement Planner Loop', project: 'AI Founder OS', worker: 'Builder-01', status: 'completed', priority: 'high' },
  { id: 't2', title: 'Add Worker Registry', project: 'AI Founder OS', worker: 'Builder-01', status: 'running', priority: 'high' },
  { id: 't3', title: 'Write Policy Engine Tests', project: 'AI Founder OS', worker: 'Verifier-01', status: 'pending', priority: 'medium' },
  { id: 't4', title: 'Research API Options', project: 'Mobile App', worker: 'Researcher-01', status: 'completed', priority: 'low' },
  { id: 't5', title: 'Design Database Schema', project: 'Mobile App', worker: 'Builder-01', status: 'pending', priority: 'high' },
  { id: 't6', title: 'Setup CI/CD Pipeline', project: 'API Integration', worker: 'Builder-01', status: 'running', priority: 'high' },
]

const demoReviews: Review[] = [
  { id: 'r1', title: 'Deploy to Production', type: 'deployment', status: 'pending', requester: 'Builder-01', date: '2 min ago' },
  { id: 'r2', title: 'Install New Skill: AWS Lambda', type: 'skill', status: 'pending', requester: 'System', date: '15 min ago' },
  { id: 'r3', title: 'Delete Test Database', type: 'data', status: 'approved', requester: 'Builder-01', date: '1 hour ago' },
]

type TabId = 'overview' | 'projects' | 'workers' | 'tasks' | 'reviews' | 'settings'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')

  useEffect(() => {
    const hash = window.location.hash.slice(1) as TabId
    if (['overview', 'projects', 'workers', 'tasks', 'reviews', 'settings'].includes(hash)) {
      setActiveTab(hash)
    }
  }, [])

  const handleTabChange = (tab: TabId) => {
    setActiveTab(tab)
    window.location.hash = tab
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'projects', label: 'Projects' },
    { id: 'workers', label: 'Workers' },
    { id: 'tasks', label: 'Tasks' },
    { id: 'reviews', label: 'Reviews' },
    { id: 'settings', label: 'Settings' },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <OverviewPanel />
      case 'projects': return <ProjectsPanel projects={demoProjects} />
      case 'workers': return <WorkersPanel workers={demoWorkers} />
      case 'tasks': return <TasksPanel tasks={demoTasks} />
      case 'reviews': return <ReviewsPanel reviews={demoReviews} />
      case 'settings': return <SettingsPanel />
      default: return <OverviewPanel />
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f9fafb' }}>
      {/* Sidebar */}
      <aside style={{ width: '240px', background: 'white', borderRight: '1px solid #e5e7eb', padding: '16px', display: 'flex', flexDirection: 'column' }}>
        <h1 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827' }}>AI Founder OS</h1>
        <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '24px' }}>Dashboard</p>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => handleTabChange(tab.id as TabId)}
              style={{
                padding: '10px 12px',
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
              {tab.id === 'reviews' && (
                <span style={{ marginLeft: '8px', background: '#ef4444', color: 'white', padding: '2px 6px', borderRadius: '10px', fontSize: '11px' }}>
                  2
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* System Status */}
        <div style={{ padding: '12px', background: '#f0fdf4', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22c55e' }} />
            <span style={{ fontSize: '13px', color: '#166534', fontWeight: '500' }}>System Online</span>
          </div>
          <p style={{ fontSize: '12px', color: '#15803d', marginTop: '4px' }}>v1.0.0</p>
        </div>
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

      {/* Project Progress */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Project Progress</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {demoProjects.map((project) => (
            <div key={project.id}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ color: '#374151', fontWeight: '500' }}>{project.name}</span>
                <span style={{ color: '#6b7280', fontSize: '14px' }}>{project.progress}%</span>
              </div>
              <div style={{ height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${project.progress}%`, background: project.progress > 70 ? '#22c55e' : '#3b82f6', borderRadius: '4px' }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px' }}>
        {/* Recent Activity */}
        <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recent Activity</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {[
              { text: 'Task completed: Implement Planner Loop', time: '2m ago', color: '#22c55e' },
              { text: 'Worker assigned: builder_01', time: '5m ago', color: '#3b82f6' },
              { text: 'Review requested: Skill Installation', time: '10m ago', color: '#eab308' },
              { text: 'Project created: Mobile App', time: '1h ago', color: '#a855f7' },
            ].map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: item.color }} />
                <span style={{ color: '#374151', flex: 1 }}>{item.text}</span>
                <span style={{ color: '#9ca3af', fontSize: '14px' }}>{item.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Quick Actions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {['Create Project', 'Add Task', 'Review Requests', 'View Logs'].map((action, i) => (
              <button key={i} style={{ padding: '10px 16px', textAlign: 'left', background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '6px', cursor: 'pointer', color: '#374151' }}>
                {action}
              </button>
            ))}
          </div>
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
        <button style={{ background: '#2563eb', color: 'white', padding: '10px 20px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: '500' }}>
          + New Project
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {projects.map((project) => (
          <div key={project.id} style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <h3 style={{ fontWeight: '600', color: '#111827' }}>{project.name}</h3>
              <span style={{ padding: '4px 8px', borderRadius: '12px', fontSize: '12px', background: project.status === 'active' ? '#dcfce7' : '#fef3c7', color: project.status === 'active' ? '#16a34a' : '#d97706' }}>
                {project.status}
              </span>
            </div>
            <div style={{ display: 'flex', gap: '16px', color: '#6b7280', fontSize: '14px', marginBottom: '12px' }}>
              <span>{project.tasks} tasks</span>
              <span>{project.workers} workers</span>
            </div>
            <div style={{ height: '6px', background: '#e5e7eb', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${project.progress}%`, background: '#3b82f6', borderRadius: '3px' }} />
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'builder': return '🔨'
      case 'researcher': return '🔍'
      case 'verifier': return '✅'
      case 'documenter': return '📝'
      case 'evaluator': return '📊'
      default: return '🤖'
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Workers</h2>
        <p style={{ color: '#6b7280' }}>Monitor worker status and performance</p>
      </div>

      {/* Worker Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {[
          { label: 'Total Workers', value: '5' },
          { label: 'Running', value: '2', color: '#22c55e' },
          { label: 'Idle', value: '3', color: '#9ca3af' },
          { label: 'Total XP', value: '5,420', color: '#a855f7' },
        ].map((stat) => (
          <div key={stat.label} style={{ background: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: stat.color || '#111827' }}>{stat.value}</div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Worker Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px' }}>
        {workers.map((worker) => (
          <div key={worker.id} style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>{getTypeIcon(worker.type)}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: getStatusColor(worker.status) }} />
              <span style={{ fontWeight: '500', color: '#111827' }}>{worker.name}</span>
            </div>
            <p style={{ color: '#6b7280', fontSize: '14px', textTransform: 'capitalize' }}>{worker.type}</p>
            <p style={{ color: '#a855f7', fontSize: '14px', marginTop: '8px' }}>XP: {worker.xp}</p>
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#ef4444'
      case 'medium': return '#eab308'
      case 'low': return '#22c55e'
      default: return '#9ca3af'
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Tasks</h2>
          <p style={{ color: '#6b7280' }}>View and manage all tasks</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button style={{ background: 'white', color: '#374151', padding: '10px 16px', borderRadius: '6px', border: '1px solid #e5e7eb', cursor: 'pointer' }}>
            Filter
          </button>
          <button style={{ background: '#2563eb', color: 'white', padding: '10px 20px', borderRadius: '6px', border: 'none', cursor: 'pointer', fontWeight: '500' }}>
            + New Task
          </button>
        </div>
      </div>

      <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Task</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Project</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Worker</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Priority</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', color: '#6b7280', fontWeight: '500', fontSize: '14px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', color: '#111827', fontWeight: '500' }}>{task.title}</td>
                <td style={{ padding: '12px 16px', color: '#6b7280' }}>{task.project}</td>
                <td style={{ padding: '12px 16px', color: '#6b7280' }}>{task.worker}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ padding: '4px 8px', borderRadius: '12px', fontSize: '12px', background: getPriorityColor(task.priority) + '20', color: getPriorityColor(task.priority), textTransform: 'capitalize' }}>
                    {task.priority}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ padding: '4px 8px', borderRadius: '12px', fontSize: '12px', background: getStatusColor(task.status) + '20', color: getStatusColor(task.status), textTransform: 'capitalize' }}>
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

function ReviewsPanel({ reviews }: { reviews: Review[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Reviews</h2>
        <p style={{ color: '#6b7280' }}>Human-in-the-loop approval requests</p>
      </div>

      {/* Pending Reviews */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>
          Pending Reviews 
          <span style={{ marginLeft: '8px', background: '#ef4444', color: 'white', padding: '2px 8px', borderRadius: '10px', fontSize: '14px' }}>
            {reviews.filter(r => r.status === 'pending').length}
          </span>
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {reviews.filter(r => r.status === 'pending').map((review) => (
            <div key={review.id} style={{ padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: '500', color: '#111827', marginBottom: '4px' }}>{review.title}</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>
                  <span style={{ background: '#f3f4f6', padding: '2px 8px', borderRadius: '4px', marginRight: '8px' }}>{review.type}</span>
                  by {review.requester} • {review.date}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button style={{ background: '#ef4444', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>Reject</button>
                <button style={{ background: '#22c55e', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>Approve</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Approved Reviews */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Recent Decisions</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {reviews.filter(r => r.status !== 'pending').map((review) => (
            <div key={review.id} style={{ padding: '12px', border: '1px solid #e5e7eb', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: '500', color: '#111827' }}>{review.title}</div>
                <div style={{ fontSize: '14px', color: '#6b7280' }}>by {review.requester} • {review.date}</div>
              </div>
              <span style={{ padding: '4px 12px', borderRadius: '12px', fontSize: '12px', background: '#22c55e20', color: '#22c55e' }}>{review.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SettingsPanel() {
  const [executionMode, setExecutionMode] = useState('normal')

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827' }}>Settings</h2>
        <p style={{ color: '#6b7280' }}>Configure system settings</p>
      </div>

      {/* Execution Mode */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Execution Mode</h3>
        <div style={{ display: 'flex', gap: '12px' }}>
          {['safe', 'normal', 'turbo'].map((mode) => (
            <button
              key={mode}
              onClick={() => setExecutionMode(mode)}
              style={{
                padding: '12px 24px',
                borderRadius: '8px',
                border: executionMode === mode ? '2px solid #2563eb' : '2px solid #e5e7eb',
                background: executionMode === mode ? '#eff6ff' : 'white',
                color: executionMode === mode ? '#2563eb' : '#374151',
                cursor: 'pointer',
                fontWeight: '500',
                textTransform: 'capitalize'
              }}
            >
              {mode}
            </button>
          ))}
        </div>
        <p style={{ marginTop: '12px', color: '#6b7280', fontSize: '14px' }}>
          {executionMode === 'safe' && 'Limited concurrency, all actions require approval'}
          {executionMode === 'normal' && 'Balanced performance with reasonable safety checks'}
          {executionMode === 'turbo' && 'Maximum speed, minimal safety overhead'}
        </p>
      </div>

      {/* System Info */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>System Information</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {[
            ['Version', '1.0.0'],
            ['Python', '3.11+'],
            ['Workers', '5 configured'],
            ['API Status', 'Online'],
          ].map(([key, value]) => (
            <div key={key} style={{ padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
              <div style={{ color: '#6b7280', fontSize: '14px' }}>{key}</div>
              <div style={{ color: '#111827', fontWeight: '500' }}>{value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Danger Zone */}
      <div style={{ background: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #fecaca' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#dc2626', marginBottom: '16px' }}>Danger Zone</h3>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button style={{ background: 'white', color: '#dc2626', padding: '10px 16px', borderRadius: '6px', border: '1px solid #dc2626', cursor: 'pointer' }}>
            Reset System
          </button>
          <button style={{ background: '#dc2626', color: 'white', padding: '10px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>
            Clear All Data
          </button>
        </div>
      </div>
    </div>
  )
}
