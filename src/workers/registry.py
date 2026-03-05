"""
Worker Registry Module

Manages AI Worker pool with XP tracking, reputation, and scheduling.
"""
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field


class WorkerType(Enum):
    """Worker type enumeration"""
    BUILDER = "builder"
    RESEARCHER = "researcher"
    DOCUMENTER = "documenter"
    VERIFIER = "verifier"
    EVALUATOR = "evaluator"


class WorkerStatus(Enum):
    """Worker status enumeration"""
    IDLE = "idle"
    ASSIGNED = "assigned"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    PAUSED = "paused"
    ERROR = "error"


# Default capabilities for each worker type
WORKER_CAPABILITIES = {
    WorkerType.BUILDER: ["cap_code", "cap_test", "cap_config"],
    WorkerType.RESEARCHER: ["cap_search", "cap_analysis"],
    WorkerType.DOCUMENTER: ["cap_doc", "cap_prd"],
    WorkerType.VERIFIER: ["cap_test", "cap_review", "cap_validate"],
    WorkerType.EVALUATOR: ["cap_metrics", "cap_benchmark", "cap_analysis"],
}


@dataclass
class XPStats:
    """XP (Experience Points) statistics for a worker"""
    total: int = 0
    success: int = 0
    failure: int = 0
    reused: int = 0

    def calculate_total(self) -> int:
        """Calculate total XP using formula: success * 1 + reused * 2 - failure * 1"""
        return (self.success * 1) + (self.reused * 2) - (self.failure * 1)

    def add_success(self):
        """Add a success (+1 XP)"""
        self.success += 1
        self.total = self.calculate_total()

    def add_reuse(self):
        """Add an experience reuse (+2 XP)"""
        self.reused += 1
        self.total = self.calculate_total()

    def add_failure(self):
        """Add a failure (-1 XP)"""
        self.failure += 1
        self.total = self.calculate_total()

    def to_dict(self) -> Dict[str, int]:
        return {
            "total": self.calculate_total(),
            "success": self.success,
            "failure": self.failure,
            "reused": self.reused
        }


@dataclass
class Reputation:
    """Reputation metrics for a worker"""
    score: float = 1.0
    success_rate: float = 0.0
    avg_resolution_time_minutes: float = 0.0
    total_tasks_completed: int = 0

    def update_from_completion(self, resolution_time_minutes: float, success: bool):
        """Update reputation based on task completion"""
        self.total_tasks_completed += 1
        
        # Update success rate (exponential moving average)
        if success:
            new_rate = 1.0
        else:
            new_rate = 0.0
        
        if self.total_tasks_completed == 1:
            self.success_rate = new_rate
        else:
            # EMA with alpha = 0.1
            self.success_rate = 0.9 * self.success_rate + 0.1 * new_rate
        
        # Update score based on success rate
        self.score = self.success_rate
        
        # Update average resolution time
        if self.total_tasks_completed == 1:
            self.avg_resolution_time_minutes = resolution_time_minutes
        else:
            self.avg_resolution_time_minutes = (
                0.9 * self.avg_resolution_time_minutes + 
                0.1 * resolution_time_minutes
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 3),
            "success_rate": round(self.success_rate, 3),
            "avg_resolution_time_minutes": round(self.avg_resolution_time_minutes, 1),
            "total_tasks_completed": self.total_tasks_completed
        }


@dataclass
class Worker:
    """Worker entity"""
    worker_id: str
    worker_type: str
    model_source: str
    fallback_model: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    xp: XPStats = field(default_factory=XPStats)
    status: str = "idle"
    current_task_id: Optional[str] = None
    reputation: Reputation = field(default_factory=Reputation)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self):
        # Auto-populate capabilities if not provided
        if not self.capabilities:
            worker_type_enum = WorkerType(self.worker_type)
            self.capabilities = WORKER_CAPABILITIES.get(worker_type_enum, [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "worker_type": self.worker_type,
            "model_source": self.model_source,
            "fallback_model": self.fallback_model,
            "capabilities": self.capabilities,
            "xp": self.xp.to_dict(),
            "status": self.status,
            "current_task_id": self.current_task_id,
            "reputation": self.reputation.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Worker':
        """Create Worker from dictionary"""
        xp = XPStats(**data.get("xp", {}))
        reputation = Reputation(**data.get("reputation", {}))
        
        return cls(
            worker_id=data["worker_id"],
            worker_type=data["worker_type"],
            model_source=data["model_source"],
            fallback_model=data.get("fallback_model"),
            capabilities=data.get("capabilities", []),
            xp=xp,
            status=data.get("status", "idle"),
            current_task_id=data.get("current_task_id"),
            reputation=reputation,
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat())
        )


class WorkerRegistry:
    """
    Worker Registry manages the pool of AI Workers.
    
    Responsibilities:
    - Worker registration and lifecycle
    - XP tracking and reputation
    - Worker selection and scheduling
    - Help request handling
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.workers: Dict[str, Worker] = {}
        self.storage_path = storage_path
        self._load_workers()
    
    def _load_workers(self):
        """Load workers from storage if available"""
        if self.storage_path:
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for worker_data in data.get("workers", []):
                        worker = Worker.from_dict(worker_data)
                        self.workers[worker.worker_id] = worker
            except (FileNotFoundError, json.JSONDecodeError):
                pass
    
    def _save_workers(self):
        """Save workers to storage"""
        if self.storage_path:
            data = {
                "workers": [w.to_dict() for w in self.workers.values()]
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def register_worker(
        self,
        worker_type: str,
        model_source: str,
        fallback_model: Optional[str] = None,
        worker_id: Optional[str] = None
    ) -> Worker:
        """
        Register a new worker.
        
        Args:
            worker_type: Type of worker (builder, researcher, documenter, verifier, evaluator)
            model_source: Primary model source (e.g., "local_ollama:deepseek-8b")
            fallback_model: Fallback model source (e.g., "cloud_openai:gpt-4")
            worker_id: Optional custom worker ID
            
        Returns:
            Registered Worker instance
        """
        # Validate worker type
        try:
            WorkerType(worker_type)
        except ValueError:
            raise ValueError(f"Invalid worker type: {worker_type}")
        
        # Generate worker ID if not provided
        if not worker_id:
            worker_id = f"worker_{worker_type}_{uuid.uuid4().hex[:8]}"
        
        worker = Worker(
            worker_id=worker_id,
            worker_type=worker_type,
            model_source=model_source,
            fallback_model=fallback_model,
            status=WorkerStatus.IDLE.value
        )
        
        self.workers[worker_id] = worker
        self._save_workers()
        
        return worker
    
    def get_worker(self, worker_id: str) -> Optional[Worker]:
        """Get worker by ID"""
        return self.workers.get(worker_id)
    
    def list_workers(
        self,
        worker_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Worker]:
        """
        List workers with optional filtering.
        
        Args:
            worker_type: Filter by worker type
            status: Filter by status
            
        Returns:
            List of matching workers
        """
        result = list(self.workers.values())
        
        if worker_type:
            result = [w for w in result if w.worker_type == worker_type]
        
        if status:
            result = [w for w in result if w.status == status]
        
        return result
    
    def get_idle_workers(self, worker_type: Optional[str] = None) -> List[Worker]:
        """Get idle workers, optionally filtered by type"""
        return self.list_workers(worker_type=worker_type, status=WorkerStatus.IDLE.value)
    
    def update_worker_status(
        self,
        worker_id: str,
        status: str,
        task_id: Optional[str] = None
    ) -> bool:
        """
        Update worker status.
        
        Args:
            worker_id: Worker ID
            status: New status
            task_id: Optional task ID to assign
            
        Returns:
            True if updated successfully
        """
        worker = self.workers.get(worker_id)
        if not worker:
            return False
        
        # Validate status
        try:
            WorkerStatus(status)
        except ValueError:
            raise ValueError(f"Invalid status: {status}")
        
        worker.status = status
        worker.current_task_id = task_id
        worker.updated_at = datetime.now(timezone.utc).isoformat()
        
        self._save_workers()
        return True
    
    def assign_task(self, worker_id: str, task_id: str) -> bool:
        """Assign a task to a worker"""
        return self.update_worker_status(worker_id, WorkerStatus.ASSIGNED.value, task_id)
    
    def start_task(self, worker_id: str) -> bool:
        """Mark worker as running a task"""
        return self.update_worker_status(worker_id, WorkerStatus.RUNNING.value)
    
    def complete_task(
        self,
        worker_id: str,
        resolution_time_minutes: float,
        success: bool = True
    ) -> bool:
        """
        Mark task as completed and update XP/reputation.
        
        Args:
            worker_id: Worker ID
            resolution_time_minutes: Time taken to complete
            success: Whether task was successful
            
        Returns:
            True if completed successfully
        """
        worker = self.workers.get(worker_id)
        if not worker:
            return False
        
        # Update XP
        if success:
            worker.xp.add_success()
        else:
            worker.xp.add_failure()
        
        # Update reputation
        worker.reputation.update_from_completion(resolution_time_minutes, success)
        
        # Reset to idle
        worker.status = WorkerStatus.IDLE.value
        worker.current_task_id = None
        worker.updated_at = datetime.now(timezone.utc).isoformat()
        
        self._save_workers()
        return True
    
    def record_experience_reuse(self, worker_id: str) -> bool:
        """
        Record that a worker's experience was reused.
        
        Args:
            worker_id: Worker whose experience was reused
            
        Returns:
            True if recorded successfully
        """
        worker = self.workers.get(worker_id)
        if not worker:
            return False
        
        worker.xp.add_reuse()
        worker.updated_at = datetime.now(timezone.utc).isoformat()
        
        self._save_workers()
        return True
    
    def calculate_priority(
        self,
        worker: Worker,
        task_type_hint: Optional[str] = None
    ) -> float:
        """
        Calculate worker priority for task assignment.
        
        Priority formula:
        Priority = XP + Availability + Success_Rate
        
        Args:
            worker: Worker to calculate priority for
            task_type_hint: Optional task type for matching
            
        Returns:
            Priority score (higher is better)
        """
        priority = worker.xp.total
        
        # Availability bonus
        if worker.status == WorkerStatus.IDLE.value:
            priority += 3
        
        # Success rate bonus
        priority += worker.reputation.success_rate * 10
        
        # Type matching bonus
        if task_type_hint and worker.worker_type == task_type_hint:
            priority += 5
        
        return priority
    
    def select_best_worker(
        self,
        task_type_hint: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None
    ) -> Optional[Worker]:
        """
        Select the best available worker for a task.
        
        Args:
            task_type_hint: Preferred worker type
            required_capabilities: Required capabilities
            
        Returns:
            Best matching worker or None
        """
        idle_workers = self.get_idle_workers()
        
        if not idle_workers:
            return None
        
        # Filter by capabilities if specified
        if required_capabilities:
            idle_workers = [
                w for w in idle_workers
                if all(cap in w.capabilities for cap in required_capabilities)
            ]
        
        if not idle_workers:
            return None
        
        # Score and rank workers
        scored_workers = [
            (w, self.calculate_priority(w, task_type_hint))
            for w in idle_workers
        ]
        
        # Return highest priority worker
        scored_workers.sort(key=lambda x: x[1], reverse=True)
        return scored_workers[0][0]
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get overall worker pool statistics"""
        all_workers = list(self.workers.values())
        
        status_counts = {}
        type_counts = {}
        
        for w in all_workers:
            status_counts[w.status] = status_counts.get(w.status, 0) + 1
            type_counts[w.worker_type] = type_counts.get(w.worker_type, 0) + 1
        
        total_xp = sum(w.xp.total for w in all_workers)
        avg_success_rate = (
            sum(w.reputation.success_rate for w in all_workers) / len(all_workers)
            if all_workers else 0
        )
        
        return {
            "total_workers": len(all_workers),
            "idle_workers": len(self.get_idle_workers()),
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "total_xp": total_xp,
            "avg_success_rate": round(avg_success_rate, 3)
        }
    
    def remove_worker(self, worker_id: str) -> bool:
        """Remove a worker from the registry"""
        if worker_id in self.workers:
            del self.workers[worker_id]
            self._save_workers()
            return True
        return False
    
    def pause_worker(self, worker_id: str) -> bool:
        """Pause a worker (won't receive new tasks)"""
        return self.update_worker_status(worker_id, WorkerStatus.PAUSED.value)
    
    def resume_worker(self, worker_id: str) -> bool:
        """Resume a paused worker"""
        return self.update_worker_status(worker_id, WorkerStatus.IDLE.value)


# Default registry instance
_default_registry: Optional[WorkerRegistry] = None


def get_registry(storage_path: Optional[str] = None) -> WorkerRegistry:
    """Get or create the default worker registry"""
    global _default_registry
    if _default_registry is None:
        _default_registry = WorkerRegistry(storage_path)
    return _default_registry


def create_default_workers(registry: WorkerRegistry) -> List[Worker]:
    """
    Create a set of default workers for a new system.
    
    Returns list of created workers
    """
    workers = []
    
    # Builder workers
    workers.append(registry.register_worker(
        worker_type=WorkerType.BUILDER.value,
        model_source="local_ollama:deepseek-8b",
        fallback_model="cloud_openai:gpt-4"
    ))
    
    # Researcher workers
    workers.append(registry.register_worker(
        worker_type=WorkerType.RESEARCHER.value,
        model_source="local_ollama:qwen2.5",
        fallback_model="brave_search"
    ))
    
    # Documenter workers
    workers.append(registry.register_worker(
        worker_type=WorkerType.DOCUMENTER.value,
        model_source="local_ollama:qwen2.5",
        fallback_model="cloud_openai:gpt-3.5-turbo"
    ))
    
    # Verifier workers
    workers.append(registry.register_worker(
        worker_type=WorkerType.VERIFIER.value,
        model_source="cloud_openai:gpt-4",
        fallback_model="cloud_anthropic:claude-3-sonnet"
    ))
    
    # Evaluator workers
    workers.append(registry.register_worker(
        worker_type=WorkerType.EVALUATOR.value,
        model_source="local_ollama:deepseek-8b",
        fallback_model="cloud_openai:gpt-4"
    ))
    
    return workers
