import { useState, useEffect, useRef } from 'react'

interface SoulConfig { id: string; name: string; coreTruths: string; boundaries: string; vibe: string; emoji: string }

const defaultSouls: SoulConfig[] = [
  { id: 'planner', name: 'Planner', emoji: '🧠', 
    coreTruths: 'Be genuinely helpful. Have opinions. Be resourceful before asking. Earn trust through competence.', 
    boundaries: 'Private things stay private. When in doubt, ask. Never send half-baked replies.',
    vibe: 'Concise when needed, thorough when it matters. Not a corporate drone. Just good.' },
  { id: 'builder', name: 'Builder', emoji: '🔨',
    coreTruths: 'Write clean, working code. Prioritize simplicity over cleverness. Test everything.',
    boundaries: 'Never commit secrets. Always validate inputs. Ask for clarification.',
    vibe: 'Get it done, get it right. Speed matters, correctness more.' },
  { id: 'researcher', name: 'Researcher', emoji: '🔍',
    coreTruths: 'Find the truth. Verify sources. Stay objective.',
    boundaries: 'Cite sources. Don\'t make things up. Distinguish facts from opinions.',
    vibe: 'Thorough, accurate, skeptical of claims without evidence.' },
  { id: 'verifier', name: 'Verifier', emoji: '✅',
    coreTruths: 'Test rigor prevents bugs. If it isn\'t tested, it\'s broken. Challenge assumptions.',
    boundaries: 'Don\'t approve weak code. Document failures clearly. Be firm but helpful.',
    vibe: 'Quality over speed. A good verifier asks hard questions.' },
  { id: 'documenter', name: 'Documenter', emoji: '📝',
    coreTruths: 'Clear documentation saves time. Write for humans. Examples matter.',
    boundaries: 'Don\'t document obvious things. Keep docs in sync. Less is more.',
    vibe: 'Clarity is king. If you can\'t explain simply, you don\'t understand.' },
  { id: 'evaluator', name: 'Evaluator', emoji: '📊',
    coreTruths: 'Data drives decisions. Measure what matters. Correlation isn\'t causation.',
    boundaries: 'Don\'t manipulate metrics. Report honestly even when it hurts.',
    vibe: 'Objective, metrics-driven, always questioning assumptions.' },
]

const demoAPIs = [{ id: 'a1', name: 'OpenAI', provider: 'OpenAI', status: 'connected' as const, lastUsed: '2 min ago', calls: 1250 }]
const demoRoutes = [{ id: 'r1', path: '/api/projects', method: 'GET', handler: 'list_projects', auth: true, rateLimit: '100/min' }]
const demoIdeas = [{ id: 'i1', title: 'AI Agent', description: '代码审查', tags: ['AI'], priority: 'high', status: 'new' as const, created: '2024-03-06' }]

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
      case 'ideas': return <IdeasPanel ideas={demoIdeas} />
      case 'apis': return <APIsPanel apis={demoAPIs} />
      case 'routes': return <RoutesPanel routes={demoRoutes} />
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
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>System Overview</h2></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
        {[{ label: 'Projects', value: '3', color: '#3b82f6' }, { label: 'Workers', value: '5', color: '#22c55e' }, { label: 'Reviews', value: '2', color: '#eab308' }, { label: 'Tasks', value: '28', color: '#a855f7' }].map((s) => (
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
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Projects</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ New</button></div>
      <div style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}><span style={{ fontWeight: '600' }}>AI Founder OS</span><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: '#dcfce7', color: '#16a34a' }}>active</span></div>
        <div style={{ height: '4px', background: '#e5e7eb', borderRadius: '2px' }}><div style={{ height: '100%', width: '75%', background: '#3b82f6', borderRadius: '2px' }} /></div>
      </div>
    </div>
  )
}

function WorkersPanel() {
  const workers = [{ name: 'Builder', type: 'builder', status: 'running' }, { name: 'Researcher', type: 'researcher', status: 'idle' }, { name: 'Verifier', type: 'verifier', status: 'running' }, { name: 'Documenter', type: 'documenter', status: 'idle' }, { name: 'Evaluator', type: 'evaluator', status: 'idle' }]
  const icons: Record<string, string> = { builder: '🔨', researcher: '🔍', verifier: '✅', documenter: '📝', evaluator: '📊' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Workers</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
        {workers.map((w, i) => (
          <div key={i} style={{ background: 'white', padding: '12px', borderRadius: '6px', textAlign: 'center' }}>
            <div style={{ fontSize: '24px' }}>{icons[w.type]}</div>
            <div style={{ fontWeight: '500', fontSize: '12px', marginTop: '4px' }}>{w.name}</div>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: w.status === 'running' ? '#22c55e' : '#9ca3af', margin: '4px auto 0' }} />
          </div>
        ))}
      </div>
    </div>
  )
}

function TasksPanel() {
  const tasks = [{ title: 'Implement Planner', status: 'completed', priority: 'high' }, { title: 'Add Worker Registry', status: 'running', priority: 'high' }]
  const colors: Record<string, string> = { completed: '#22c55e', running: '#3b82f6', high: '#ef4444' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Tasks</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ New</button></div>
      <div style={{ background: 'white', borderRadius: '6px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Task</th>
            <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Priority</th>
            <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Status</th>
          </tr></thead>
          <tbody>
            {tasks.map((t, i) => (<tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
              <td style={{ padding: '6px 10px', fontWeight: '500', fontSize: '12px' }}>{t.title}</td>
              <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: colors[t.priority] + '20', color: colors[t.priority] }}>{t.priority}</span></td>
              <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: colors[t.status] + '20', color: colors[t.status] }}>{t.status}</span></td>
            </tr>))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ReviewsPanel() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Reviews</h2>
      <div style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
        <div style={{ padding: '10px', border: '1px solid #e5e7eb', borderRadius: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div><div style={{ fontWeight: '500', fontSize: '13px' }}>Deploy to Production</div><div style={{ fontSize: '11px', color: '#6b7280' }}>Builder-01</div></div>
          <div style={{ display: 'flex', gap: '4px' }}><button style={{ background: '#ef4444', color: 'white', padding: '4px 8px', borderRadius: '4px', border: 'none', fontSize: '11px' }}>Reject</button><button style={{ background: '#22c55e', color: 'white', padding: '4px 8px', borderRadius: '4px', border: 'none', fontSize: '11px' }}>Approve</button></div>
        </div>
      </div>
    </div>
  )
}

function IdeasPanel({ ideas }: { ideas: { id: string; title: string; description: string; tags: string[]; priority: string; status: string; created: string }[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Ideas</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ New</button></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
        {ideas.map((idea) => (<div key={idea.id} style={{ background: 'white', padding: '12px', borderRadius: '6px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}><span style={{ fontWeight: '600', fontSize: '13px' }}>{idea.title}</span><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: '#3b82f620', color: '#3b82f6' }}>{idea.status}</span></div>
          <p style={{ fontSize: '11px', color: '#6b7280', marginBottom: '6px' }}>{idea.description}</p>
          <div style={{ display: 'flex', gap: '4px' }}>{idea.tags.map((tag, i) => (<span key={i} style={{ background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px', fontSize: '10px' }}>{tag}</span>))}</div>
        </div>))}
      </div>
    </div>
  )
}

function APIsPanel({ apis }: { apis: { id: string; name: string; provider: string; status: string; lastUsed: string; calls: number }[] }) {
  const [selectedAPI, setSelectedAPI] = useState<typeof apis[0] | null>(null)
  const [editForm, setEditForm] = useState({ apiKey: '', status: 'connected' })
  const statusColors: Record<string, string> = { connected: '#22c55e', disconnected: '#9ca3af' }
  const openSettings = (api: typeof apis[0]) => { setSelectedAPI(api); setEditForm({ apiKey: api.apiKey || '', status: api.status }) }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>API Connections</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ Add</button></div>
      <div style={{ background: 'white', borderRadius: '6px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}>
            <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Name</th>
            <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Status</th>
            <th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Actions</th>
          </tr></thead>
          <tbody>
            {apis.map((api) => (<tr key={api.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
              <td style={{ padding: '6px 10px', fontWeight: '500', fontSize: '12px' }}>{api.name}</td>
              <td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '6px', fontSize: '10px', background: statusColors[api.status] + '20', color: statusColors[api.status] }}>{api.status}</span></td>
              <td style={{ padding: '6px 10px' }}><button onClick={() => openSettings(api)} style={{ background: '#f3f4f6', padding: '4px 8px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>⚙️</button></td>
            </tr>))}
          </tbody>
        </table>
      </div>
      {selectedAPI && (<div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
        <div style={{ background: 'white', padding: '20px', borderRadius: '10px', width: '320px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}><h3 style={{ fontSize: '15px', fontWeight: 'bold' }}>⚙️ {selectedAPI.name}</h3><button onClick={() => setSelectedAPI(null)} style={{ background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer' }}>×</button></div>
          <div style={{ marginBottom: '10px' }}><label style={{ display: 'block', fontSize: '11px', fontWeight: '500', marginBottom: '4px' }}>API Key</label><input type="password" value={editForm.apiKey} onChange={(e) => setEditForm({...editForm, apiKey: e.target.value})} style={{ width: '100%', padding: '6px 10px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px' }} /></div>
          <div style={{ marginBottom: '14px' }}><label style={{ display: 'block', fontSize: '11px', fontWeight: '500', marginBottom: '4px' }}>Status</label><select value={editForm.status} onChange={(e) => setEditForm({...editForm, status: e.target.value})} style={{ width: '100%', padding: '6px 10px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px' }}><option value="connected">Connected</option><option value="disconnected">Disconnected</option></select></div>
          <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}><button onClick={() => setSelectedAPI(null)} style={{ padding: '6px 10px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer' }}>Cancel</button><button onClick={() => { alert('Saved!'); setSelectedAPI(null) }} style={{ padding: '6px 10px', borderRadius: '4px', border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>Save</button></div>
        </div></div>)}
    </div>
  )
}

function RoutesPanel({ routes }: { routes: { id: string; path: string; method: string; handler: string; auth: boolean }[] }) {
  const methodColors: Record<string, string> = { GET: '#22c55e', POST: '#3b82f6' }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>API Routes</h2><button style={{ background: '#2563eb', color: 'white', padding: '4px 10px', borderRadius: '4px', border: 'none' }}>+ Add</button></div>
      <div style={{ background: 'white', borderRadius: '6px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead><tr style={{ background: '#f9fafb', borderBottom: '1px solid #e5e7eb' }}><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Method</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Path</th><th style={{ padding: '6px 10px', textAlign: 'left', color: '#6b7280', fontSize: '11px' }}>Handler</th></tr></thead>
          <tbody>
            {routes.map((r) => (<tr key={r.id} style={{ borderBottom: '1px solid #f3f4f6' }}><td style={{ padding: '6px 10px' }}><span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', background: methodColors[r.method] + '20', color: methodColors[r.method], fontWeight: '500' }}>{r.method}</span></td><td style={{ padding: '6px 10px', fontFamily: 'monospace', fontSize: '11px' }}>{r.path}</td><td style={{ padding: '6px 10px', color: '#6b7280', fontSize: '11px' }}>{r.handler}</td></tr>))}
          </tbody>
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
      if (input.toLowerCase().includes('status')) response = '📊 Status:\n• Projects: 3\n• Workers: 5\n• Tasks: 28'
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
  const [souls, setSouls] = useState<SoulConfig[]>(defaultSouls)
  const [selectedSoul, setSelectedSoul] = useState<SoulConfig | null>(null)
  const [editForm, setEditForm] = useState({ coreTruths: '', boundaries: '', vibe: '', emoji: '' })

  const openEdit = (soul: SoulConfig) => { setSelectedSoul(soul); setEditForm({ coreTruths: soul.coreTruths, boundaries: soul.boundaries, vibe: soul.vibe, emoji: soul.emoji }) }
  const saveSoul = () => { if (selectedSoul) { setSouls(souls.map(s => s.id === selectedSoul.id ? { ...s, ...editForm } : s)); alert('Soul saved!'); setSelectedSoul(null) } }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Soul Settings</h2><p style={{ color: '#6b7280', fontSize: '11px' }}>Configure personality for Planner and Workers</p></div></div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        {souls.map((soul) => (
          <div key={soul.id} onClick={() => openEdit(soul)} style={{ background: 'white', padding: '14px', borderRadius: '6px', cursor: 'pointer', border: '2px solid transparent' }}>
            <div style={{ fontSize: '24px', marginBottom: '6px' }}>{soul.emoji}</div>
            <div style={{ fontWeight: '600', fontSize: '14px' }}>{soul.name}</div>
            <p style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{soul.coreTruths.slice(0, 50)}...</p>
          </div>
        ))}
      </div>

      {selectedSoul && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '10px', width: '500px', maxHeight: '80vh', overflow: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}><h3 style={{ fontSize: '16px', fontWeight: 'bold' }}>{selectedSoul.emoji} {selectedSoul.name} Soul</h3><button onClick={() => setSelectedSoul(null)} style={{ background: 'none', border: 'none', fontSize: '20px', cursor: 'pointer' }}>×</button></div>
            
            <div style={{ marginBottom: '12px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Emoji</label><input value={editForm.emoji} onChange={(e) => setEditForm({...editForm, emoji: e.target.value})} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '14px' }} /></div>
            
            <div style={{ marginBottom: '12px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Core Truths</label><textarea value={editForm.coreTruths} onChange={(e) => setEditForm({...editForm, coreTruths: e.target.value})} rows={3} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px', resize: 'vertical' }} /></div>
            
            <div style={{ marginBottom: '12px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Boundaries</label><textarea value={editForm.boundaries} onChange={(e) => setEditForm({...editForm, boundaries: e.target.value})} rows={3} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px', resize: 'vertical' }} /></div>
            
            <div style={{ marginBottom: '14px' }}><label style={{ display: 'block', fontSize: '12px', fontWeight: '600', marginBottom: '4px' }}>Vibe</label><textarea value={editForm.vibe} onChange={(e) => setEditForm({...editForm, vibe: e.target.value})} rows={2} style={{ width: '100%', padding: '8px', border: '1px solid #e5e7eb', borderRadius: '4px', fontSize: '12px', resize: 'vertical' }} /></div>
            
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button onClick={() => { setSouls(souls.map(s => s.id === selectedSoul.id ? defaultSouls.find(d => d.id === s.id)! : s)); setSelectedSoul(null) }} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer', fontSize: '12px' }}>Reset</button>
              <button onClick={() => setSelectedSoul(null)} style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #e5e7eb', background: 'white', cursor: 'pointer' }}>Cancel</button>
              <button onClick={saveSoul} style={{ padding: '8px 12px', borderRadius: '4px', border: 'none', background: '#2563eb', color: 'white', cursor: 'pointer' }}>Save</button>
            </div>
          </div></div>
      )}
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
