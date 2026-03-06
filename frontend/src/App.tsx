import { useState, useEffect, useRef } from 'react'

// Types
interface Idea { id: string; title: string; description: string; tags: string[]; priority: string; status: string; created: string }
interface Project { id: string; name: string; status: string; progress: number; tasks: number }
interface Worker { id: string; name: string; type: string; status: string; xp: number }
interface Task { id: string; title: string; project: string; status: string; priority: string }
interface Review { id: string; title: string; type: string; status: string; requester: string }
interface Connection { id: string; name: string; provider: string; status: string; calls: number }
interface SoulConfig { id: string; name: string; coreTruths: string; boundaries: string; vibe: string; emoji: string }

const API_BASE = '' // Empty means relative to current origin

const defaultSouls: SoulConfig[] = [
  { id: 'planner', name: 'Planner', emoji: '🧠', coreTruths: 'Be genuinely helpful. Have opinions. Be resourceful before asking.', boundaries: 'Private things stay private. When in doubt, ask.', vibe: 'Concise when needed, thorough when it matters.' },
  { id: 'builder', name: 'Builder', emoji: '🔨', coreTruths: 'Write clean code. Prioritize simplicity. Test everything.', boundaries: 'Never commit secrets. Validate inputs.', vibe: 'Get it done, get it right.' },
  { id: 'researcher', name: 'Researcher', emoji: '🔍', coreTruths: 'Find the truth. Verify sources. Stay objective.', boundaries: 'Cite sources. Don\'t make things up.', vibe: 'Thorough, accurate, skeptical.' },
  { id: 'verifier', name: 'Verifier', emoji: '✅', coreTruths: 'Test rigor prevents bugs. Challenge assumptions.', boundaries: 'Don\'t approve weak code. Be firm.', vibe: 'Quality over speed.' },
  { id: 'documenter', name: 'Documenter', emoji: '📝', coreTruths: 'Clear documentation saves time. Write for humans.', boundaries: 'Keep docs in sync. Less is more.', vibe: 'Clarity is king.' },
  { id: 'evaluator', name: 'Evaluator', emoji: '📊', coreTruths: 'Data drives decisions. Measure what matters.', boundaries: 'Don\'t manipulate metrics. Report honestly.', vibe: 'Objective, metrics-driven.' },
]

type TabId = 'overview' | 'projects' | 'workers' | 'tasks' | 'reviews' | 'ideas' | 'apis' | 'routes' | 'console' | 'souls' | 'settings'

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview')
  const tabs = [
    { id: 'overview', label: 'Overview' }, { id: 'projects', label: 'Projects' }, { id: 'workers', label: 'Workers' },
    { id: 'tasks', label: 'Tasks' }, { id: 'reviews', label: 'Reviews' }, { id: 'ideas', label: 'Ideas' },
    { id: 'apis', label: 'APIs' }, { id: 'routes', label: 'Routes' }, { id: 'console', label: 'Console' },
    { id: 'souls', label: 'Souls' }, { id: 'settings', label: 'Settings' },
  ]

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <OverviewPanel />
      case 'projects': return <ProjectsPanel />
      case 'workers': return <WorkersPanel />
      case 'tasks': return <TasksPanel />
      case 'reviews': return <ReviewsPanel />
      case 'ideas': return <IdeasPanel />
      case 'apis': return <APIsPanel />
      case 'routes': return <RoutesPanel />
      case 'console': return <ConsolePanel />
      case 'souls': return <SoulsPanel />
      case 'settings': return <SettingsPanel />
      default: return <OverviewPanel />
    }
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#f9fafb' }}>
      <aside style={{ width: '180px', background: 'white', borderRight: '1px solid #e5e7eb', padding: '12px' }}>
        <h1 style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '2px' }}>AI Founder OS</h1>
        <p style={{ fontSize: '10px', color: '#6b7280', marginBottom: '12px' }}>Dashboard</p>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id as TabId)}
              style={{ padding: '8px 10px', borderRadius: '4px', textAlign: 'left', background: activeTab === tab.id ? '#2563eb' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#374151', border: 'none', cursor: 'pointer', fontSize: '12px' }}>{tab.label}</button>
          ))}
        </nav>
      </aside>
      <main style={{ flex: 1, overflow: 'auto', padding: '12px' }}>{renderContent()}</main>
    </div>
  )
}

function OverviewPanel() {
  const [stats, setStats] = useState({ projects: 0, workers: 0, reviews: 0, tasks: 0 })
  
  useEffect(() => {
    Promise.all([
      fetch('/api/projects').then(r => r.json()).then(d => d.length).catch(() => 0),
      fetch('/api/workers').then(r => r.json()).then(d => d.length).catch(() => 0),
      fetch('/api/reviews?status=pending').then(r => r.json()).then(d => d.length).catch(() => 0),
      fetch('/api/tasks').then(r => r.json()).then(d => d.filter((t: any) => t.status === 'completed').length).catch(() => 0),
    ]).then(([p, w, r, t]) => setStats({ projects: p, workers: w, reviews: r, tasks: t }))
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>System Overview</h2></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        {[{ label: 'Projects', value: stats.projects, color: '#3b82f6' }, { label: 'Workers', value: stats.workers, color: '#22c55e' }, { label: 'Reviews', value: stats.reviews, color: '#eab308' }, { label: 'Completed', value: stats.tasks, color: '#a855f7' }].map((s) => (
          <div key={s.label} style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
            <div style={{ fontSize: '20px', fontWeight: 'bold', color: s.color }}>{s.value}</div>
            <div style={{ fontSize: '11px', color: '#6b7280' }}>{s.label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ProjectsPanel() {
  const [projects, setProjects] = useState<Project[]>([])

  useEffect(() => { fetch('/api/projects').then(r => r.json()).then(setProjects).catch(() => setProjects([])) }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Projects</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ New</button></div>
      {projects.length === 0 ? <p style={{ color: '#6b7280', fontSize: '12px' }}>No projects yet. Create your first project!</p> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          {projects.map((p) => (
            <div key={p.id} style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}><span style={{ fontWeight: '600' }}>{p.name}</span><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: '#dcfce7', color: '#16a34a' }}>{p.status}</span></div>
              <div style={{ height: '4px', background: '#e5e7eb', borderRadius: '2px' }}><div style={{ height: '100%', width: p.progress + '%', background: '#3b82f6', borderRadius: '2px' }} /></div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function WorkersPanel() {
  const [workers, setWorkers] = useState<Worker[]>([])
  const icons: Record<string, string> = { builder: '🔨', researcher: '🔍', verifier: '✅', documenter: '📝', evaluator: '📊', planner: '🧠' }

  useEffect(() => { fetch('/api/workers').then(r => r.json()).then(setWorkers).catch(() => setWorkers([])) }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Workers</h2>
      {workers.length === 0 ? <p style={{ color: '#6b7280', fontSize: '12px' }}>No workers active. Start a task to activate workers!</p> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
          {workers.map((w) => (
            <div key={w.id} style={{ background: 'white', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px' }}>{icons[w.type] || '🤖'}</div>
              <div style={{ fontWeight: '500', fontSize: '12px', marginTop: '4px' }}>{w.name}</div>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: w.status === 'running' ? '#22c55e' : '#9ca3af', margin: '4px auto 0' }} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function TasksPanel() {
  const [tasks, setTasks] = useState<Task[]>([])
  const colors: Record<string, string> = { completed: '#22c55e', running: '#3b82f6', pending: '#eab308', failed: '#ef4444', high: '#ef4444', medium: '#eab308' }

  useEffect(() => { fetch('/api/tasks').then(r => r.json()).then(setTasks).catch(() => setTasks([])) }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Tasks</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ New</button></div>
      {tasks.length === 0 ? <p style={{ color: '#6b7280', fontSize: '12px' }}>No tasks yet.</p> : (
        <div style={{ background: 'white', borderRadius: '6px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
              <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Task</th>
              <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Priority</th>
              <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Status</th>
            </tr></thead>
            <tbody>
              {tasks.slice(0, 10).map((t) => (<tr key={t.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '6px 10px', fontWeight: '500', fontSize: '12px' }}>{t.title}</td>
                <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: (colors[t.priority] || '#9ca3af') + '20', color: colors[t.priority] || '#9ca3af' }}>{t.priority}</span></td>
                <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: (colors[t.status] || '#9ca3af') + '20', color: colors[t.status] || '#9ca3af' }}>{t.status}</span></td>
              </tr>))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function ReviewsPanel() {
  const [reviews, setReviews] = useState<Review[]>([])

  useEffect(() => { fetch('/api/reviews').then(r => r.json()).then(setReviews).catch(() => setReviews([])) }, [])

  const handleApprove = async (id: string) => {
    await fetch(`/api/reviews/${id}/approve`, { method: 'POST' })
    setReviews(reviews.map(r => r.id === id ? { ...r, status: 'approved' } : r))
  }

  const handleReject = async (id: string) => {
    await fetch(`/api/reviews/${id}/reject`, { method: 'POST' })
    setReviews(reviews.map(r => r.id === id ? { ...r, status: 'rejected' } : r))
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Reviews</h2>
      {reviews.length === 0 ? <p style={{ color: '#6b7280', fontSize: '12px' }}>No pending reviews.</p> : (
        <div style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
          {reviews.filter(r => r.status === 'pending').map((r) => (
            <div key={r.id} style={{ padding: '10px', border: '1px solid #e5e7eb', borderRadius: '4px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div><div style={{ fontWeight: '500', fontSize: '13px' }}>{r.title}</div><div style={{ fontSize: '11px', color: '#6b7280' }}>{r.requester}</div></div>
              <div style={{ display: 'flex', gap: '4px' }}><button onClick={() => handleReject(r.id)} style={{ background: '#ef4444', color: 'white', padding: '4px 8px', borderRadius: '4px', border: 'none', fontSize: '11px' }}>Reject</button><button onClick={() => handleApprove(r.id)} style={{ background: '#22c55e', color: 'white', padding: '4px 8px', borderRadius: '4px', border: 'none', fontSize: '11px' }}>Approve</button></div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function IdeasPanel() {
  const [ideas, setIdeas] = useState<Idea[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [newIdea, setNewIdea] = useState({ title: '', description: '', tags: '' })
  
  useEffect(() => { fetch('/api/ideas').then(r => r.json()).then(setIdeas).catch(() => setIdeas([])) }, [])
  
  const handleAdd = async () => {
    if (!newIdea.title) return
    await fetch('/api/ideas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newIdea.title, description: newIdea.description, tags: newIdea.tags.split(',').map(t => t.trim()).filter(Boolean) })
    })
    const res = await fetch('/api/ideas')
    setIdeas(await res.json())
    setShowAdd(false)
    setNewIdea({ title: '', description: '', tags: '' })
  }
  
  const statusColors: Record<string, string> = { new: '#3b82f6', reviewing: '#eab308', approved: '#22c55e' }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Ideas</h2><button onClick={() => setShowAdd(true)} style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ New</button></div>
      {ideas.length === 0 ? <p style={{ color: '#6b7280', fontSize: '12px' }}>No ideas yet.</p> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          {ideas.map((idea) => (<div key={idea.id} style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}><span style={{ fontWeight: '600', fontSize: '13px' }}>{idea.title}</span><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: (statusColors[idea.status] || '#9ca3af') + '20', color: statusColors[idea.status] || '#9ca3af' }}>{idea.status}</span></div>
            <p style={{ fontSize: '11px', color: '#6b7280', marginBottom: '6px' }}>{idea.description}</p>
            <div style={{ display: 'flex', gap: '4px' }}>{idea.tags.map((tag, i) => (<span key={i} style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>{tag}</span>))}</div>
          </div>))}
        </div>
      )}
      
      {showAdd && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '10px', width: '350px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '14px' }}>💡 Add New Idea</h3>
            <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Title</label><input value={newIdea.title} onChange={e => setNewIdea({...newIdea, title: e.target.value})} placeholder="Idea title" style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }} /></div>
            <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Description</label><textarea value={newIdea.description} onChange={e => setNewIdea({...newIdea, description: e.target.value})} placeholder="Describe your idea" rows={3} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px', resize: 'vertical' }} /></div>
            <div style={{ marginBottom: '14px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Tags (comma separated)</label><input value={newIdea.tags} onChange={e => setNewIdea({...newIdea, tags: e.target.value})} placeholder="AI, automation, etc." style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }} /></div>
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}><button onClick={() => setShowAdd(false)} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer' }}>Cancel</button><button onClick={handleAdd} style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>Add</button></div>
          </div>
        </div>
      )}
    </div>
  )
}

function APIsPanel() {
  const [connections, setConnections] = useState<Connection[]>([])
  const [providers, setProviders] = useState<{id: string, name: string, models: {id: string, name: string}[]}[]>([])
  const [showAdd, setShowAdd] = useState(false)
  const [newConn, setNewConn] = useState({ name: '', provider: '', model: '', apiKey: '' })
  
  useEffect(() => { 
    fetch('/api/connections').then(r => r.json()).then(setConnections).catch(() => setConnections([]))
    fetch('/api/providers').then(r => r.json()).then(setProviders).catch(() => setProviders([]))
  }, [])
  
  const selectedProvider = providers.find(p => p.id === newConn.provider)
  
  const handleAdd = async () => {
    if (!newConn.name || !newConn.provider) return
    await fetch('/api/connections', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newConn.name, provider: newConn.provider, model: newConn.model, api_key: newConn.apiKey })
    })
    const res = await fetch('/api/connections')
    setConnections(await res.json())
    setShowAdd(false)
    setNewConn({ name: '', provider: '', model: '', apiKey: '' })
  }
  
  const providerNames: Record<string, string> = { openai: 'OpenAI', anthropic: 'Anthropic', deepseek: 'DeepSeek', minimax: 'MiniMax', alibaba: '阿里百炼', zhipu: '智谱AI', openrouter: 'OpenRouter', github: 'GitHub', brave: 'Brave Search' }
  const statusColors: Record<string, string> = { connected: '#22c55e', disconnected: '#9ca3af', error: '#ef4444' }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>API Connections</h2><button onClick={() => setShowAdd(true)} style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ Add</button></div>
      {connections.length === 0 ? <p style={{ color: '#6b7280', fontSize: '12px' }}>No API connections configured.</p> : (
        <div style={{ background: 'white', borderRadius: '6px', overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Name</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Provider</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Model</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Status</th></tr></thead>
            <tbody>
              {connections.map((c) => (
                <tr key={c.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '6px 10px', fontWeight: '500', fontSize: '12px' }}>{c.name}</td>
                  <td style={{ padding: '6px 10px', color: '#6b7280', fontSize: '12px' }}>{providerNames[c.provider] || c.provider}</td>
                  <td style={{ padding: '6px 10px', color: '#6b7280', fontSize: '12px' }}>{c.model || '-'}</td>
                  <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: (statusColors[c.status] || '#9ca3af') + '20', color: statusColors[c.status] || '#9ca3af' }}>{c.status}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      
      {showAdd && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '10px', width: '380px' }}>
            <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '14px' }}>➕ Add API Connection</h3>
            <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Name</label><input value={newConn.name} onChange={e => setNewConn({...newConn, name: e.target.value})} placeholder="e.g., My OpenAI" style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }} /></div>
            <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Provider</label><select value={newConn.provider} onChange={e => setNewConn({...newConn, provider: e.target.value, model: ''})} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }}><option value="">Select provider</option>{providers.map(p => (<option key={p.id} value={p.id}>{p.name}</option>))}</select></div>
            {selectedProvider && selectedProvider.models.length > 0 && (
              <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>Model</label><select value={newConn.model} onChange={e => setNewConn({...newConn, model: e.target.value})} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }}><option value="">Select model</option>{selectedProvider.models.map(m => (<option key={m.id} value={m.id}>{m.name}</option>))}</select></div>
            )}
            <div style={{ marginBottom: '14px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '500', marginBottom: '4px' }}>API Key</label><input type="password" value={newConn.apiKey} onChange={e => setNewConn({...newConn, apiKey: e.target.value})} placeholder="sk-..." style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '13px' }} /></div>
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}><button onClick={() => setShowAdd(false)} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer' }}>Cancel</button><button onClick={handleAdd} style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>Add</button></div>
          </div>
        </div>
      )}
    </div>
  )
}

function RoutesPanel() {
  const routes = [
    { method: 'GET', path: '/api/projects', handler: 'list_projects' },
    { method: 'POST', path: '/api/projects', handler: 'create_project' },
    { method: 'GET', path: '/api/tasks', handler: 'list_tasks' },
    { method: 'GET', path: '/api/workers', handler: 'list_workers' },
    { method: 'GET', path: '/api/reviews', handler: 'list_reviews' },
    { method: 'GET', path: '/api/ideas', handler: 'list_ideas' },
    { method: 'GET', path: '/api/connections', handler: 'list_connections' },
    { method: 'GET', path: '/health', handler: 'health_check' },
  ]
  const methodColors: Record<string, string> = { GET: '#22c55e', POST: '#3b82f6', PUT: '#eab308', DELETE: '#ef4444' }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>API Routes</h2>
      <div style={{ background: 'white', borderRadius: '6px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Method</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Path</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Handler</th></tr></thead>
          <tbody>{routes.map((r, i) => (<tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}><td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', background: (methodColors[r.method] || '#9ca3af') + '20', color: methodColors[r.method] || '#9ca3af', fontWeight: '500' }}>{r.method}</span></td><td style={{ padding: '6px 10px', fontFamily: 'monospace', fontSize: '11px' }}>{r.path}</td><td style={{ padding: '6px 10px', color: '#6b7280', fontSize: '11px' }}>{r.handler}</td></tr>))}</tbody>
        </table>
      </div>
    </div>
  )
}

function ConsolePanel() {
  const [messages, setMessages] = useState([{ role: 'assistant', content: 'Hello! I am your AI Planner.\n\nCommands:\n• "status"\n• "list tasks"\n• "help"\n\nHow can I help?' }])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const sendMessage = () => {
    if (!input.trim()) return
    setMessages([...messages, { role: 'user', content: input }])
    setTimeout(() => {
      let response = 'Got: "' + input + '"\n\nTry "help"'
      if (input.toLowerCase().includes('status')) response = '📊 Fetching status from API...'
      else if (input.toLowerCase().includes('help')) response = 'Commands:\n• "status"\n• "list tasks"\n• "help"'
      setMessages(prev => [...prev, { role: 'assistant', content: response }])
    }, 500)
    setInput('')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', height: 'calc(100vh - 60px)' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Console</h2>
      <div style={{ flex: 1, background: '#1e1e1e', borderRadius: '8px', padding: '12px', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {messages.map((msg, i) => (<div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}><div style={{ maxWidth: '80%', padding: '8px 12px', borderRadius: '12px', background: msg.role === 'user' ? '#2563eb' : '#2d2d2d', color: 'white', fontSize: '13px', whiteSpace: 'pre-wrap' }}>{msg.content}</div></div>))}
        <div ref={messagesEndRef} /></div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => { if (e.key === 'Enter') sendMessage() }} placeholder="Type command..." style={{ flex: 1, padding: '10px 14px', borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '14px' }} />
        <button onClick={sendMessage} style={{ background: '#2563eb', color: 'white', padding: '10px 20px', borderRadius: '8px', border: 'none', cursor: 'pointer' }}>Send</button>
      </div>
    </div>
  )
}

function SoulsPanel() {
  const [souls, setSouls] = useState<SoulConfig[]>([])
  const [selectedSoul, setSelectedSoul] = useState<SoulConfig | null>(null)
  const [editForm, setEditForm] = useState({ coreTruths: '', boundaries: '', vibe: '', emoji: '' })

  useEffect(() => { fetch('/api/souls').then(r => r.json()).then(setSouls).catch(() => setSouls([])) }, [])

  const openEdit = (soul: SoulConfig) => { setSelectedSoul(soul); setEditForm({ coreTruths: soul.coreTruths, boundaries: soul.boundaries, vibe: soul.vibe, emoji: soul.emoji }) }
  
  const saveSoul = async () => { 
    if (selectedSoul) {
      await fetch(`/api/souls/${selectedSoul.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...editForm, name: selectedSoul.name })
      })
      const res = await fetch('/api/souls')
      setSouls(await res.json())
      alert('Soul saved!')
      setSelectedSoul(null) 
    } 
  }

  const resetSoul = async (id: string) => {
    await fetch(`/api/souls/${id}/reset`, { method: 'POST' })
    const res = await fetch('/api/souls')
    setSouls(await res.json())
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Soul Settings</h2><p style={{ color: '#6b7280', fontSize: '11px' }}>Configure personality for Planner and Workers</p></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        {souls.map((soul) => (<div key={soul.id} onClick={() => openEdit(soul)} style={{ background: 'white', padding: '14px', borderRadius: '6px', cursor: 'pointer' }}>
          <div style={{ fontSize: '24px', marginBottom: '6px' }}>{soul.emoji}</div>
          <div style={{ fontWeight: '600', fontSize: '14px' }}>{soul.name}</div>
          <p style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{soul.coreTruths.slice(0, 40)}...</p>
        </div>))}
      </div>
      {selectedSoul && (<div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
        <div style={{ background: 'white', padding: '20px', borderRadius: '10px', width: '450px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}><h3 style={{ fontSize: '16px', fontWeight: 'bold' }}>{selectedSoul.emoji} {selectedSoul.name} Soul</h3><button onClick={() => setSelectedSoul(null)} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}>×</button></div>
          <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Emoji</label><input value={editForm.emoji} onChange={(e) => setEditForm({...editForm, emoji: e.target.value})} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '14px' }} /></div>
          <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Core Truths</label><textarea value={editForm.coreTruths} onChange={(e) => setEditForm({...editForm, coreTruths: e.target.value})} rows={2} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px', resize: 'vertical' }} /></div>
          <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Boundaries</label><textarea value={editForm.boundaries} onChange={(e) => setEditForm({...editForm, boundaries: e.target.value})} rows={2} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px', resize: 'vertical' }} /></div>
          <div style={{ marginBottom: '14px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Vibe</label><textarea value={editForm.vibe} onChange={(e) => setEditForm({...editForm, vibe: e.target.value})} rows={2} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px', resize: 'vertical' }} /></div>
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}><button onClick={() => setSelectedSoul(null)} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer' }}>Cancel</button><button onClick={saveSoul} style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>Save</button></div>
        </div></div>)}
    </div>
  )
}

function SettingsPanel() {
  const [mode, setMode] = useState('normal')
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Settings</h2>
      <div style={{ background: 'white', padding: '16px', borderRadius: '6px' }}>
        <h3 style={{ fontSize: '14px', marginBottom: '10px' }}>Execution Mode</h3>
        <div style={{ display: 'flex', gap: '6px' }}>{['safe', 'normal', 'turbo'].map((m) => (<button key={m} onClick={() => setMode(m)} style={{ padding: '6px 12px', borderRadius: '4px', border: mode === m ? '2px solid #2563eb' : '2px solid #e5e7eb', background: mode === m ? '#eff6ff' : 'white', color: mode === m ? '#2563eb' : '#374151', cursor: 'pointer', textTransform: 'capitalize', fontSize: '12px' }}>{m}</button>))}</div>
      </div>
    </div>
  )
}
