"""
AI Founder OS - Main API Server

FastAPI server providing backend endpoints for the dashboard.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add parent to path for storage and providers modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from storage import Storage, DEFAULT_SOULS

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# ============================================================================
# Data Models
# ============================================================================

class Idea(BaseModel):
    id: str = ""
    title: str
    description: str = ""
    tags: List[str] = []
    priority: str = "P2"
    value_hypothesis: str = ""
    risk_level: str = "medium"
    status: str = "new"
    links: Dict[str, List[str]] = {}
    created_by: str = "human"
    created_at: str = ""
    updated_at: str = ""

    def __init__(self, **data):
        if not data.get("id"):
            data["id"] = f"idea_{uuid.uuid4().hex[:8]}"
        if not data.get("created_at"):
            data["created_at"] = datetime.utcnow().isoformat() + "Z"
        if not data.get("updated_at"):
            data["updated_at"] = data["created_at"]
        super().__init__(**data)


class Project(BaseModel):
    id: str = ""
    name: str
    one_sentence_goal: str = ""
    kpis: List[Dict[str, Any]] = []
    definition_of_done: List[str] = []
    constraints: Dict[str, List[str]] = {}
    operating_mode: str = "normal"
    execution_limits: Dict[str, int] = {}
    routing_policy: Dict[str, Any] = {}
    governance: Dict[str, Any] = {}
    status: str = "active"
    current_bottleneck: str = ""
    next_3_tasks: List[str] = []
    created_by: str = "human"
    created_at: str = ""
    updated_at: str = ""

    def __init__(self, **data):
        if not data.get("id"):
            data["id"] = f"proj_{uuid.uuid4().hex[:8]}"
        if not data.get("created_at"):
            data["created_at"] = datetime.utcnow().isoformat() + "Z"
        if not data.get("updated_at"):
            data["updated_at"] = data["created_at"]
        super().__init__(**data)


class Task(BaseModel):
    id: str = ""
    project_id: str
    title: str
    goal: str = ""
    inputs: Dict[str, Any] = {}
    expected_artifact: Dict[str, Any] = {}
    validators: List[Dict[str, Any]] = []
    risk_level: str = "medium"
    required_capabilities: List[str] = []
    routing_hints: Dict[str, Any] = {}
    state: str = "created"
    retry_count: int = 0
    depends_on: List[str] = []
    created_by: str = "planner"
    assigned_to: Dict[str, Any] = {}
    timestamps: Dict[str, str] = {}

    def __init__(self, **data):
        if not data.get("id"):
            data["id"] = f"task_{uuid.uuid4().hex[:8]}"
        if not data.get("timestamps"):
            now = datetime.utcnow().isoformat() + "Z"
            data["timestamps"] = {
                "created_at": now,
                "updated_at": now
            }
        super().__init__(**data)


class Worker(BaseModel):
    worker_id: str = ""
    worker_type: str
    model_source: str = ""
    capability_tokens: List[str] = []
    xp: Dict[str, int] = {}
    status: str = "idle"
    current_task_id: str = ""
    reputation: Dict[str, float] = {}

    def __init__(self, **data):
        if not data.get("worker_id"):
            data["worker_id"] = f"worker_{data.get('worker_type', 'unknown')}_{uuid.uuid4().hex[:6]}"
        if not data.get("xp"):
            data["xp"] = {"total": 0, "success": 0, "failure": 0, "reused": 0}
        if not data.get("reputation"):
            data["reputation"] = {"score": 1.0, "success_rate": 0.0, "avg_resolution_time": 0}
        super().__init__(**data)


class ReviewCard(BaseModel):
    id: str = ""
    project_id: str = ""
    type: str = ""
    risk_level: str = ""
    context: Dict[str, Any] = {}
    proposal: Dict[str, Any] = {}
    evidence_ids: List[str] = []
    impact_preview: Dict[str, Any] = {}
    status: str = "pending"
    resolution: Optional[Dict[str, Any]] = None
    created_at: str = ""
    updated_at: str = ""

    def __init__(self, **data):
        if not data.get("id"):
            data["id"] = f"gate_{uuid.uuid4().hex[:8]}"
        if not data.get("created_at"):
            data["created_at"] = datetime.utcnow().isoformat() + "Z"
        if not data.get("updated_at"):
            data["updated_at"] = data["created_at"]
        super().__init__(**data)


class Connection(BaseModel):
    connection_id: str = ""
    provider: str
    name: str = ""
    auth_type: str = "api_key"
    credentials: Dict[str, Any] = {}
    scopes: List[str] = []
    quota: Dict[str, Any] = {}
    allowed_workers: List[str] = []
    allowed_projects: List[str] = []
    status: str = "active"
    last_used: str = ""
    health_check: Dict[str, Any] = {}

    def __init__(self, **data):
        if not data.get("connection_id"):
            data["connection_id"] = f"conn_{uuid.uuid4().hex[:8]}"
        super().__init__(**data)


# ============================================================================
# In-Memory Storage
# ============================================================================

class DataStore:
    """In-memory data store for the API"""
    
    def __init__(self):
        self.ideas: Dict[str, Idea] = {}
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.workers: Dict[str, Worker] = {}
        self.review_cards: Dict[str, ReviewCard] = {}
        self.connections: Dict[str, Connection] = {}
        
        # System state
        self.execution_mode: str = "normal"
        self.system_health: str = "healthy"
        self.system_status: str = "running"
        
        # Initialize demo data
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Initialize with demo data"""
        # Demo workers
        for worker_type in ["builder", "researcher", "documenter", "verifier", "evaluator"]:
            worker = Worker(
                worker_type=worker_type,
                model_source=f"local_ollama:{worker_type}-model",
                status="idle"
            )
            self.workers[worker.worker_id] = worker
        
        # Demo projects
        project = Project(
            name="AI Founder OS",
            one_sentence_goal="Build an AI-native operating system for founders",
            status="active"
        )
        self.projects[project.id] = project
        
        # Demo tasks
        task = Task(
            project_id=project.id,
            title="Integrate Backend API",
            goal="Connect frontend to Python backend API",
            state="queued"
        )
        self.tasks[task.id] = task
        
        # Demo review card
        review = ReviewCard(
            project_id=project.id,
            type="task_review",
            risk_level="medium",
            context={"summary": "API integration task ready for review"},
            proposal={"change": "Start API integration work"}
        )
        self.review_cards[review.id] = review


# Global data store
db = DataStore()


# ============================================================================
# FastAPI App
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    yield


app = FastAPI(
    title="AI Founder OS API",
    description="Backend API for AI Founder OS Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - allow all for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Ideas Endpoints
# ============================================================================

@app.get("/api/ideas", response_model=List[Dict])
def list_ideas(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = Query(50, le=100)
) -> List[Dict]:
    """List all ideas with optional filters"""
    ideas = list(db.ideas.values())
    
    if status:
        ideas = [i for i in ideas if i.status == status]
    if priority:
        ideas = [i for i in ideas if i.priority == priority]
    
    return [i.dict() for i in ideas[:limit]]


@app.post("/api/ideas", response_model=Dict)
def create_idea(idea: Idea) -> Dict:
    """Create a new idea"""
    db.ideas[idea.id] = idea
    return idea.dict()


@app.get("/api/ideas/{idea_id}", response_model=Dict)
def get_idea(idea_id: str) -> Dict:
    """Get a specific idea"""
    if idea_id not in db.ideas:
        raise HTTPException(status_code=404, detail="Idea not found")
    return db.ideas[idea_id].dict()


@app.put("/api/ideas/{idea_id}", response_model=Dict)
def update_idea(idea_id: str, idea: Idea) -> Dict:
    """Update an idea"""
    if idea_id not in db.ideas:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.ideas[idea_id] = idea
    return idea.dict()


# ============================================================================
# Projects Endpoints
# ============================================================================

@app.get("/api/projects", response_model=List[Dict])
def list_projects(
    status: Optional[str] = None,
    limit: int = Query(50, le=100)
) -> List[Dict]:
    """List all projects"""
    projects = list(db.projects.values())
    
    if status:
        projects = [p for p in projects if p.status == status]
    
    return [p.dict() for p in projects[:limit]]


@app.post("/api/projects", response_model=Dict)
def create_project(project: Project) -> Dict:
    """Create a new project"""
    db.projects[project.id] = project
    return project.dict()


@app.get("/api/projects/{project_id}", response_model=Dict)
def get_project(project_id: str) -> Dict:
    """Get a specific project"""
    if project_id not in db.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.projects[project_id].dict()


@app.put("/api/projects/{project_id}", response_model=Dict)
def update_project(project_id: str, project: Project) -> Dict:
    """Update a project"""
    if project_id not in db.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    db.projects[project_id] = project
    return project.dict()


# ============================================================================
# Tasks Endpoints
# ============================================================================

@app.get("/api/tasks", response_model=List[Dict])
def list_tasks(
    project_id: Optional[str] = None,
    state: Optional[str] = None,
    limit: int = Query(50, le=100)
) -> List[Dict]:
    """List all tasks"""
    tasks = list(db.tasks.values())
    
    if project_id:
        tasks = [t for t in tasks if t.project_id == project_id]
    if state:
        tasks = [t for t in tasks if t.state == state]
    
    return [t.dict() for t in tasks[:limit]]


@app.post("/api/tasks", response_model=Dict)
def create_task(task: Task) -> Dict:
    """Create a new task"""
    db.tasks[task.id] = task
    return task.dict()


@app.get("/api/tasks/{task_id}", response_model=Dict)
def get_task(task_id: str) -> Dict:
    """Get a specific task"""
    if task_id not in db.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.tasks[task_id].dict()


@app.put("/api/tasks/{task_id}", response_model=Dict)
def update_task(task_id: str, task: Task) -> Dict:
    """Update a task"""
    if task_id not in db.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    db.tasks[task_id] = task
    return task.dict()


# ============================================================================
# Workers Endpoints
# ============================================================================

@app.get("/api/workers", response_model=List[Dict])
def list_workers(
    worker_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict]:
    """List all workers"""
    workers = list(db.workers.values())
    
    if worker_type:
        workers = [w for w in workers if w.worker_type == worker_type]
    if status:
        workers = [w for w in workers if w.status == status]
    
    return [w.dict() for w in workers]


@app.get("/api/workers/{worker_id}", response_model=Dict)
def get_worker(worker_id: str) -> Dict:
    """Get a specific worker"""
    if worker_id not in db.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
    return db.workers[worker_id].dict()


@app.put("/api/workers/{worker_id}", response_model=Dict)
def update_worker(worker_id: str, worker: Worker) -> Dict:
    """Update a worker"""
    if worker_id not in db.workers:
        raise HTTPException(status_code=404, detail="Worker not found")
    db.workers[worker_id] = worker
    return worker.dict()


# ============================================================================
# Review Cards (Human Gate) Endpoints
# ============================================================================

@app.get("/api/reviews", response_model=List[Dict])
def list_reviews(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    gate_type: Optional[str] = None
) -> List[Dict]:
    """List all review cards"""
    reviews = list(db.review_cards.values())
    
    if project_id:
        reviews = [r for r in reviews if r.project_id == project_id]
    if status:
        reviews = [r for r in reviews if r.status == status]
    if gate_type:
        reviews = [r for r in reviews if r.type == gate_type]
    
    return [r.dict() for r in reviews]


@app.post("/api/reviews", response_model=Dict)
def create_review(review: ReviewCard) -> Dict:
    """Create a new review card"""
    db.review_cards[review.id] = review
    return review.dict()


@app.get("/api/reviews/{review_id}", response_model=Dict)
def get_review(review_id: str) -> Dict:
    """Get a specific review card"""
    if review_id not in db.review_cards:
        raise HTTPException(status_code=404, detail="Review card not found")
    return db.review_cards[review_id].dict()


@app.post("/api/reviews/{review_id}/approve", response_model=Dict)
def approve_review(review_id: str, notes: str = "") -> Dict:
    """Approve a review card"""
    if review_id not in db.review_cards:
        raise HTTPException(status_code=404, detail="Review card not found")
    
    review = db.review_cards[review_id]
    review.status = "approved"
    review.resolution = {
        "by": "human",
        "decision": "approved",
        "notes": notes,
        "resolved_at": datetime.utcnow().isoformat() + "Z"
    }
    review.updated_at = datetime.utcnow().isoformat() + "Z"
    
    return review.dict()


@app.post("/api/reviews/{review_id}/reject", response_model=Dict)
def reject_review(review_id: str, notes: str = "") -> Dict:
    """Reject a review card"""
    if review_id not in db.review_cards:
        raise HTTPException(status_code=404, detail="Review card not found")
    
    review = db.review_cards[review_id]
    review.status = "rejected"
    review.resolution = {
        "by": "human",
        "decision": "rejected",
        "notes": notes,
        "resolved_at": datetime.utcnow().isoformat() + "Z"
    }
    review.updated_at = datetime.utcnow().isoformat() + "Z"
    
    return review.dict()


# ============================================================================
# Connections Endpoints
# ============================================================================

@app.get("/api/connections", response_model=List[Dict])
def list_connections(
    provider: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict]:
    """List all connections"""
    connections = list(db.connections.values())
    
    if provider:
        connections = [c for c in connections if c.provider == provider]
    if status:
        connections = [c for c in connections if c.status == status]
    
    return [c.dict() for c in connections]


@app.post("/api/connections", response_model=Dict)
def create_connection(connection: Connection) -> Dict:
    """Create a new connection"""
    db.connections[connection.id] = connection
    return connection.dict()


@app.get("/api/connections/{connection_id}", response_model=Dict)
def get_connection(connection_id: str) -> Dict:
    """Get a specific connection"""
    if connection_id not in db.connections:
        raise HTTPException(status_code=404, detail="Connection not found")
    return db.connections[connection_id].dict()


# ============================================================================
# Providers API - Available AI Providers and Models
# ============================================================================

from connections.providers import PROVIDERS, list_providers

@app.get("/api/providers", response_model=List[Dict])
def get_providers():
    """List all available AI providers"""
    return list_providers()


@app.get("/api/providers/{provider_id}", response_model=Dict)
def get_provider(provider_id: str):
    """Get provider details with models"""
    if provider_id not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")
    return {"id": provider_id, **PROVIDERS[provider_id]}


# ============================================================================
# System Endpoints
# ============================================================================

@app.get("/api/system/status")
def get_system_status() -> Dict:
    """Get system status"""
    return {
        "system_health": db.system_health,
        "system_status": db.system_status,
        "execution_mode": db.execution_mode,
        "stats": {
            "total_ideas": len(db.ideas),
            "active_projects": len([p for p in db.projects.values() if p.status == "active"]),
            "total_tasks": len(db.tasks),
            "pending_tasks": len([t for t in db.tasks.values() if t.state in ["created", "queued"]]),
            "total_workers": len(db.workers),
            "idle_workers": len([w for w in db.workers.values() if w.status == "idle"]),
            "pending_reviews": len([r for r in db.review_cards.values() if r.status == "pending"])
        },
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }


@app.post("/api/system/mode")
def set_execution_mode(mode: str) -> Dict:
    """Set execution mode"""
    valid_modes = ["safe", "normal", "turbo"]
    if mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Invalid mode. Must be one of: {valid_modes}")
    
    db.execution_mode = mode
    return {"execution_mode": mode}


# ============================================================================
# Souls API - Personality Configuration
# ============================================================================

@app.get("/api/souls", response_model=List[Dict])
def list_souls():
    """List all soul configurations"""
    return [{"id": sid, **Storage.load_soul(sid)} for sid in Storage.list_souls()]


@app.get("/api/souls/{soul_id}", response_model=Dict)
def get_soul(soul_id: str):
    """Get a specific soul configuration"""
    soul = Storage.load_soul(soul_id)
    if not soul:
        # Return default if not found
        soul = DEFAULT_SOULS.get(soul_id, {"name": soul_id, "emoji": "🤖", "coreTruths": "", "boundaries": "", "vibe": ""})
    return {"id": soul_id, **soul}


@app.put("/api/souls/{soul_id}", response_model=Dict)
def update_soul(soul_id: str, data: Dict):
    """Update a soul configuration"""
    Storage.save_soul(soul_id, data)
    return {"id": soul_id, **data}


@app.post("/api/souls/{soul_id}/reset", response_model=Dict)
def reset_soul(soul_id: str):
    """Reset a soul to default"""
    default = DEFAULT_SOULS.get(soul_id, {})
    Storage.save_soul(soul_id, default)
    return {"id": soul_id, **default}


# ============================================================================
# Memory API - Daily Logs
# ============================================================================

@app.get("/api/memories", response_model=List[str])
def list_memories():
    """List all memory dates"""
    return Storage.list_memories()


@app.get("/api/memories/{date}", response_model=Dict)
def get_memory(date: str):
    """Get memory for a specific date"""
    content = Storage.load_memory(date)
    return {"date": date, "content": content or ""}


@app.put("/api/memories/{date}", response_model=Dict)
def save_memory(date: str, data: Dict):
    """Save memory for a specific date"""
    Storage.save_memory(date, data.get("content", ""))
    return {"date": date, "saved": True}


# ============================================================================
# Initialize Storage
# ============================================================================

# Initialize default souls on startup
from storage import init_default_souls
init_default_souls()


# ============================================================================
# Vector Memory API - Per-Agent Isolated Memory
# ============================================================================

from memory import MemoryManager, DEFAULT_AGENTS, init_agent_memories

# Initialize memories for all agents
init_agent_memories()


@app.get("/api/memory/agents")
def list_memory_agents():
    """List all agents with memory"""
    return [{"id": agent_id, "name": agent_id.capitalize()} for agent_id in DEFAULT_AGENTS]


@app.get("/api/memory/search")
def search_all_memory(q: str, agents: Optional[str] = None):
    """Search across all agents' memories"""
    agent_list = agents.split(",") if agents else None
    return MemoryManager.search_all(q, agent_list)


@app.get("/api/memory/{agent_id}")
def get_agent_memories(agent_id: str, limit: int = 50):
    """Get all memories for an agent"""
    if agent_id not in DEFAULT_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    memory = MemoryManager.get_memory(agent_id)
    return memory.get_all_memories()[:limit]


@app.post("/api/memory/{agent_id}")
def add_agent_memory(agent_id: str, content: str, metadata: Optional[Dict] = None):
    """Add a memory to an agent"""
    if agent_id not in DEFAULT_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    memory = MemoryManager.get_memory(agent_id)
    memory_id = memory.add_memory(content, metadata)
    return {"id": memory_id, "agent_id": agent_id, "content": content}


@app.get("/api/memory/{agent_id}/search")
def search_agent_memory(agent_id: str, q: str, limit: int = 5):
    """Search memories for an agent"""
    if agent_id not in DEFAULT_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    memory = MemoryManager.get_memory(agent_id)
    return memory.search(q, limit)


@app.delete("/api/memory/{agent_id}/{memory_id}")
def delete_agent_memory(agent_id: str, memory_id: str):
    """Delete a specific memory"""
    if agent_id not in DEFAULT_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    memory = MemoryManager.get_memory(agent_id)
    success = memory.delete_memory(memory_id)
    if not success:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "agent_id": agent_id, "memory_id": memory_id}


@app.delete("/api/memory/{agent_id}")
def clear_agent_memory(agent_id: str):
    """Clear all memories for an agent"""
    if agent_id not in DEFAULT_AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    memory = MemoryManager.get_memory(agent_id)
    memory.clear()
    return {"status": "cleared", "agent_id": agent_id}


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
def health_check() -> Dict:
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# API Keys Management & Model Fetching
# ============================================================================

from api_keys import get_provider_models, DEFAULT_MODELS
import json
from pathlib import Path

# API Keys storage
KEYS_FILE = Path(__file__).parent.parent / "data" / "api_keys.json"

def load_keys() -> Dict:
    """Load API keys from file"""
    if KEYS_FILE.exists():
        try:
            return json.loads(KEYS_FILE.read_text())
        except:
            pass
    return {}

def save_keys(keys: Dict) -> None:
    """Save API keys to file"""
    KEYS_FILE.parent.mkdir(exist_ok=True)
    KEYS_FILE.write_text(json.dumps(keys, indent=2))


@app.get("/api/keys")
def list_api_keys():
    """List saved API key providers (not the keys themselves)"""
    keys = load_keys()
    return {"providers": list(keys.keys())}


@app.post("/api/keys/{provider}")
def save_api_key(provider: str, key: str = ""):
    """Save API key for a provider"""
    keys = load_keys()
    if key:
        keys[provider] = key
    elif provider in keys:
        del keys[provider]
    save_keys(keys)
    return {"provider": provider, "saved": bool(key)}


@app.get("/api/providers")
def list_providers():
    """List all providers with their models"""
    keys = load_keys()
    result = []
    
    all_providers = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "deepseek": "DeepSeek",
        "minimax": "MiniMax",
        "alibaba": "阿里云 (Qwen)",
        "zhipu": "智谱AI",
        "openrouter": "OpenRouter",
        "github": "GitHub Copilot",
        "brave": "Brave Search",
    }
    
    for pid, pname in all_providers.items():
        api_key = keys.get(pid, "")
        models = get_provider_models(pid, api_key if api_key else None)
        result.append({
            "id": pid,
            "name": pname,
            "models": models,
            "has_key": bool(api_key),
        })
    
    return result


@app.get("/api/providers/{provider}")
def get_provider(provider: str):
    """Get a specific provider with models"""
    keys = load_keys()
    api_key = keys.get(provider, "")
    models = get_provider_models(provider, api_key if api_key else None)
    
    names = {
        "openai": "OpenAI", "anthropic": "Anthropic", "deepseek": "DeepSeek",
        "minimax": "MiniMax", "alibaba": "阿里云 (Qwen)", "zhipu": "智谱AI",
        "openrouter": "OpenRouter", "github": "GitHub Copilot", "brave": "Brave Search",
    }
    
    return {
        "id": provider,
        "name": names.get(provider, provider),
        "models": models,
        "has_key": bool(api_key),
    }
