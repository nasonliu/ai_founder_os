"""
AI Founder OS - Dashboard Module

Dashboard backend API providing:
- Project Path Graph visualization
- Review Inbox for Human Gate
- Worker Monitor
- Observability metrics
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class ProjectStatus(Enum):
    """Project status values"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class GateType(Enum):
    """Human Gate types"""
    TASK_REVIEW = "task_review"
    SKILL_INSTALL = "skill_install"
    CONNECTION_SCOPE = "connection_scope"
    POLICY_CHANGE = "policy_change"
    KPI_FAILURE = "kpi_failure"
    REPO_WRITE = "repo_write"


class GateStatus(Enum):
    """Review card status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class ExecutionMode(Enum):
    """System execution modes"""
    SAFE = "safe"
    NORMAL = "normal"
    TURBO = "turbo"


@dataclass
class ReviewCard:
    """
    Review Card for Human Gate System.
    
    Represents a decision point that requires human approval.
    """
    id: str = ""
    project_id: str = ""
    type: str = ""
    risk_level: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    proposal: Dict[str, Any] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)
    impact_preview: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    resolution: Optional[Dict[str, Any]] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = f"gate_{uuid.uuid4().hex[:8]}"
        if not self.created_at:
            now = datetime.utcnow().isoformat() + "Z"
            self.created_at = now
            self.updated_at = now
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ReviewCard':
        return cls(**data)
    
    def approve(self, notes: str = "") -> None:
        """Approve the review card"""
        self.status = "approved"
        self.resolution = {
            "by": "human",
            "decision": "approved",
            "notes": notes,
            "resolved_at": datetime.utcnow().isoformat() + "Z"
        }
        self.updated_at = datetime.utcnow().isoformat() + "Z"
    
    def reject(self, notes: str = "") -> None:
        """Reject the review card"""
        self.status = "rejected"
        self.resolution = {
            "by": "human",
            "decision": "rejected",
            "notes": notes,
            "resolved_at": datetime.utcnow().isoformat() + "Z"
        }
        self.updated_at = datetime.utcnow().isoformat() + "Z"
    
    def modify(self, notes: str, constraints_added: List[str] = None) -> None:
        """Approve with modifications"""
        self.status = "modified"
        self.resolution = {
            "by": "human",
            "decision": "modified",
            "notes": notes,
            "constraints_added": constraints_added or [],
            "resolved_at": datetime.utcnow().isoformat() + "Z"
        }
        self.updated_at = datetime.utcnow().isoformat() + "Z"


@dataclass
class ProjectPathNode:
    """Node in Project Path Graph"""
    id: str
    type: str  # idea, task, subtask, artifact, validator, verifier, human_review, dataset, training
    label: str
    status: str  # pending, running, completed, failed, waiting
    artifact_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List['ProjectPathNode'] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        result = {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "status": self.status,
            "metadata": self.metadata
        }
        if self.artifact_id:
            result["artifact_id"] = self.artifact_id
        if self.children:
            result["children"] = [c.to_dict() for c in self.children]
        return result


@dataclass
class WorkerMetrics:
    """Worker metrics for observability"""
    worker_id: str
    worker_type: str
    status: str  # idle, busy, paused, error
    xp_total: int = 0
    success_count: int = 0
    failure_count: int = 0
    reused_count: int = 0
    success_rate: float = 0.0
    avg_resolution_time_minutes: float = 0.0
    current_task_id: Optional[str] = None
    reputation_score: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SystemMetrics:
    """System-wide metrics for observability"""
    timestamp: str = ""
    uptime_seconds: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    active_workers: int = 0
    idle_workers: int = 0
    queue_length: int = 0
    avg_task_latency_minutes: float = 0.0
    error_rate: float = 0.0
    daily_spend_usd: float = 0.0
    api_usage_count: int = 0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CostMetrics:
    """Cost tracking metrics"""
    daily_spend: float = 0.0
    weekly_spend: float = 0.0
    monthly_spend: float = 0.0
    project_spend: Dict[str, float] = field(default_factory=dict)
    model_spend: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


class DashboardAPI:
    """
    Dashboard API for AI Founder OS.
    
    Provides backend endpoints for:
    - Project Path Graph
    - Review Inbox (Human Gate)
    - Worker Monitor
    - Observability
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Data storage (in-memory for now, can be replaced with DB)
        self.review_cards: Dict[str, ReviewCard] = {}
        self.project_paths: Dict[str, ProjectPathNode] = {}
        self.worker_metrics: Dict[str, WorkerMetrics] = {}
        self.system_metrics: Optional[SystemMetrics] = None
        self.cost_metrics: CostMetrics = CostMetrics()
        
        # Execution state
        self.execution_mode = ExecutionMode.NORMAL
        self.system_status = "running"  # running, paused, error
        self.start_time = datetime.utcnow()
    
    # =========================================================================
    # Review Card (Human Gate) Methods
    # =========================================================================
    
    def create_review_card(
        self,
        project_id: str,
        gate_type: str,
        risk_level: str,
        summary: str,
        why_now: str,
        affected_entities: List[str],
        change: str,
        options: List[Dict[str, Any]] = None,
        recommended_option: str = None,
        evidence_ids: List[str] = None,
        impact_preview: Dict[str, Any] = None
    ) -> ReviewCard:
        """Create a new review card for human approval"""
        
        card = ReviewCard(
            id=f"gate_{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            type=gate_type,
            risk_level=risk_level,
            context={
                "summary": summary,
                "why_now": why_now,
                "affected_entities": affected_entities
            },
            proposal={
                "change": change,
                "options": options or [],
                "recommended_option": recommended_option
            },
            evidence_ids=evidence_ids or [],
            impact_preview=impact_preview or {}
        )
        
        self.review_cards[card.id] = card
        return card
    
    def get_pending_reviews(self, project_id: str = None) -> List[ReviewCard]:
        """Get pending review cards, optionally filtered by project"""
        cards = [c for c in self.review_cards.values() if c.status == "pending"]
        
        if project_id:
            cards = [c for c in cards if c.project_id == project_id]
        
        # Sort by risk level and creation time
        risk_order = {"high": 0, "medium": 1, "low": 2}
        cards.sort(key=lambda c: (risk_order.get(c.risk_level, 3), c.created_at))
        
        return cards
    
    def get_review_card(self, card_id: str) -> Optional[ReviewCard]:
        """Get a specific review card"""
        return self.review_cards.get(card_id)
    
    def approve_review(self, card_id: str, notes: str = "") -> bool:
        """Approve a review card"""
        card = self.review_cards.get(card_id)
        if not card:
            return False
        
        card.approve(notes)
        return True
    
    def reject_review(self, card_id: str, notes: str = "") -> bool:
        """Reject a review card"""
        card = self.review_cards.get(card_id)
        if not card:
            return False
        
        card.reject(notes)
        return True
    
    def modify_review(
        self,
        card_id: str,
        notes: str,
        constraints_added: List[str] = None
    ) -> bool:
        """Approve with modifications"""
        card = self.review_cards.get(card_id)
        if not card:
            return False
        
        card.modify(notes, constraints_added)
        return True
    
    def get_review_stats(self) -> Dict:
        """Get review statistics"""
        cards = list(self.review_cards.values())
        
        total = len(cards)
        pending = len([c for c in cards if c.status == "pending"])
        approved = len([c for c in cards if c.status == "approved"])
        rejected = len([c for c in cards if c.status == "rejected"])
        modified = len([c for c in cards if c.status == "modified"])
        
        # By type
        by_type = {}
        for card in cards:
            by_type[card.type] = by_type.get(card.type, 0) + 1
        
        # By risk level
        by_risk = {}
        for card in cards:
            by_risk[card.risk_level] = by_risk.get(card.risk_level, 0) + 1
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "modified": modified,
            "by_type": by_type,
            "by_risk_level": by_risk
        }
    
    # =========================================================================
    # Project Path Graph Methods
    # =========================================================================
    
    def build_project_path(
        self,
        project_id: str,
        project_name: str,
        tasks: List[Dict],
        artifacts: List[Dict] = None
    ) -> ProjectPathNode:
        """Build a project path graph from tasks and artifacts"""
        
        artifacts = artifacts or []
        artifact_map = {a.get("id"): a for a in artifacts}
        
        # Root node
        root = ProjectPathNode(
            id=f"{project_id}_root",
            type="project",
            label=project_name,
            status="running"
        )
        
        # Group tasks by dependency level
        task_map = {}
        for task in tasks:
            task_id = task.get("id")
            task_map[task_id] = task
        
        # Build task nodes (simplified - just list them)
        task_nodes = []
        for task in tasks:
            task_id = task.get("id")
            state = task.get("state", "pending")
            
            # Determine node status
            status_map = {
                "created": "pending",
                "queued": "pending",
                "assigned": "running",
                "running": "running",
                "verifying": "running",
                "verified": "completed",
                "failed": "failed",
                "blocked": "waiting"
            }
            
            node = ProjectPathNode(
                id=task_id,
                type="task",
                label=task.get("title", task_id),
                status=status_map.get(state, "pending"),
                artifact_id=task.get("expected_artifact", {}).get("path_hint"),
                metadata={
                    "goal": task.get("goal", ""),
                    "state": state,
                    "retry_count": task.get("retry_count", 0)
                }
            )
            task_nodes.append(node)
        
        # Add task nodes as children
        root.children = task_nodes
        
        self.project_paths[project_id] = root
        return root
    
    def get_project_path(self, project_id: str) -> Optional[Dict]:
        """Get project path graph as dictionary"""
        path = self.project_paths.get(project_id)
        if path:
            return path.to_dict()
        return None
    
    def update_task_status(self, project_id: str, task_id: str, status: str) -> bool:
        """Update task status in project path"""
        path = self.project_paths.get(project_id)
        if not path:
            return False
        
        # Find and update the task node
        for child in path.children:
            if child.id == task_id:
                child.status = status
                return True
        
        return False
    
    # =========================================================================
    # Worker Monitor Methods
    # =========================================================================
    
    def register_worker(
        self,
        worker_id: str,
        worker_type: str,
        model_source: str = ""
    ) -> WorkerMetrics:
        """Register a new worker"""
        metrics = WorkerMetrics(
            worker_id=worker_id,
            worker_type=worker_type,
            status="idle"
        )
        
        self.worker_metrics[worker_id] = metrics
        return metrics
    
    def update_worker_status(
        self,
        worker_id: str,
        status: str,
        current_task_id: str = None
    ) -> bool:
        """Update worker status"""
        metrics = self.worker_metrics.get(worker_id)
        if not metrics:
            return False
        
        metrics.status = status
        if current_task_id:
            metrics.current_task_id = current_task_id
        
        return True
    
    def record_worker_success(
        self,
        worker_id: str,
        resolution_time_minutes: float
    ) -> bool:
        """Record a successful task completion"""
        metrics = self.worker_metrics.get(worker_id)
        if not metrics:
            return False
        
        metrics.success_count += 1
        metrics.xp_total += 1
        
        # Update success rate
        total = metrics.success_count + metrics.failure_count
        if total > 0:
            metrics.success_rate = metrics.success_count / total
        
        # Update average resolution time
        if metrics.avg_resolution_time_minutes == 0:
            metrics.avg_resolution_time_minutes = resolution_time_minutes
        else:
            # Exponential moving average
            metrics.avg_resolution_time_minutes = (
                0.7 * metrics.avg_resolution_time_minutes +
                0.3 * resolution_time_minutes
            )
        
        # Update reputation
        metrics.reputation_score = (
            metrics.success_rate * 0.6 +
            (1 - min(metrics.avg_resolution_time_minutes / 60, 1)) * 0.4
        )
        
        return True
    
    def record_worker_failure(self, worker_id: str) -> bool:
        """Record a failed task"""
        metrics = self.worker_metrics.get(worker_id)
        if not metrics:
            return False
        
        metrics.failure_count += 1
        metrics.xp_total = max(0, metrics.xp_total - 1)
        
        # Update success rate
        total = metrics.success_count + metrics.failure_count
        if total > 0:
            metrics.success_rate = metrics.success_count / total
        
        return True
    
    def record_experience_reuse(self, worker_id: str) -> bool:
        """Record experience reuse for XP bonus"""
        metrics = self.worker_metrics.get(worker_id)
        if not metrics:
            return False
        
        metrics.reused_count += 1
        metrics.xp_total += 2
        
        return True
    
    def get_worker_metrics(self, worker_id: str) -> Optional[Dict]:
        """Get metrics for a specific worker"""
        metrics = self.worker_metrics.get(worker_id)
        if metrics:
            return metrics.to_dict()
        return None
    
    def get_all_workers(self) -> List[Dict]:
        """Get all worker metrics"""
        return [m.to_dict() for m in self.worker_metrics.values()]
    
    def get_worker_stats(self) -> Dict:
        """Get aggregated worker statistics"""
        workers = list(self.worker_metrics.values())
        
        if not workers:
            return {
                "total": 0,
                "by_type": {},
                "by_status": {}
            }
        
        total = len(workers)
        idle = len([w for w in workers if w.status == "idle"])
        busy = len([w for w in workers if w.status == "busy"])
        paused = len([w for w in workers if w.status == "paused"])
        error = len([w for w in workers if w.status == "error"])
        
        # By type
        by_type = {}
        for w in workers:
            by_type[w.worker_type] = by_type.get(w.worker_type, 0) + 1
        
        # By status
        by_status = {
            "idle": idle,
            "busy": busy,
            "paused": paused,
            "error": error
        }
        
        # Aggregated metrics
        avg_success_rate = sum(w.success_rate for w in workers) / total
        avg_xp = sum(w.xp_total for w in workers) / total
        avg_resolution_time = sum(w.avg_resolution_time_minutes for w in workers) / total
        
        return {
            "total": total,
            "idle": idle,
            "busy": busy,
            "paused": paused,
            "error": error,
            "by_type": by_type,
            "by_status": by_status,
            "avg_success_rate": round(avg_success_rate, 3),
            "avg_xp": round(avg_xp, 1),
            "avg_resolution_time_minutes": round(avg_resolution_time, 1)
        }
    
    # =========================================================================
    # Observability Methods
    # =========================================================================
    
    def update_system_metrics(
        self,
        total_tasks: int = None,
        completed_tasks: int = None,
        failed_tasks: int = None,
        queue_length: int = None,
        avg_latency: float = None,
        api_usage: int = None
    ) -> SystemMetrics:
        """Update system metrics"""
        
        if not self.system_metrics:
            self.system_metrics = SystemMetrics()
        
        if total_tasks is not None:
            self.system_metrics.total_tasks = total_tasks
        if completed_tasks is not None:
            self.system_metrics.completed_tasks = completed_tasks
        if failed_tasks is not None:
            self.system_metrics.failed_tasks = failed_tasks
        if queue_length is not None:
            self.system_metrics.queue_length = queue_length
        if avg_latency is not None:
            self.system_metrics.avg_task_latency_minutes = avg_latency
        if api_usage is not None:
            self.system_metrics.api_usage_count = api_usage
        
        # Calculate derived metrics
        total = self.system_metrics.total_tasks
        if total > 0:
            self.system_metrics.error_rate = (
                self.system_metrics.failed_tasks / total
            )
        
        # Update worker counts
        worker_stats = self.get_worker_stats()
        self.system_metrics.active_workers = worker_stats.get("busy", 0)
        self.system_metrics.idle_workers = worker_stats.get("idle", 0)
        
        # Update uptime
        self.system_metrics.uptime_seconds = int(
            (datetime.utcnow() - self.start_time).total_seconds()
        )
        
        return self.system_metrics
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        if not self.system_metrics:
            self.update_system_metrics()
        
        return self.system_metrics.to_dict()
    
    def update_cost_metrics(
        self,
        daily: float = None,
        weekly: float = None,
        monthly: float = None,
        project_costs: Dict[str, float] = None,
        model_costs: Dict[str, float] = None
    ) -> CostMetrics:
        """Update cost metrics"""
        
        if daily is not None:
            self.cost_metrics.daily_spend = daily
        if weekly is not None:
            self.cost_metrics.weekly_spend = weekly
        if monthly is not None:
            self.cost_metrics.monthly_spend = monthly
        if project_costs:
            self.cost_metrics.project_spend = project_costs
        if model_costs:
            self.cost_metrics.model_spend = model_costs
        
        return self.cost_metrics
    
    def get_cost_metrics(self) -> Dict:
        """Get current cost metrics"""
        return self.cost_metrics.to_dict()
    
    # =========================================================================
    # System Status Methods
    # =========================================================================
    
    def get_status(self) -> Dict:
        """Get overall dashboard status"""
        uptime_seconds = int((datetime.utcnow() - self.start_time).total_seconds())
        
        return {
            "system_status": self.system_status,
            "execution_mode": self.execution_mode.value,
            "uptime_seconds": uptime_seconds,
            "review_stats": self.get_review_stats(),
            "worker_stats": self.get_worker_stats(),
            "pending_reviews": len(self.get_pending_reviews())
        }
    
    def set_execution_mode(self, mode: str) -> bool:
        """Set execution mode (safe, normal, turbo)"""
        try:
            self.execution_mode = ExecutionMode(mode)
            return True
        except ValueError:
            return False
    
    def pause_system(self) -> None:
        """Pause the system"""
        self.system_status = "paused"
    
    def resume_system(self) -> None:
        """Resume the system"""
        self.system_status = "running"
    
    def get_next_gate(self) -> Optional[Dict]:
        """Get the next pending review that needs attention"""
        pending = self.get_pending_reviews()
        
        if not pending:
            return None
        
        # Return the first (highest priority) pending review
        card = pending[0]
        return {
            "card_id": card.id,
            "type": card.type,
            "risk_level": card.risk_level,
            "summary": card.context.get("summary", ""),
            "project_id": card.project_id
        }
    
    def export_state(self) -> Dict:
        """Export dashboard state for persistence"""
        return {
            "review_cards": [c.to_dict() for c in self.review_cards.values()],
            "execution_mode": self.execution_mode.value,
            "system_status": self.system_status,
            "worker_metrics": [w.to_dict() for w in self.worker_metrics.values()]
        }
    
    def import_state(self, state: Dict) -> None:
        """Import dashboard state from persistence"""
        self.review_cards.clear()
        for card_data in state.get("review_cards", []):
            card = ReviewCard.from_dict(card_data)
            self.review_cards[card.id] = card
        
        self.worker_metrics.clear()
        for wm_data in state.get("worker_metrics", []):
            wm = WorkerMetrics(**wm_data)
            self.worker_metrics[wm.worker_id] = wm
        
        if state.get("execution_mode"):
            try:
                self.execution_mode = ExecutionMode(state["execution_mode"])
            except ValueError:
                pass
        
        if state.get("system_status"):
            self.system_status = state["system_status"]


def create_dashboard(config: Optional[Dict] = None) -> DashboardAPI:
    """Factory function to create a Dashboard API"""
    return DashboardAPI(config)


if __name__ == "__main__":
    # Demo usage
    dashboard = create_dashboard()
    
    # Create a review card
    card = dashboard.create_review_card(
        project_id="proj_001",
        gate_type="task_review",
        risk_level="high",
        summary="Review code changes for new feature",
        why_now="Feature is complete and needs review before merge",
        affected_entities=["task_001", "task_002"],
        change="Merge feature branch to main",
        options=[
            {"id": "opt1", "description": "Approve and merge"},
            {"id": "opt2", "description": "Request changes"}
        ],
        recommended_option="opt1",
        impact_preview={
            "files": ["src/feature.py", "tests/test_feature.py"],
            "time_estimate": "30 minutes"
        }
    )
    
    print(f"Created review card: {card.id}")
    
    # Get pending reviews
    pending = dashboard.get_pending_reviews()
    print(f"Pending reviews: {len(pending)}")
    
    # Register some workers
    dashboard.register_worker("worker_builder_01", "builder", "ollama:deepseek-8b")
    dashboard.register_worker("worker_verifier_01", "verifier", "openai:gpt-4")
    
    # Get worker stats
    stats = dashboard.get_worker_stats()
    print(f"Worker stats: {stats}")
    
    # Get dashboard status
    status = dashboard.get_status()
    print(f"Dashboard status: {status}")
