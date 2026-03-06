import { useState, useEffect, useRef } from 'react'

interface Idea { id: string; title: string; description: string; tags: string[]; priority: string; status: string; created: string }
interface APIConnection { id: string; name: string; provider: string; status: 'connected' | 'disconnected' | 'error'; lastUsed: string; calls: number; apiKey?: string }
interface Route { id: string; path: string; method: string; handler: string; auth: boolean; rateLimit: string }
interface Message { id: string; role: 'user' | 'assistant'; content: string; timestamp: string }

const demoAPIs: APIConnection[] = [
  { id: 'a1', name: 'OpenAI', provider: 'OpenAI', status: 'connected', lastUsed: '2 min ago', calls: 1250, apiKey: 'sk-****abc' },
  { id: 'a2', name: 'Anthropic', provider: 'Anthropic', status: 'connected', lastUsed: '1 hour ago', calls: 890 },
  { id: 'a3', name: 'DeepSeek', provider: 'DeepSeek', status: 'connected', lastUsed: '30 min ago', calls: 2100 },
]
const demoRoutes: Route[] = [
  { id: 'r1', path: '/api/projects', method: 'GET', handler: 'list_projects', auth: true, rateLimit: '100/min' },
  { id: 'r2', path: '/api/tasks', method: 'GET', handler: 'list_tasks', auth: true, rateLimit: '100/min' },
]
const demoIdeas: Idea[] = [
  { id: 'i1', title: 'AI Agent自动代码审查', description: '使用LLM实现代码审查', tags: ['AI'], priority: 'high', status: 'new', created: '2024-03-06' },
]

type TabId = 'overview' | 'projects' | 'workers' | 'tasks' | 'reviews' | 'ideas' | 'apis' | 'routes' | 'console' | 'settings'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')

  useEffect(() => {
    const hash = window.location.hash.slice(1) as TabId
    if (['overview', 'projects', 'workers', 'tasks', 'reviews', 'ideas', 'apis', 'routes', 'console', 'settings'].includes(hash)) setActiveTab(hash)
  }, [])

  const handleTabChange = (tab: TabId) => window.location.hash = tab

  const tabs = [
    { id: 'overview', label: 'Overview' }, { id: 'projects', label: 'Projects' }, { id: 'workers', label: 'Workers' },
    { id: 'tasks', label: 'Tasks' }, { id: 'reviews', label: 'Reviews' }, { id: 'ideas', label: 'Ideas' },
    { id: 'apis', label: 'APIs' }, { id: 'routes', label: 'Routes' }, { id: 'console', label: 'Console' }, { id: 'settings', label: 'Settings' },
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
      case 'console': return <ConsolePanel />
      case 'settings': return <SettingsPanel />
      default: return <OverviewPanel />
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f9fafb' }}>
      <aside style={{ width: '180px', background: 'white', borderRight: '1px solid #e5e7eb', padding: '12px', display: 'flex', flexDirection: 'column' }}>
        <h1 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '2px' }}>AI Founder OS</h1>
        <p style={{ fontSize: '10px', color: '#6b7280', marginBottom: '12px' }}>Dashboard</p>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px', flex: 1 }}>
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => handleTabChange(tab.id as TabId)}
              style={{ padding: '6px 8px', borderRadius: '4px', textAlign: 'left', background: activeTab === tab.id ? '#2563eb' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#374151', border: 'none', cursor: 'pointer', fontSize: '12px' }}>{tab.label}</button>
          ))}
        </nav>
        <div style={{ padding: '6px', background: '#f0fdf4', borderRadius: '4px', border: '1px solid #bbf7d0' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#22c55e' }} />
            <span style={{ fontSize: '10px', color: '#166534' }}>Online</span>
          </div>
        </div>
      </aside>
      <main style={{ flex: 1, overflow: 'auto', padding: '12px' }}>{renderContent()}</main>
    </div>
  )
}

function OverviewPanel() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>System Overview</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Monitor your AI engineering organization</p></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        {[{ label: 'Projects', value: '3', color: '#3b82f6' }, { label: 'Workers', value: '2', color: '#22c55e' }, { label: 'Reviews', value: '2', color: '#eab308' }, { label: 'Tasks', value: '28', color: '#a855f7' }].map((s) => (
          <div key={s.label} style={{ background: 'white', padding: '12px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: s.color }}>{s.value}</div>
            <div style={{ fontSize: '11px', color: '#6b7280' }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ProjectsPanel() {
  const projects = [{ id: '1', name: 'AI Founder OS', status: 'active', progress: 75 }]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Projects</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Manage projects</p></div>
      <button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none', fontSize: '12px' }}>+ New</button></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
        {projects.map((p) => (
          <div key={p.id} style={{ background: 'white', padding: '12px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}><span style={{ fontWeight: '600', fontSize: '13px' }}>{p.name}</span>
            <span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: '#dcfce7', color: '#16a34a' }}>{p.status}</span></div>
            <div style={{ height: '4px', background: '#e5e7eb', borderRadius: '2px' }}><div style={{ height: '100%', width: p.progress + '%', background: '#3b82f6', borderRadius: '2px' }} /></div></div>
        ))}
      </div>
    </div>
  )
}

function WorkersPanel() {
  const workers = [{ id: 'w1', name: 'Builder-01', type: 'builder', status: 'running', xp: 1250 }]
  const icons: Record<string, string> = { builder: '🔨', researcher: '🔍', verifier: '✅', documenter: '📝', evaluator: '📊' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Workers</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Monitor workers</p></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
        {workers.map((w) => (
          <div key={w.id} style={{ background: 'white', padding: '12px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '20px', marginBottom: '4px' }}>{icons[w.type]}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '2px' }}><div style={{ width: '6px', height: '6px', borderRadius: '50%', background: w.status === 'running' ? '#22c55e' : '#9ca3af' }} /><span style={{ fontWeight: '500', fontSize: '12px' }}>{w.name}</span></div>
            <div style={{ fontSize: '10px', color: '#a855f7' }}>XP: {w.xp}</div></div>
        ))}
      </div>
    </div>
  )
}

function TasksPanel() {
  const tasks = [{ id: 't1', title: 'Implement Planner', status: 'completed', priority: 'high' }, { id: 't2', title: 'Add Worker Registry', status: 'running', priority: 'high' }]
  const colors: Record<string, string> = { completed: '#22c55e', running: '#3b82f6', pending: '#eab308', high: '#ef4444', medium: '#eab308' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Tasks</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>View tasks</p></div>
      <button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none', fontSize: '12px' }}>+ New Task</button></div>
      <div style={{ background: 'white', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}><thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Task</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Priority</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Status</th>
        </tr></thead><tbody>
          {tasks.map((t) => (<tr key={t.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
            <td style={{ padding: '6px 10px', fontWeight: '500', fontSize: '12px' }}>{t.title}</td>
            <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: colors[t.priority] + '20', color: colors[t.priority] }}>{t.priority}</span></td>
            <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: colors[t.status] + '20', color: colors[t.status] }}>{t.status}</span></td>
          </tr>))}
        </tbody></table></div>
    </div>
  )
}

function ReviewsPanel() {
  const reviews = [{ id: 'r1', title: 'Deploy to Production', status: 'pending', requester: 'Builder-01' }]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Reviews</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Approval requests</p></div>
      <div style={{ background: 'white', padding: '12px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
        {reviews.map((r) => (<div key={r.id} style={{ padding: '10px', border: '1px solid #e5e7eb', borderRadius: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div><div style={{ fontWeight: '500', fontSize: '13px', marginBottom: '2px' }}>{r.title}</div><div style={{ fontSize: '11px', color: '#6b7280' }}>{r.requester}</div></div>
          <div style={{ display: 'flex', gap: '4px' }}><button style={{ background: '#ef4444', color: 'white', padding: '4px 8px', borderRadius: '4px', border: 'none', fontSize: '11px' }}>Reject</button>
          <button style={{ background: '#22c55e', color: 'white', padding: '4px 8px', borderRadius: '4px', border: 'none', fontSize: '11px' }}>Approve</button></div>
        </div>))}
      </div>
    </div>
  )
}

function IdeasPanel({ ideas }: { ideas: Idea[] }) {
  const statusColors: Record<string, string> = { new: '#3b82f6', reviewing: '#eab308', approved: '#22c55e' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Ideas</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Inspiration collection</p></div>
      <button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none', fontSize: '12px' }}>+ New</button></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
        {ideas.map((idea) => (<div key={idea.id} style={{ background: 'white', padding: '12px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}><span style={{ fontWeight: '600', flex: 1, fontSize: '13px' }}>{idea.title}</span>
          <span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: statusColors[idea.status] + '20', color: statusColors[idea.status] }}>{idea.status}</span></div>
          <p style={{ fontSize: '11px', color: '#6b7280', marginBottom: '6px' }}>{idea.description}</p>
          <div style={{ display: 'flex', gap: '4px' }}>{idea.tags.map((tag, i) => (<span key={i} style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>{tag}</span>))}</div>
        </div>))}
      </div>
    </div>
  )
}

function APIsPanel({ apis }: { apis: APIConnection[] }) {
  const [selectedAPI, setSelectedAPI] = useState<APIConnection | null>(null)
  const [editForm, setEditForm] = useState({ apiKey: '', status: 'connected' })
  const statusColors: Record<string, string> = { connected: '#22c55e', disconnected: '#9ca3af', error: '#ef4444' }

  const openSettings = (api: APIConnection) => { setSelectedAPI(api); setEditForm({ apiKey: api.apiKey || '', status: api.status }) }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>API Connections</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Manage external services</p></div>
      <button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none', fontSize: '12px' }}>+ Add</button></div>
      <div style={{ background: 'white', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}><thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Name</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Status</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Calls</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Actions</th>
        </tr></thead><tbody>
          {apis.map((api) => (<tr key={api.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
            <td style={{ padding: '6px 10px', fontWeight: '500', fontSize: '12px' }}>{api.name}</td>
            <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: statusColors[api.status] + '20', color: statusColors[api.status] }}>{api.status}</span></td>
            <td style={{ padding: '6px 10px', color: '#6b7280', fontSize: '12px' }}>{api.calls.toLocaleString()}</td>
            <td style={{ padding: '6px 10px' }}><button onClick={() => openSettings(api)} style={{ background: '#f3f4f6', padding: '4px 6px', borderRadius: '4px', border: 'none', fontSize: '10px', cursor: 'pointer' }}>⚙️</button></td>
          </tr>))}
        </tbody></table></div>
      {selectedAPI && (<div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
        <div style={{ background: 'white', padding: '20px', borderRadius: '10px', width: '360px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}><h3 style={{ fontSize: '16px', fontWeight: 'bold' }}>⚙️ {selectedAPI.name}</h3>
          <button onClick={() => setSelectedAPI(null)} style={{ background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer' }}>×</button></div>
          <div style={{ marginBottom: '12px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>API Key</label>
          <input type="password" value={editForm.apiKey} onChange={(e) => setEditForm({...editForm, apiKey: e.target.value})} style={{ width: '100%', padding: '6px 10px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }} /></div>
          <div style={{ marginBottom: '16px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Status</label>
          <select value={editForm.status} onChange={(e) => setEditForm({...editForm, status: e.target.value})} style={{ width: '100%', padding: '6px 10px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }}>
            <option value="connected">Connected</option><option value="disconnected">Disconnected</option><option value="error">Error</option></select></div>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
            <button onClick={() => setSelectedAPI(null)} style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer' }}>Cancel</button>
            <button onClick={() => { alert('Saved!'); setSelectedAPI(null) }} style={{ padding: '6px 12px', borderRadius: '4px', border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>Save</button>
          </div></div></div>)}
    </div>
  )
}

function RoutesPanel({ routes }: { routes: Route[] }) {
  const methodColors: Record<string, string> = { GET: '#22c55e', POST: '#3b82f6', PUT: '#eab308', DELETE: '#ef4444' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>API Routes</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Route configuration</p></div>
      <button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none', fontSize: '12px' }}>+ Add</button></div>
      <div style={{ background: 'white', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}><thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Method</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Path</th>
          <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Handler</th>
        </tr></thead><tbody>
          {routes.map((route) => (<tr key={route.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
            <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', background: methodColors[route.method] + '20', color: methodColors[route.method], fontWeight: '500' }}>{route.method}</span></td>
            <td style={{ padding: '6px 10px', fontFamily: 'monospace', fontSize: '11px' }}>{route.path}</td>
            <td style={{ padding: '6px 10px', color: '#6b7280', fontSize: '11px' }}>{route.handler}</td>
          </tr>))}
        </tbody></table></div>
    </div>
  )
}

function ConsolePanel() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hello! I am your AI Planner Assistant.\n\nCommands:\n• "create project MyProject"\n• "list tasks"\n• "add task Build API"\n• "status"\n\nHow can I help?', timestamp: new Date().toISOString() }
  ])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const sendMessage = () => {
    if (!input.trim()) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input, timestamp: new Date().toISOString() }
    setMessages([...messages, userMsg])
    setTimeout(() => {
      let response = ''
      const cmd = input.toLowerCase()
      if (cmd.includes('create project')) response = `✅ Project created: ${input.replace(/create project/i, '').trim()}\nStatus: Active`
      else if (cmd.includes('list tasks') || cmd.includes('show tasks')) response = `📋 Tasks:\n1. Implement Planner - running\n2. Add Worker Registry - pending\n3. Write Tests - pending`
      else if (cmd.includes('add task')) response = `✅ Task added: ${input.replace(/add task/i, '').trim()}\nPriority: medium`
      else if (cmd.includes('status')) response = `📊 Status:\n• Projects: 3\n• Workers: 2\n• Tasks: 28\n• System: Normal`
      else if (cmd.includes('help')) response = `Commands:\n• "create project [name]"\n• "list tasks"\n• "add task [desc]"\n• "status"`
      else response = `Got: "${input}"\n\nTry: "help"`
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'assistant', content: response, timestamp: new Date().toISOString() }])
    }, 500)
    setInput('')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: 'calc(100vh - 60px)' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Console</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Interact with Planner</p></div>
      <div style={{ flex: 1, background: '#1e1e1e', borderRadius: '8px', padding: '12px', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {messages.map((msg) => (<div key={msg.id} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
          <div style={{ maxWidth: '80%', padding: '8px 12px', borderRadius: '12px', background: msg.role === 'user' ? '#2563eb' : '#2d2d2d', color: 'white', fontSize: '13px', whiteSpace: 'pre-wrap' }}>{msg.content}</div></div>))}
        <div ref={messagesEndRef} /></div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => { if (e.key === 'Enter') sendMessage() }}
          placeholder="Type command..." style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }} />
        <button onClick={sendMessage} style={{ background: '#2563eb', color: 'white', padding: '10px 20px', borderRadius: '8px', border: 'none', cursor: 'pointer', fontSize: '14px' }}>Send</button>
      </div>
    </div>
  )
}

function SettingsPanel() {
  const [mode, setMode] = useState('normal')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Settings</h2><p style={{ color: '#6b7280', fontSize: '12px' }}>Configure system</p></div>
      <div style={{ background: 'white', padding: '16px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
        <h3 style={{ fontSize: '14px', marginBottom: '10px' }}>Execution Mode</h3>
        <div style={{ display: 'flex', gap: '6px' }}>{['safe', 'normal', 'turbo'].map((m) => (<button key={m} onClick={() => setMode(m)} style={{ padding: '6px 12px', borderRadius: '4px', border: mode === m ? '2px solid #2563eb' : '2px solid #e5e7eb', background: mode === m ? '#eff6ff' : 'white', color: mode === m ? '#2563eb' : '#374151', cursor: 'pointer', textTransform: 'capitalize', fontSize: '12px' }}>{m}</button>))}</div>
      </div>
    </div>
  )
}
