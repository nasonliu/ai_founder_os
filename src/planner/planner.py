"""
AI Founder OS - Planner Module

The Planner is the orchestration core of AI Founder OS.
It manages task generation, worker scheduling, and execution flow.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class TaskState(Enum):
    """Task lifecycle states"""
    IDLE = "idle"
    CREATED = "created"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    NEEDS_REVIEW = "needs_review"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    FAILED = "failed"
    CANCELED = "canceled"
    BLOCKED = "blocked"


class TaskRiskLevel(Enum):
    """Task risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class WorkerType(Enum):
    """Worker types"""
    BUILDER = "builder"
    RESEARCHER = "researcher"
    DOCUMENTER = "documenter"
    VERIFIER = "verifier"
    EVALUATOR = "evaluator"


@dataclass
class Task:
    """Task data model"""
    id: str
    project_id: str
    title: str
    goal: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    expected_artifact: Dict[str, Any] = field(default_factory=dict)
    validators: List[Dict[str, Any]] = field(default_factory=list)
    risk_level: str = "low"
    required_capabilities: List[str] = field(default_factory=list)
    routing_hints: Dict[str, str] = field(default_factory=dict)
    state: str = "created"
    retry_count: int = 0
    depends_on: List[str] = field(default_factory=list)
    created_by: str = "planner"
    assigned_to: Optional[Dict[str, str]] = None
    timestamps: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"task_{uuid.uuid4().hex[:8]}"
        if not self.timestamps:
            now = datetime.utcnow().isoformat() + "Z"
            self.timestamps = {
                "created_at": now,
                "updated_at": now
            }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        """Create from dictionary"""
        return cls(**data)
    
    def can_retry(self, max_retries: int = 3) -> bool:
        """Check if task can be retried"""
        return self.state == "failed" and self.retry_count < max_retries
    
    def transition_to(self, new_state: TaskState) -> bool:
        """Transition to new state with validation"""
        valid_transitions = {
            TaskState.CREATED: [TaskState.QUEUED],
            TaskState.QUEUED: [TaskState.ASSIGNED, TaskState.CANCELED],
            TaskState.ASSIGNED: [TaskState.RUNNING, TaskState.IDLE],
            TaskState.RUNNING: [TaskState.VERIFYING, TaskState.NEEDS_REVIEW, 
                              TaskState.FAILED, TaskState.BLOCKED],
            TaskState.VERIFYING: [TaskState.VERIFIED, TaskState.FAILED, TaskState.NEEDS_REVIEW],
            TaskState.NEEDS_REVIEW: [TaskState.QUEUED, TaskState.CANCELED, TaskState.BLOCKED],
            TaskState.FAILED: [TaskState.QUEUED, TaskState.BLOCKED],
            TaskState.VERIFIED: [TaskState.ASSIGNED],
            TaskState.BLOCKED: [TaskState.RUNNING],
        }
        
        current = TaskState(self.state)
        if new_state in valid_transitions.get(current, []):
            self.state = new_state.value
            self.timestamps["updated_at"] = datetime.utcnow().isoformat() + "Z"
            return True
        return False


@dataclass
class Project:
    """Project data model"""
    id: str
    name: str
    one_sentence_goal: str = ""
    kpis: List[Dict] = field(default_factory=list)
    definition_of_done: List[str] = field(default_factory=list)
    constraints: Dict[str, List[str]] = field(default_factory=dict)
    operating_mode: str = "normal"
    execution_limits: Dict[str, int] = field(default_factory=lambda: {
        "max_concurrency": 3, 
        "retry_limit": 3
    })
    routing_policy: Dict[str, Any] = field(default_factory=dict)
    governance: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"
    current_bottleneck: str = ""
    next_3_tasks: List[str] = field(default_factory=list)
    created_by: str = "human"
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            now = datetime.utcnow().isoformat() + "Z"
            self.created_at = now
            self.updated_at = now
    
    def to_dict(self) -> Dict:
        return asdict(self)


class Planner:
    """
    Core Planner orchestration engine.
    
    Responsibilities:
    - Task generation and scheduling
    - Worker assignment
    - Failure handling and slowdown
    - Human gate triggering
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.tasks: Dict[str, Task] = {}
        self.projects: Dict[str, Project] = {}
        self.task_queue: List[str] = []  # Task IDs
        self.max_concurrency = self.config.get("max_concurrency", 3)
        self.retry_limit = self.config.get("retry_limit", 3)
        self.slowdown_triggered = False
        self.consecutive_failures = 0  # Track consecutive failures
        
    def load_tasks(self, tasks_data: List[Dict]) -> None:
        """Load tasks from data"""
        for task_data in tasks_data:
            task = Task.from_dict(task_data)
            self.tasks[task.id] = task
            if task.state == "queued":
                self.task_queue.append(task.id)
    
    def load_projects(self, projects_data: List[Dict]) -> None:
        """Load projects from data"""
        for proj_data in projects_data:
            project = Project(**proj_data)
            self.projects[project.id] = project
    
    def get_next_task(self) -> Optional[Task]:
        """Get next task from queue based on priority"""
        if not self.task_queue:
            return None
        
        # Simple priority: FIFO for now
        # TODO: Add XP-based and dependency-aware scheduling
        task_id = self.task_queue[0]
        return self.tasks.get(task_id)
    
    def assign_task(self, task_id: str, worker_id: str) -> bool:
        """Assign task to a worker"""
        task = self.tasks.get(task_id)
        if not task or task.state not in ["created", "queued"]:
            return False
        
        now = datetime.utcnow().isoformat() + "Z"
        task.assigned_to = {
            "worker_id": worker_id,
            "assigned_at": now
        }
        task.timestamps["started_at"] = now
        task.transition_to(TaskState.ASSIGNED)
        
        # Remove from queue if it was there
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)
        
        return True
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """Mark task as completed"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if success:
            task.state = "verified"
            self.consecutive_failures = 0  # Reset on success
        else:
            task.state = "failed"
            task.retry_count += 1
            self.consecutive_failures += 1  # Track consecutive failures
            
            # Check for auto slowdown
            if self.consecutive_failures >= self.retry_limit:
                self._trigger_slowdown()
        
        task.timestamps["updated_at"] = datetime.utcnow().isoformat() + "Z"
        task.timestamps["ended_at"] = datetime.utcnow().isoformat() + "Z"
        return True
    
    def queue_task(self, task_id: str) -> bool:
        """Add task to execution queue"""
        task = self.tasks.get(task_id)
        if not task or task.state != "created":
            return False
        
        task.transition_to(TaskState.QUEUED)
        self.task_queue.append(task_id)
        return True
    
    def create_task(self, task_data: Dict) -> Task:
        """Create a new task"""
        # Generate ID if not provided
        if "id" not in task_data:
            task_data["id"] = f"task_{uuid.uuid4().hex[:8]}"
        task = Task(**task_data)
        self.tasks[task.id] = task
        return task
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status summary"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        return {
            "id": task.id,
            "title": task.title,
            "state": task.state,
            "retry_count": task.retry_count,
            "assigned_to": task.assigned_to
        }
    
    def get_project_status(self, project_id: str) -> Optional[Dict]:
        """Get project status"""
        project = self.projects.get(project_id)
        if not project:
            return None
        
        project_tasks = [t for t in self.tasks.values() if t.project_id == project_id]
        task_counts = {}
        for task in project_tasks:
            task_counts[task.state] = task_counts.get(task.state, 0) + 1
        
        return {
            "id": project.id,
            "name": project.name,
            "status": project.status,
            "task_counts": task_counts,
            "current_bottleneck": project.current_bottleneck
        }
    
    def get_blockers(self) -> List[Dict]:
        """Get all blocking issues"""
        blockers = []
        for task in self.tasks.values():
            if task.state in ["failed", "blocked"]:
                blockers.append({
                    "task_id": task.id,
                    "title": task.title,
                    "state": task.state,
                    "retry_count": task.retry_count,
                    "project_id": task.project_id
                })
        return blockers
    
    def _trigger_slowdown(self) -> None:
        """Trigger auto slowdown on repeated failures"""
        self.slowdown_triggered = True
        self.max_concurrency = max(1, self.max_concurrency - 1)
    
    def reset_slowdown(self) -> None:
        """Reset slowdown mode"""
        self.slowdown_triggered = False
        self.max_concurrency = self.config.get("max_concurrency", 3)
    
    def get_status_summary(self) -> Dict:
        """Get overall system status"""
        total_tasks = len(self.tasks)
        task_by_state = {}
        for task in self.tasks.values():
            task_by_state[task.state] = task_by_state.get(task.state, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "tasks_by_state": task_by_state,
            "queue_length": len(self.task_queue),
            "max_concurrency": self.max_concurrency,
            "slowdown_triggered": self.slowdown_triggered,
            "total_projects": len(self.projects)
        }
    
    def export_state(self) -> Dict:
        """Export current state for persistence"""
        return {
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "projects": [p.to_dict() for p in self.projects.values()],
            "task_queue": self.task_queue,
            "config": self.config
        }
    
    def import_state(self, state: Dict) -> None:
        """Import state from persistence"""
        self.tasks.clear()
        self.projects.clear()
        
        for task_data in state.get("tasks", []):
            task = Task.from_dict(task_data)
            self.tasks[task.id] = task
        
        for proj_data in state.get("projects", []):
            project = Project(**proj_data)
            self.projects[project.id] = project
        
        self.task_queue = state.get("task_queue", [])
        self.config = state.get("config", {})


def create_planner(config: Optional[Dict] = None) -> Planner:
    """Factory function to create a Planner"""
    return Planner(config)


if __name__ == "__main__":
    # Demo usage
    planner = create_planner({"max_concurrency": 3, "retry_limit": 3})
    
    # Create a project
    project = Project(
        id="proj_001",
        name="AI Founder OS",
        one_sentence_goal="Build an AI-native operating system"
    )
    planner.projects[project.id] = project
    
    # Create a task
    task_data = {
        "id": "task_001",
        "project_id": "proj_001",
        "title": "Implement Planner Loop",
        "goal": "Build the core Planner orchestration engine",
        "risk_level": "high",
        "validators": [
            {
                "id": "val_001",
                "type": "unit_test",
                "command": "pytest tests/",
                "blocking": True
            }
        ]
    }
    task = planner.create_task(task_data)
    planner.queue_task(task.id)
    
    print("Planner initialized!")
    print(f"Status: {planner.get_status_summary()}")
