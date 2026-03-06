import { useState, useEffect } from 'react'

// Types
interface Idea {
  id: string
  title: string
  description: string
  tags: string[]
  priority: string
  status: string
  created: string
}

interface APIConnection {
  id: string
  name: string
  provider: string
  status: 'connected' | 'disconnected' | 'error'
  lastUsed: string
  calls: number
}

interface Route {
  id: string
  path: string
  method: string
  handler: string
  auth: boolean
  rateLimit: string
}

const demoIdeas: Idea[] = [
  { id: 'i1', title: 'AI Agent自动代码审查', description: '使用LLM实现自动化代码审查和优化建议', tags: ['AI', '代码审查'], priority: 'high', status: 'new', created: '2024-03-06' },
  { id: 'i2', title: '智能测试用例生成', description: '基于代码分析自动生成单元测试', tags: ['测试', '自动化'], priority: 'medium', status: 'reviewing', created: '2024-03-05' },
  { id: 'i3', title: '多模型路由优化', description: '根据任务类型自动选择最优LLM模型', tags: ['LLM', '优化'], priority: 'high', status: 'approved', created: '2024-03-04' },
  { id: 'i4', title: '可视化工作流编排', description: '拖拽式AI任务流程设计器', tags: ['UI', '工作流'], priority: 'low', status: 'new', created: '2024-03-03' },
]

const demoAPIs: APIConnection[] = [
  { id: 'a1', name: 'OpenAI', provider: 'OpenAI', status: 'connected', lastUsed: '2 min ago', calls: 1250 },
  { id: 'a2', name: 'Anthropic', provider: 'Anthropic', status: 'connected', lastUsed: '1 hour ago', calls: 890 },
  { id: 'a3', name: 'DeepSeek', provider: 'DeepSeek', status: 'connected', lastUsed: '30 min ago', calls: 2100 },
  { id: 'a4', name: 'GitHub', provider: 'GitHub', status: 'connected', lastUsed: '5 min ago', calls: 560 },
  { id: 'a5', name: 'Brave Search', provider: 'Brave', status: 'disconnected', lastUsed: '2 days ago', calls: 0 },
]

const demoRoutes: Route[] = [
  { id: 'r1', path: '/api/projects', method: 'GET', handler: 'list_projects', auth: true, rateLimit: '100/min' },
  { id: 'r2', path: '/api/projects', method: 'POST', handler: 'create_project', auth: true, rateLimit: '20/min' },
  { id: 'r3', path: '/api/tasks', method: 'GET', handler: 'list_tasks', auth: true, rateLimit: '100/min' },
  { id: 'r4', path: '/api/workers', method: 'GET', handler: 'list_workers', auth: true, rateLimit: '50/min' },
  { id: 'r5', path: '/api/reviews', method: 'GET', handler: 'list_reviews', auth: true, rateLimit: '50/min' },
  { id: 'r6', path: '/api/ideas', method: 'GET', handler: 'list_ideas', auth: false, rateLimit: '200/min' },
  { id: 'r7', path: '/api/system/status', method: 'GET', handler: 'system_status', auth: false, rateLimit: '500/min' },
]

type TabId = 'overview' | 'projects' | 'workers' | 'tasks' | 'reviews' | 'ideas' | 'apis' | 'routes' | 'settings'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')

  useEffect(() => {
    const hash = window.location.hash.slice(1) as TabId
    const validTabs = ['overview', 'projects', 'workers', 'tasks', 'reviews', 'ideas', 'apis', 'routes', 'settings']
    if (validTabs.includes(hash)) setActiveTab(hash)
  }, [])

  const handleTabChange = (tab: TabId) => { setActiveTab(tab); window.location.hash = tab }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'projects', label: 'Projects' },
    { id: 'workers', label: 'Workers' },
    { id: 'tasks', label: 'Tasks' },
    { id: 'reviews', label: 'Reviews' },
    { id: 'ideas', label: 'Ideas' },
    { id: 'apis', label: 'APIs' },
    { id: 'routes', label: 'Routes' },
    { id: 'settings', label: 'Settings' },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <OverviewPanel />
      case 'projects': return <ProjectsPanel />
      case 'workers': return <WorkersPanel />
      case 'tasks': return <TasksPanel />
      case 'reviews': return <ReviewsPanel />
      case 'ideas': return <IdeasPanel ideas={demoIdeas} />
      case 'apis': return <APIsPanel apis={demoAPIs} />
      case 'routes': return <RoutesPanel routes={demoRoutes} />
      case 'settings': return <SettingsPanel />
      default: return <OverviewPanel />
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f9fafb' }}>
      <aside style={{ width: '220px', background: 'white', borderRight: '1px solid #e5e7eb', padding: '16px', display: 'flex', flexDirection: 'column' }}>
        <h1 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827' }}>AI Founder OS</h1>
        <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '20px' }}>Dashboard</p>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px', flex: 1 }}>
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => handleTabChange(tab.id as TabId)}
              style={{ padding: '8px 12px', borderRadius: '6px', textAlign: 'left', background: activeTab === tab.id ? '#eff6ff' : 'transparent',
                color: activeTab === tab.id ? '#2563eb' : '#374151', border: 'none', cursor: 'pointer', fontSize: '14px' }}>
              {tab.label}
            </button>
          ))}
        </nav>
        <div style={{ padding: '10px', background: '#f0fdf4', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e' }} />
            <span style={{ fontSize: '12px', color: '#166534' }}>Online v1.0</span>
          </div>
        </div>
      </aside>
      <main style={{ flex: 1, overflow: 'auto', padding: '20px' }}>{renderContent()}</main>
    </div>
  )
}

function OverviewPanel() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>System Overview</h2><p style={{ color: '#6b7280' }}>Monitor your AI engineering organization</p></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        {[
          { label: 'Active Projects', value: '3', color: '#3b82f6' },
          { label: 'Running Workers', value: '2', color: '#22c55e' },
          { label: 'Pending Reviews', value: '2', color: '#eab308' },
          { label: 'Completed Tasks', value: '28', color: '#a855f7' },
        ].map((s) => (
          <div key={s.label} style={{ background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '28px', fontWeight: 'bold', color: s.color }}>{s.value}</div>
            <div style={{ fontSize: '13px', color: '#6b7280' }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ProjectsPanel() {
  const projects = [
    { id: '1', name: 'AI Founder OS', status: 'active', tasks: 12, progress: 75 },
    { id: '2', name: 'Mobile App', status: 'planning', tasks: 5, progress: 20 },
    { id: '3', name: 'API Integration', status: 'active', tasks: 8, progress: 60 },
  ]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>Projects</h2><p style={{ color: '#6b7280' }}>Manage your projects</p></div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none', cursor: 'pointer' }}>+ New Project</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
        {projects.map((p) => (
          <div key={p.id} style={{ background: 'white', padding: '16px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontWeight: '600' }}>{p.name}</span>
              <span style={{ padding: '2px 8px', borderRadius: '10px', fontSize: '11px', background: p.status === 'active' ? '#dcfce7' : '#fef3c7', color: p.status === 'active' ? '#16a34a' : '#d97706' }}>{p.status}</span>
            </div>
            <div style={{ height: '4px', background: '#e5e7eb', borderRadius: '2px' }}>
              <div style={{ height: '100%', width: p.progress + '%', background: '#3b82f6', borderRadius: '2px' }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function WorkersPanel() {
  const workers = [
    { id: 'w1', name: 'Builder-01', type: 'builder', status: 'running', xp: 1250 },
    { id: 'w2', name: 'Researcher-01', type: 'researcher', status: 'idle', xp: 890 },
    { id: 'w3', name: 'Verifier-01', type: 'verifier', status: 'running', xp: 2100 },
    { id: 'w4', name: 'Documenter-01', type: 'documenter', status: 'idle', xp: 560 },
    { id: 'w5', name: 'Evaluator-01', type: 'evaluator', status: 'idle', xp: 720 },
  ]
  const icons: Record<string, string> = { builder: '🔨', researcher: '🔍', verifier: '✅', documenter: '📝', evaluator: '📊' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>Workers</h2><p style={{ color: '#6b7280' }}>Monitor worker status</p></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px' }}>
        {workers.map((w) => (
          <div key={w.id} style={{ background: 'white', padding: '16px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ fontSize: '28px', marginBottom: '8px' }}>{icons[w.type]}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: w.status === 'running' ? '#22c55e' : '#9ca3af' }} />
              <span style={{ fontWeight: '500' }}>{w.name}</span>
            </div>
            <div style={{ fontSize: '12px', color: '#a855f7' }}>XP: {w.xp}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function TasksPanel() {
  const tasks = [
    { id: 't1', title: 'Implement Planner Loop', project: 'AI Founder OS', status: 'completed', priority: 'high' },
    { id: 't2', title: 'Add Worker Registry', project: 'AI Founder OS', status: 'running', priority: 'high' },
    { id: 't3', title: 'Write Tests', project: 'AI Founder OS', status: 'pending', priority: 'medium' },
  ]
  const colors: Record<string, string> = { completed: '#22c55e', running: '#3b82f6', pending: '#eab308', failed: '#ef4444', high: '#ef4444', medium: '#eab308', low: '#22c55e' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>Tasks</h2><p style={{ color: '#6b7280' }}>View all tasks</p></div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none' }}>+ New Task</button>
      </div>
      <div style={{ background: 'white', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Task</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Project</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Priority</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Status</th>
          </tr></thead>
          <tbody>
            {tasks.map((t) => (
              <tr key={t.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px', fontWeight: '500' }}>{t.title}</td>
                <td style={{ padding: '10px 14px', color: '#6b7280' }}>{t.project}</td>
                <td style={{ padding: '10px 14px' }}><span style={{ padding: '2px 8px', borderRadius: '8px', fontSize: '11px', background: colors[t.priority] + '20', color: colors[t.priority] }}>{t.priority}</span></td>
                <td style={{ padding: '10px 14px' }}><span style={{ padding: '2px 8px', borderRadius: '8px', fontSize: '11px', background: colors[t.status] + '20', color: colors[t.status] }}>{t.status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ReviewsPanel() {
  const reviews = [
    { id: 'r1', title: 'Deploy to Production', type: 'deployment', status: 'pending', requester: 'Builder-01', date: '2 min ago' },
    { id: 'r2', title: 'Install New Skill', type: 'skill', status: 'pending', requester: 'System', date: '15 min ago' },
  ]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>Reviews</h2><p style={{ color: '#6b7280' }}>Human-in-the-loop approvals</p></div>
      <div style={{ background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Pending ({reviews.length})</h3>
        {reviews.map((r) => (
          <div key={r.id} style={{ padding: '14px', border: '1px solid #e5e7eb', borderRadius: '8px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: '500', marginBottom: '4px' }}>{r.title}</div>
              <div style={{ fontSize: '13px', color: '#6b7280' }}><span style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px', marginRight: '8px' }}>{r.type}</span>by {r.requester} • {r.date}</div>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button style={{ background: '#ef4444', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer', fontSize: '13px' }}>Reject</button>
              <button style={{ background: '#22c55e', color: 'white', padding: '6px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer', fontSize: '13px' }}>Approve</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function IdeasPanel({ ideas }: { ideas: Idea[] }) {
  const statusColors: Record<string, string> = { new: '#3b82f6', reviewing: '#eab308', approved: '#22c55e', rejected: '#ef4444' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>Ideas</h2><p style={{ color: '#6b7280' }}>Collect and manage inspirations</p></div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none' }}>+ New Idea</button>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
        {ideas.map((idea) => (
          <div key={idea.id} style={{ background: 'white', padding: '16px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontWeight: '600', flex: 1 }}>{idea.title}</span>
              <span style={{ padding: '2px 8px', borderRadius: '8px', fontSize: '11px', background: statusColors[idea.status] + '20', color: statusColors[idea.status] }}>{idea.status}</span>
            </div>
            <p style={{ fontSize: '13px', color: '#6b7280', marginBottom: '8px' }}>{idea.description}</p>
            <div style={{ display: 'flex', gap: '6px', marginBottom: '8px' }}>
              {idea.tags.map((tag, i) => (<span key={i} style={{ background: '#f3f4f6', padding: '2px 8px', borderRadius: '4px', fontSize: '11px' }}>{tag}</span>))}
            </div>
            <div style={{ fontSize: '11px', color: '#9ca3af' }}>Created: {idea.created}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function APIsPanel({ apis }: { apis: APIConnection[] }) {
  const statusColors: Record<string, string> = { connected: '#22c55e', disconnected: '#9ca3af', error: '#ef4444' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>API Connections</h2><p style={{ color: '#6b7280' }}>Manage external services</p></div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none' }}>+ Add API</button>
      </div>
      <div style={{ background: 'white', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Name</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Provider</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Status</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Calls</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Last Used</th>
          </tr></thead>
          <tbody>
            {apis.map((api) => (
              <tr key={api.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px', fontWeight: '500' }}>{api.name}</td>
                <td style={{ padding: '10px 14px', color: '#6b7280' }}>{api.provider}</td>
                <td style={{ padding: '10px 14px' }}><span style={{ padding: '2px 8px', borderRadius: '8px', fontSize: '11px', background: statusColors[api.status] + '20', color: statusColors[api.status] }}>{api.status}</span></td>
                <td style={{ padding: '10px 14px', color: '#6b7280' }}>{api.calls.toLocaleString()}</td>
                <td style={{ padding: '10px 14px', color: '#6b7280', fontSize: '13px' }}>{api.lastUsed}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function RoutesPanel({ routes }: { routes: Route[] }) {
  const methodColors: Record<string, string> = { GET: '#22c55e', POST: '#3b82f6', PUT: '#eab308', DELETE: '#ef4444' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>API Routes</h2><p style={{ color: '#6b7280' }}>Route configuration and management</p></div>
        <button style={{ background: '#2563eb', color: 'white', padding: '8px 16px', borderRadius: '6px', border: 'none' }}>+ Add Route</button>
      </div>
      <div style={{ background: 'white', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Method</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Path</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Handler</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Auth</th>
            <th style={{ padding: '10px 14px', textAlign: 'left', color: '#6b7280', fontSize: '13px' }}>Rate Limit</th>
          </tr></thead>
          <tbody>
            {routes.map((route) => (
              <tr key={route.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '10px 14px' }}><span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '11px', background: methodColors[route.method] + '20', color: methodColors[route.method], fontWeight: '500' }}>{route.method}</span></td>
                <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontSize: '13px' }}>{route.path}</td>
                <td style={{ padding: '10px 14px', color: '#6b7280', fontSize: '13px' }}>{route.handler}</td>
                <td style={{ padding: '10px 14px' }}><span style={{ padding: '2px 8px', borderRadius: '8px', fontSize: '11px', background: route.auth ? '#22c55e20' : '#ef444420', color: route.auth ? '#22c55e' : '#ef4444' }}>{route.auth ? 'Yes' : 'No'}</span></td>
                <td style={{ padding: '10px 14px', color: '#6b7280', fontSize: '13px' }}>{route.rateLimit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function SettingsPanel() {
  const [mode, setMode] = useState('normal')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div><h2 style={{ fontSize: '22px', fontWeight: 'bold' }}>Settings</h2><p style={{ color: '#6b7280' }}>Configure system</p></div>
      <div style={{ background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Execution Mode</h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['safe', 'normal', 'turbo'].map((m) => (
            <button key={m} onClick={() => setMode(m)} style={{ padding: '8px 16px', borderRadius: '6px', border: mode === m ? '2px solid #2563eb' : '2px solid #e5e7eb', background: mode === m ? '#eff6ff' : 'white', color: mode === m ? '#2563eb' : '#374151', cursor: 'pointer', textTransform: 'capitalize' }}>{m}</button>
          ))}
        </div>
      </div>
      <div style={{ background: 'white', padding: '20px', borderRadius: '10px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>System Info</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
          {[['Version', '1.0.0'], ['Python', '3.11+'], ['Workers', '5'], ['API', 'Online']].map(([k, v]) => (
            <div key={k} style={{ padding: '10px', background: '#f9fafb', borderRadius: '6px' }}>
              <div style={{ fontSize: '12px', color: '#6b7280' }}>{k}</div>
              <div style={{ fontWeight: '500' }}>{v}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
