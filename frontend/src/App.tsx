import { useState, useEffect, useRef } from 'react'

interface Idea { id: string; title: string; description: string; tags: string[]; priority: string; status: string; created: string }
interface Project { id: string; name: string; status: string; progress: number; tasks: number; description?: string }
interface Worker { id: string; name: string; type: string; status: string; xp: number }
interface Task { id: string; title: string; project: string; status: string; priority: string }
interface Review { id: string; title: string; type: string; status: string; requester: string }
interface Connection { id: string; name: string; provider: string; model: string; status: string; calls: number }
interface SoulConfig { id: string; name: string; coreTruths: string; boundaries: string; vibe: string; emoji: string }

type TabId = 'overview' | 'projects' | 'workers' | 'tasks' | 'reviews' | 'ideas' | 'apis' | 'routes' | 'console' | 'souls' | 'settings'

const c = { primary: '#7C9A92', bg: '#F5F2ED', surface: '#FFFFFF', text: '#4A4A4A', textLight: '#8A8A8A', success: '#8BA888', warning: '#D4B896', error: '#C49A9A', border: '#E8E4DF', secondary: '#B4A396' }

function App() {
  const [tab, setTab] = useState<TabId>('overview')
  const tabs = [
    {id:'overview',l:'Overview',i:'◈'}, {id:'projects',l:'Projects',i:'◇'}, {id:'workers',l:'Workers',i:'◉'},
    {id:'tasks',l:'Tasks',i:'✓'}, {id:'reviews',l:'Reviews',i:'⚡'}, {id:'ideas',l:'Ideas',i:'💡'},
    {id:'apis',l:'APIs',i:'⚙'}, {id:'routes',l:'Routes',i:'↝'}, {id:'console',l:'Console',i:'▸'},
    {id:'souls',l:'Souls',i:'◇'}, {id:'settings',l:'Settings',i:'⚙'},
  ]
  return (
    <div style={{display:'flex',height:'100vh',background:c.bg,fontFamily:'-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif'}}>
      <aside style={{width:200,background:c.surface,borderRight:`1px solid ${c.border}`,padding:'24px 16px',display:'flex',flexDirection:'column'}}>
        <h1 style={{fontSize:18,fontWeight:600,color:c.text,margin:'0 0 4px 0'}}>AI Founder OS</h1>
        <p style={{fontSize:11,color:c.textLight,margin:'0 0 32px 0'}}>Dashboard</p>
        <nav style={{display:'flex',flexDirection:'column',gap:4,flex:1}}>
          {tabs.map(t => (
            <button key={t.id} onClick={()=>setTab(t.id as TabId)}
              style={{padding:'10px 14px',borderRadius:8,textAlign:'left',background:tab===t.id?c.primary+'20':'transparent',
                color:tab===t.id?c.primary:c.textLight,border:'none',cursor:'pointer',fontSize:13,fontWeight:tab===t.id?500:400,
                display:'flex',alignItems:'center',gap:10,transition:'all 0.2s'}}>
              <span>{t.i}</span>{t.l}
            </button>
          ))}
        </nav>
        <div style={{fontSize:10,color:c.textLight,borderTop:`1px solid ${c.border}`,paddingTop:16}}>v1.0.0 · AI Founder OS</div>
      </aside>
      <main style={{flex:1,overflow:'auto',padding:32}}>
        {tab==='overview'&&<Overview/>} {tab==='projects'&&<Projects/>} {tab==='workers'&&<Workers/>}
        {tab==='tasks'&&<Tasks/>} {tab==='reviews'&&<Reviews/>} {tab==='ideas'&&<Ideas/>}
        {tab==='apis'&&<APIs/>} {tab==='routes'&&<Routes/>} {tab==='console'&&<Console/>}
        {tab==='souls'&&<Souls/>} {tab==='settings'&&<Settings/>}
      </main>
    </div>
  )
}

function Overview() {
  const [s, setS] = useState({p:0,w:0,r:0,t:0,i:0,a:0})
  useEffect(()=>{Promise.all([
    fetch('/api/projects').then(r=>r.json()).then(d=>(d||[]).length).catch(()=>0),
    fetch('/api/workers').then(r=>r.json()).then(d=>(d||[]).length).catch(()=>0),
    fetch('/api/reviews?status=pending').then(r=>r.json()).then(d=>(d||[]).length).catch(()=>0),
    fetch('/api/tasks').then(r=>r.json()).then(d=>(d||[]).length).catch(()=>0),
    fetch('/api/ideas').then(r=>r.json()).then(d=>(d||[]).length).catch(()=>0),
    fetch('/api/connections').then(r=>r.json()).then(d=>(d||[]).length).catch(()=>0),
  ]).then(([p,w,r,t,i,a])=>setS({p,w,r,t,i,a}))},[])
  const cards = [{l:'Projects',v:s.p,i:'◇',col:c.primary},{l:'Workers',v:s.w,i:'◉',col:c.success},{l:'Reviews',v:s.r,i:'⚡',col:c.warning},{l:'Tasks',v:s.t,i:'✓',col:'#9DB4C0'},{l:'Ideas',v:s.i,i:'💡',col:c.error},{l:'APIs',v:s.a,i:'⚙',col:c.secondary}]
  return (
    <div style={{maxWidth:1200,gap:28,display:'flex',flexDirection:'column'}}>
      <h2 style={{fontSize:24,fontWeight:600,color:c.text,margin:0}}>Dashboard</h2>
      <p style={{fontSize:14,color:c.textLight,margin:0}}>Welcome back! Here's your system overview.</p>
      <div style={{display:'grid',gridTemplateColumns:'repeat(6,1fr)',gap:16}}>
        {cards.map(x=>(<div key={x.l} style={{background:c.surface,padding:20,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}>
          <div style={{fontSize:24,marginBottom:12,color:x.col}}>{x.i}</div>
          <div style={{fontSize:28,fontWeight:600,color:c.text}}>{x.v}</div>
          <div style={{fontSize:12,color:c.textLight}}>{x.l}</div>
        </div>))}
      </div>
      <div style={{display:'grid',gridTemplateColumns:'2fr 1fr',gap:20}}>
        <div style={{background:c.surface,padding:24,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}>
          <h3 style={{fontSize:16,fontWeight:600,margin:'0 0 20px 0'}}>Quick Actions</h3>
          {['New Project','New Task','Add Idea','Add API'].map(a=>(<button key={a} style={{width:'100%',padding:12,marginBottom:8,background:c.bg,border:'none',borderRadius:8,textAlign:'left',cursor:'pointer',fontSize:13,color:c.text}}>+ {a}</button>))}
        </div>
        <div style={{background:c.surface,padding:24,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}>
          <h3 style={{fontSize:16,fontWeight:600,margin:'0 0 20px 0'}}>System Status</h3>
          {[{n:'Backend',s:'●'},{n:'API',s:'●'},{n:'Workers',s:'●'}].map(x=>(<div key={x.n} style={{display:'flex',justifyContent:'space-between',padding:'12px 0',borderBottom:`1px solid ${c.border}`}}><span style={{fontSize:13,color:c.text}}>{x.n}</span><span style={{fontSize:13,color:c.success}}>{x.s} Online</span></div>))}
        </div>
      </div>
    </div>
  )
}

function Projects() {
  const [p, setP] = useState<Project[]>([])
  const [show, setShow] = useState(false)
  const [n, setN] = useState({name:'',description:'',status:'active'})
  useEffect(()=>{fetch('/api/projects').then(r=>r.json()).then(d=>setP(d||[])).catch(()=>[])},[])
  const add = async () => {if(!n.name)return;await fetch('/api/projects',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(n)});setP(await fetch('/api/projects').then(r=>r.json()));setShow(false);setN({name:'',description:'',status:'active'})}
  const sc = {active:c.success,paused:c.warning,completed:c.primary,archived:c.textLight}
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>Projects</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Manage your projects</p></div>
        <button onClick={()=>setShow(true)} style={{background:c.primary,color:'white',padding:'12px 20px',borderRadius:8,border:'none',cursor:'pointer',fontSize:13}}>+ New Project</button>
      </div>
      {p.length===0?<div style={{background:c.surface,padding:60,borderRadius:12,textAlign:'center'}}><div style={{fontSize:48,marginBottom:16}}>◇</div><p style={{color:c.textLight}}>No projects yet</p></div>:
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:16}}>{p.map(x=>(<div key={x.id} style={{background:c.surface,padding:20,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}>
          <div style={{display:'flex',justifyContent:'space-between',marginBottom:12}}><h4 style={{fontSize:15,fontWeight:600,margin:0}}>{x.name}</h4><span style={{padding:'4px 10px',borderRadius:20,fontSize:11,background:sc[x.status]||c.textLight,color:'white'}}>{x.status}</span></div>
          {x.description&&<p style={{fontSize:12,color:c.textLight,margin:'0 0 16px 0'}}>{x.description}</p>}
          <div style={{display:'flex',justifyContent:'space-between'}}><span style={{fontSize:12,color:c.textLight}}>{x.tasks||0} tasks</span><div style={{width:100,height:6,background:c.border,borderRadius:3}}><div style={{width:x.progress+'%',height:'100%',background:c.primary,borderRadius:3}}/></div></div>
        </div>))}</div>}
      {show&&<M title="New Project" onClose={()=>setShow(false)} onSave={add} fields={[{l:'Name',v:n.name,onChange:(e:any)=>setN({...n,name:e.target.value})},{l:'Description',v:n.description,onChange:(e:any)=>setN({...n,description:e.target.value}),type:'textarea'}]}/>}
    </div>
  )
}

function Workers() {
  const [w, setW] = useState<Worker[]>([])
  const ic = {builder:'🔨',researcher:'🔍',verifier:'✅',documenter:'📝',evaluator:'📊',planner:'🧠'}
  useEffect(()=>{fetch('/api/workers').then(r=>r.json()).then(d=>setW(d||[])).catch(()=>[])},[])
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>Workers</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Your AI workforce</p></div>
      {w.length===0?<div style={{background:c.surface,padding:60,borderRadius:12,textAlign:'center'}}><div style={{fontSize:48,marginBottom:16}}>◉</div><p style={{color:c.textLight}}>No workers</p></div>:
        <div style={{display:'grid',gridTemplateColumns:'repeat(6,1fr)',gap:16}}>{w.map(x=>(<div key={x.id} style={{background:c.surface,padding:24,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`,textAlign:'center'}}>
          <div style={{fontSize:36,marginBottom:12}}>{ic[x.type]||'🤖'}</div>
          <div style={{fontWeight:600,marginBottom:4}}>{x.name}</div>
          <div style={{fontSize:11,color:c.textLight,marginBottom:12}}>{x.type}</div>
          <div style={{width:8,height:8,borderRadius:'50%',background:x.status==='running'?c.success:c.textLight,margin:'0 auto'}}/>
        </div>))}</div>}
    </div>
  )
}

function Tasks() {
  const [t, setT] = useState<Task[]>([])
  const [show, setShow] = useState(false)
  const [n, setN] = useState({title:'',project:'',priority:'medium'})
  useEffect(()=>{fetch('/api/tasks').then(r=>r.json()).then(d=>setT(d||[])).catch(()=>[])},[])
  const add = async () => {if(!n.title)return;await fetch('/api/tasks',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(n)});setT(await fetch('/api/tasks').then(r=>r.json()));setShow(false);setN({title:'',project:'',priority:'medium'})}
  const sc = {completed:c.success,running:c.primary,pending:c.warning,failed:c.error,high:c.error,medium:c.warning,low:c.textLight}
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>Tasks</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Track your tasks</p></div>
        <button onClick={()=>setShow(true)} style={{background:c.primary,color:'white',padding:'12px 20px',borderRadius:8,border:'none',cursor:'pointer',fontSize:13}}>+ New Task</button>
      </div>
      <div style={{background:c.surface,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`,overflow:'hidden'}}>
        <table style={{width:'100%',borderCollapse:'collapse'}}>
          <thead><tr style={{background:c.bg}}><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Task</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Project</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Priority</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Status</th></tr></thead>
          <tbody>{t.length===0?<tr><td colSpan={4} style={{padding:40,textAlign:'center',color:c.textLight}}>No tasks yet</td></tr>:t.map(x=>(<tr key={x.id} style={{borderTop:`1px solid ${c.border}`}}><td style={{padding:'14px 20px',fontWeight:500,fontSize:13}}>{x.title}</td><td style={{padding:'14px 20px',fontSize:13,color:c.textLight}}>{x.project||'-'}</td><td style={{padding:'14px 20px'}}><span style={{padding:'4px 10px',borderRadius:20,fontSize:11,background:sc[x.priority]||c.textLight,color:'white'}}>{x.priority}</span></td><td style={{padding:'14px 20px'}}><span style={{padding:'4px 10px',borderRadius:20,fontSize:11,background:sc[x.status]||c.textLight,color:'white'}}>{x.status}</span></td></tr>))}</tbody>
        </table>
      </div>
      {show&&<M title="New Task" onClose={()=>setShow(false)} onSave={add} fields={[{l:'Title',v:n.title,onChange:(e:any)=>setN({...n,title:e.target.value})},{l:'Project',v:n.project,onChange:(e:any)=>setN({...n,project:e.target.value})},{l:'Priority',v:n.priority,onChange:(e:any)=>setN({...n,priority:e.target.value}),type:'select',options:['low','medium','high']}]}/>}
    </div>
  )
}

function Reviews() {
  const [r, setR] = useState<Review[]>([])
  useEffect(()=>{fetch('/api/reviews').then(r=>r.json()).then(d=>setR(d||[])).catch(()=>[])},[])
  const app = async (id:string) => {await fetch(`/api/reviews/${id}/approve`,{method:'POST'});setR(r.map(x=>x.id===id?{...x,status:'approved'}:x))}
  const rej = async (id:string) => {await fetch(`/api/reviews/${id}/reject`,{method:'POST'});setR(r.map(x=>x.id===id?{...x,status:'rejected'}:x))}
  const p = r.filter(x=>x.status==='pending'), h = r.filter(x=>x.status!=='pending')
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>Reviews</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Pending approvals</p></div>
      <div style={{background:c.surface,padding:24,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}>
        <h3 style={{fontSize:16,fontWeight:600,margin:'0 0 16px 0'}}>Pending ({p.length})</h3>
        {p.length===0?<p style={{color:c.textLight,textAlign:'center',padding:20}}>No pending reviews</p>:<div style={{display:'flex',flexDirection:'column',gap:12}}>{p.map(x=>(<div key={x.id} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:16,background:c.bg,borderRadius:8}}><div><div style={{fontWeight:500}}>{x.title}</div><div style={{fontSize:12,color:c.textLight,marginTop:4}}>{x.requester} · {x.type}</div></div><div style={{display:'flex',gap:8}}><button onClick={()=>rej(x.id)} style={{padding:'8px 16px',borderRadius:6,border:'none',background:c.error,color:'white',cursor:'pointer'}}>Reject</button><button onClick={()=>app(x.id)} style={{padding:'8px 16px',borderRadius:6,border:'none',background:c.success,color:'white',cursor:'pointer'}}>Approve</button></div></div>))}</div>}
      </div>
      {h.length>0&&<div style={{background:c.surface,padding:24,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}><h3 style={{fontSize:16,fontWeight:600,margin:'0 0 16px 0'}}>History</h3>{h.map(x=>(<div key={x.id} style={{display:'flex',justifyContent:'space-between',padding:12,borderBottom:`1px solid ${c.border}`}}><span>{x.title}</span><span style={{fontSize:12,padding:'2px 8px',borderRadius:4,background:x.status==='approved'?c.success+'20':c.error+'20',color:x.status==='approved'?c.success:c.error}}>{x.status}</span></div>))}</div>}
    </div>
  )
}

function Ideas() {
  const [i, setI] = useState<Idea[]>([])
  const [show, setShow] = useState(false)
  const [n, setN] = useState({title:'',description:'',tags:'',priority:'medium'})
  useEffect(()=>{fetch('/api/ideas').then(r=>r.json()).then(d=>setI(d||[])).catch(()=>[])},[])
  const add = async () => {if(!n.title)return;await fetch('/api/ideas',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...n,tags:n.tags.split(',').map(t=>t.trim()).filter(Boolean)})});setI(await fetch('/api/ideas').then(r=>r.json()));setShow(false);setN({title:'',description:'',tags:'',priority:'medium'})}
  const sc = {new:c.primary,reviewing:c.warning,approved:c.success,rejected:c.error}
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>Ideas</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Collect and manage ideas</p></div>
        <button onClick={()=>setShow(true)} style={{background:c.secondary,color:'white',padding:'12px 20px',borderRadius:8,border:'none',cursor:'pointer',fontSize:13}}>+ New Idea</button>
      </div>
      {i.length===0?<div style={{background:c.surface,padding:60,borderRadius:12,textAlign:'center'}}><div style={{fontSize:48,marginBottom:16}}>💡</div><p style={{color:c.textLight}}>No ideas yet</p></div>:
        <div style={{display:'grid',gridTemplateColumns:'repeat(3,1fr)',gap:16}}>{i.map(x=>(<div key={x.id} style={{background:c.surface,padding:20,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`}}>
          <div style={{display:'flex',justifyContent:'space-between',marginBottom:12}}><h4 style={{fontSize:14,fontWeight:600,margin:0}}>{x.title}</h4><span style={{padding:'3px 8px',borderRadius:12,fontSize:10,background:sc[x.status]||c.textLight,color:'white'}}>{x.status}</span></div>
          <p style={{fontSize:12,color:c.textLight,margin:'0 0 12px 0'}}>{x.description}</p>
          <div style={{display:'flex',gap:6,flexWrap:'wrap'}}>{x.tags.map((t,k)=><span key={k} style={{padding:'2px 8px',background:c.bg,borderRadius:4,fontSize:10}}>{t}</span>)}</div>
        </div>))}</div>}
      {show&&<M title="New Idea" onClose={()=>setShow(false)} onSave={add} fields={[{l:'Title',v:n.title,onChange:(e:any)=>setN({...n,title:e.target.value})},{l:'Description',v:n.description,onChange:(e:any)=>setN({...n,description:e.target.value}),type:'textarea'},{l:'Tags (comma)',v:n.tags,onChange:(e:any)=>setN({...n,tags:e.target.value})}]}/>}
    </div>
  )
}

function APIs() {
  const [cn, setCn] = useState<Connection[]>([])
  const [pr, setPr] = useState<{id:string,name:string,models:{id:string,name:string}[]}[]}>([])
  const [show, setShow] = useState(false)
  const [n, setN] = useState({name:'',provider:'',model:'',apiKey:''})
  useEffect(()=>{fetch('/api/connections').then(r=>r.json()).then(d=>setCn(d||[])).catch(()=>[]);fetch('/api/providers').then(r=>r.json()).then(d=>setPr(d||[])).catch(()=>[])},[])
  const sp = pr.find(p=>p.id===n.provider)
  const add = async () => {if(!n.name||!n.provider)return;await fetch('/api/connections',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n.name,provider:n.provider,model:n.model,api_key:n.apiKey})});setCn(await fetch('/api/connections').then(r=>r.json()));setShow(false);setN({name:'',provider:'',model:'',apiKey:''})}
  const sc = {connected:c.success,disconnected:c.textLight,error:c.error}
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>API Connections</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Manage your API integrations</p></div>
        <button onClick={()=>setShow(true)} style={{background:c.primary,color:'white',padding:'12px 20px',borderRadius:8,border:'none',cursor:'pointer',fontSize:13}}>+ Add API</button>
      </div>
      {cn.length===0?<div style={{background:c.surface,padding:60,borderRadius:12,textAlign:'center'}}><div style={{fontSize:48,marginBottom:16}}>⚙</div><p style={{color:c.textLight}}>No connections</p></div>:
        <div style={{background:c.surface,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`,overflow:'hidden'}}>
          <table style={{width:'100%',borderCollapse:'collapse'}}>
            <thead><tr style={{background:c.bg}}><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Name</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Provider</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Model</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Status</th></tr></thead>
            <tbody>{cn.map(x=>(<tr key={x.id} style={{borderTop:`1px solid ${c.border}`}}><td style={{padding:'14px 20px',fontWeight:500}}>{x.name}</td><td style={{padding:'14px 20px',color:c.textLight}}>{pr.find(p=>p.id===x.provider)?.name||x.provider}</td><td style={{padding:'14px 20px',color:c.textLight}}>{x.model||'-'}</td><td style={{padding:'14px 20px'}}><span style={{padding:'4px 10px',borderRadius:20,fontSize:11,background:sc[x.status]||c.textLight,color:'white'}}>{x.status}</span></td></tr>))}</tbody>
          </table>
        </div>}
      {show&&<div style={{position:'fixed',top:0,left:0,right:0,bottom:0,background:'rgba(0,0,0,0.4)',display:'flex',alignItems:'center',justifyContent:'center',zIndex:100}}>
        <div style={{background:c.surface,padding:32,borderRadius:16,width:420,boxShadow:'0 20px 60px rgba(0,0,0,0.2)'}}>
          <h3 style={{fontSize:18,fontWeight:600,margin:'0 0 24px 0'}}>Add API Connection</h3>
          <div style={{marginBottom:16}}><label style={{display:'block',fontSize:12,marginBottom:6}}>Name</label><input value={n.name} onChange={e=>setN({...n,name:e.target.value})} style={{width:'100%',padding:12,border:`1px solid ${c.border}`,borderRadius:8,fontSize:14}} placeholder="My API"/></div>
          <div style={{marginBottom:16}}><label style={{display:'block',fontSize:12,marginBottom:6}}>Provider</label><select value={n.provider} onChange={e=>setN({...n,provider:e.target.value,model:''})} style={{width:'100%',padding:12,border:`1px solid ${c.border}`,borderRadius:8,fontSize:14}}><option value="">Select provider</option>{pr.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></div>
          {sp&&sp.models.length>0&&<div style={{marginBottom:16}}><label style={{display:'block',fontSize:12,marginBottom:6}}>Model</label><select value={n.model} onChange={e=>setN({...n,model:e.target.value})} style={{width:'100%',padding:12,border:`1px solid ${c.border}`,borderRadius:8,fontSize:14}}><option value="">Select model</option>{sp.models.map(m=><option key={m.id} value={m.id}>{m.name}</option>)}</select></div>}
          <div style={{marginBottom:24}}><label style={{display:'block',fontSize:12,marginBottom:6}}>API Key</label><input type="password" value={n.apiKey} onChange={e=>setN({...n,apiKey:e.target.value})} style={{width:'100%',padding:12,border:`1px solid ${c.border}`,borderRadius:8,fontSize:14}} placeholder="sk-..."/></div>
          <div style={{display:'flex',gap:12,justifyContent:'flex-end'}}><button onClick={()=>setShow(false)} style={{padding:'12px 20px',borderRadius:8,border:`1px solid ${c.border}`,background:c.surface,cursor:'pointer'}}>Cancel</button><button onClick={add} style={{padding:'12px 20px',borderRadius:8,border:'none',background:c.primary,color:'white',cursor:'pointer'}}>Add</button></div>
        </div>
      </div>}
    </div>
  )
}

function Routes() {
  const rt = [{m:'GET',p:'/api/projects',h:'list_projects'},{m:'POST',p:'/api/projects',h:'create_project'},{m:'GET',p:'/api/tasks',h:'list_tasks'},{m:'GET',p:'/api/workers',h:'list_workers'},{m:'GET',p:'/api/reviews',h:'list_reviews'},{m:'GET',p:'/api/ideas',h:'list_ideas'},{m:'GET',p:'/api/connections',h:'list_connections'},{m:'GET',p:'/api/providers',h:'list_providers'},{m:'GET',p:'/api/souls',h:'list_souls'},{m:'GET',p:'/health',h:'health_check'}]
  const mc = {GET:c.success,POST:c.primary,PUT:c.warning,DELETE:c.error}
  return (
    <div style={{maxWidth:1200,gap:24,display:'flex',flexDirection:'column'}}>
      <div><h2 style={{fontSize:24,fontWeight:600,margin:0}}>API Routes</h2><p style={{fontSize:14,color:c.textLight,margin:0}}>Available endpoints</p></div>
      <div style={{background:c.surface,borderRadius:12,boxShadow:`0 2px 8px ${c.border}`,overflow:'hidden'}}>
        <table style={{width:'100%',borderCollapse:'collapse'}}>
          <thead><tr style={{background:c.bg}}><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Method</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Path</th><th style={{padding:'14px 20px',textAlign:'left',fontSize:12,color:c.textLight,fontWeight:500}}>Handler</th></tr></thead>
          <tbody>{rt.map((x,i)=><tr key={i} style={{borderTop:`1px solid ${c.border}`}}><td style={{padding:'14px 20px'}}><span style={{padding:'4px 10px',borderRadius:4,fontSize:11,background:mc[x.m]||c.textLight,color:'white',fontWeight:500}}>{x.m}</span></td><td style={{padding:'14px 20px',fontFamily:'monospace',fontSize:13}}>{x.p}</td><td style={{padding:'14px 20px',color:c.textLight,fontSize:13}}>{x.h}</td></tr>)}</tbody>
        </table>
      </div>
    </div>
  )
}

function Console() {
  const [ms, setMs] = useState([{r:'assistant',c:'Hello! I am your AI Planner.\n\nCommands:\n• "status"\n• "list tasks"\n• "help"\n\nHow can I help?'}])
  const [i, setI] = useState(''