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


@dataclass
class DashboardState:
    """Dashboard state object for API responses"""
    system_health: str = "healthy"
    execution_mode: str = "normal"
    total_ideas: int = 0
    active_projects: int = 0
    pending_tasks: int = 0
    idle_workers: int = 0
    pending_reviews: int = 0
    last_updated: str = ""
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
    
    @property
    def gate_type(self) -> str:
        """Alias for type property for backward compatibility"""
        return self.type
    
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
    
    @property
    def node_type(self) -> str:
        """Alias for type for test compatibility"""
        return self.type
    
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
class ProjectPathGraph:
    """Graph structure for project path visualization (test-compatible)"""
    project_id: str
    nodes: List[ProjectPathNode]
    edges: List[tuple] = field(default_factory=list)
    current_node_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "project_id": self.project_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": self.edges,
            "current_node_id": self.current_node_id
        }


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
class AggregateWorkerMetrics:
    """Aggregate worker metrics for dashboard"""
    success_rate: float = 0.0
    total_tasks: int = 0
    idle_count: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_latency_seconds: float = 0.0
    
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
    daily_spend_usd: float = 0.0
    weekly_spend_usd: float = 0.0
    monthly_spend_usd: float = 0.0
    api_calls: int = 0
    project_spend: Dict[str, float] = field(default_factory=dict)
    model_spend: Dict[str, float] = field(default_factory=dict)
    
    # Aliases for backward compatibility
    @property
    def daily_spend(self) -> float:
        return self.daily_spend_usd
    
    @daily_spend.setter
    def daily_spend(self, value: float):
        self.daily_spend_usd = value
    
    @property
    def weekly_spend(self) -> float:
        return self.weekly_spend_usd
    
    @weekly_spend.setter
    def weekly_spend(self, value: float):
        self.weekly_spend_usd = value
    
    @property
    def monthly_spend(self) -> float:
        return self.monthly_spend_usd
    
    @monthly_spend.setter
    def monthly_spend(self, value: float):
        self.monthly_spend_usd = value
    
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
        self.project_paths: Dict[str, ProjectPathGraph] = {}
        self.worker_metrics: Dict[str, WorkerMetrics] = {}
        self.aggregate_worker_metrics: AggregateWorkerMetrics = AggregateWorkerMetrics()
        self.system_metrics: Optional[SystemMetrics] = None
        self.cost_metrics: CostMetrics = CostMetrics()
        
        # Execution state
        self._execution_mode = ExecutionMode.NORMAL
        self._system_health = "healthy"
        self.system_status = "running"  # running, paused, error
        self.start_time = datetime.utcnow()
    
    @property
    def execution_mode(self) -> str:
        return self._execution_mode.value
    
    @execution_mode.setter
    def execution_mode(self, value):
        if isinstance(value, ExecutionMode):
            self._execution_mode = value
        else:
            self._execution_mode = ExecutionMode(value)
    
    @property
    def system_health(self) -> str:
        return self._system_health
    
    @system_health.setter
    def system_health(self, value: str):
        self._system_health = value
    
    # =========================================================================
    # Compatibility Methods
    # =========================================================================
    
    def list_review_cards(
        self,
        project_id: str = None,
        status: str = None,
        gate_type: str = None,
        risk_level: str = None
    ) -> List[ReviewCard]:
        """List review cards with filters"""
        return list_review_cards(self, project_id, status, gate_type, risk_level)
    
    def approve_review_card(self, card_id: str, notes: str = "") -> Optional[ReviewCard]:
        """Approve a review card (compatibility wrapper)"""
        return approve_review_card(self, card_id, notes)
    
    def reject_review_card(self, card_id: str, notes: str) -> Optional[ReviewCard]:
        """Reject a review card (compatibility wrapper)"""
        return reject_review_card(self, card_id, notes)
    
    def modify_review_card(self, card_id: str, notes: str, 
                          constraints_added: List[str] = None) -> Optional[ReviewCard]:
        """Modify a review card (compatibility wrapper)"""
        return modify_review_card(self, card_id, notes, constraints_added)
    
    def create_path_graph(self, project_id: str, tasks: List[Dict],
                          artifacts: List[Dict] = None) -> ProjectPathNode:
        """Create project path graph (compatibility wrapper)"""
        return create_path_graph(self, project_id, tasks, artifacts)
    
    def get_path_graph(self, project_id: str) -> Optional[Dict]:
        """Get project path graph (compatibility wrapper)"""
        return get_path_graph(self, project_id)
    
    def update_path_graph_node(self, project_id: str, node_id: str,
                               status: str) -> Optional[Dict]:
        """Update node in path graph (compatibility wrapper)"""
        return update_path_graph_node(self, project_id, node_id, status)
    
    def set_system_health(self, health: str) -> None:
        """Set system health status"""
        self.system_health = health
    
    def set_execution_mode(self, mode: str) -> bool:
        """Set execution mode (compatibility wrapper)"""
        self._execution_mode = ExecutionMode(mode)
        return True
    
    def get_dashboard_state(self, ideas_count: int = 0, projects_count: int = 0,
                           tasks_count: int = 0, workers_idle: int = 0) -> DashboardState:
        """Get dashboard state"""
        return DashboardState(
            system_health=self.system_health,
            execution_mode=self.execution_mode,
            total_ideas=ideas_count,
            active_projects=projects_count,
            pending_tasks=tasks_count,
            idle_workers=workers_idle,
            pending_reviews=len(self.get_pending_reviews()),
            last_updated=datetime.utcnow().isoformat() + "Z"
        )
    
    def update_worker_metrics(self, metrics: Dict[str, Any]) -> None:
        """Update worker metrics (compatibility wrapper)"""
        # Update aggregate metrics
        if "success_rate" in metrics:
            self.aggregate_worker_metrics.success_rate = metrics["success_rate"]
        if "total_tasks" in metrics:
            self.aggregate_worker_metrics.total_tasks = metrics["total_tasks"]
        if "idle_count" in metrics:
            self.aggregate_worker_metrics.idle_count = metrics["idle_count"]
        
        # Also update per-worker metrics if worker_id provided
        worker_id = metrics.get("worker_id")
        if worker_id and worker_id in self.worker_metrics:
            wm = self.worker_metrics[worker_id]
            if "success_rate" in metrics:
                wm.success_rate = metrics["success_rate"]
            if "total_tasks" in metrics:
                wm.success_count = int(metrics["total_tasks"] * metrics.get("success_rate", 0.8))
    
    def get_worker_metrics(self, worker_id: str = None) -> AggregateWorkerMetrics:
        """Get worker metrics (compatibility wrapper)"""
        return self.aggregate_worker_metrics
    
    def get_worker_metrics_func(self, worker_id: str = None) -> Any:
        """Internal worker metrics getter"""
        if worker_id:
            return self.worker_metrics.get(worker_id)
        return self.aggregate_worker_metrics
    
    def record_task_completion(self, success: bool, latency_seconds: float) -> None:
        """Record task completion (compatibility wrapper)"""
        if success:
            self.aggregate_worker_metrics.tasks_completed += 1
            # Update average latency for successful tasks only
            total_success = self.aggregate_worker_metrics.tasks_completed
            old_avg = self.aggregate_worker_metrics.avg_latency_seconds
            if total_success == 1:
                self.aggregate_worker_metrics.avg_latency_seconds = latency_seconds
            else:
                self.aggregate_worker_metrics.avg_latency_seconds = (
                    (old_avg * (total_success - 1) + latency_seconds) / total_success
                )
        else:
            self.aggregate_worker_metrics.tasks_failed += 1
    
    def record_api_call(self, cost_usd: float = 0.0) -> None:
        """Record API call (compatibility wrapper)"""
        self.cost_metrics.api_calls += 1
        self.cost_metrics.daily_spend_usd += cost_usd
        self.cost_metrics.monthly_spend_usd += cost_usd
    
    def get_observability_metrics(self) -> Dict:
        """Get observability metrics"""
        return {
            "worker_success_rate": 0.0,
            "task_latency_avg_seconds": 0.0,
            "api_calls_total": self.cost_metrics.daily_spend,
            "model_latency_avg_ms": 0.0,
            "error_frequency": 0.0,
            "cost_daily_usd": self.cost_metrics.daily_spend,
            "tasks_completed_today": 0,
            "tasks_failed_today": 0,
            "queue_wait_time_avg_seconds": 0.0
        }
    
    # =========================================================================
    # Review Card (Human Gate) Methods
    # =========================================================================
    
    def create_review_card(
        self,
        project_id: str,
        gate_type: str,
        risk_level: str = "medium",
        summary: str = None,
        why_now: str = None,
        affected_entities: List[str] = None,
        change: str = None,
        options: List[Dict[str, Any]] = None,
        recommended_option: str = None,
        evidence_ids: List[str] = None,
        impact_preview: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> ReviewCard:
        """Create a new review card for human approval"""
        
        # Support legacy context parameter for backward compatibility
        if context:
            summary = summary or context.get("summary", "")
            why_now = why_now or context.get("why_now", "")
            affected_entities = affected_entities or context.get("affected_entities", [])
        
        summary = summary or ""
        why_now = why_now or ""
        affected_entities = affected_entities or []
        
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
            "total_cards": total,
            "pending_count": pending,
            "by_status": {
                "pending": pending,
                "approved": approved,
                "rejected": rejected,
                "modified": modified
            },
            "by_type": by_type,
            "by_risk": by_risk
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
    ) -> ProjectPathGraph:
        """Build a project path graph from tasks and artifacts"""
        
        artifacts = artifacts or []
        artifact_map = {a.get("id"): a for a in artifacts}
        
        # Build task nodes and edges
        task_nodes = []
        edges = []
        current_node_id = None
        
        for task in tasks:
            task_id = task.get("id")
            state = task.get("state", "pending")
            depends_on = task.get("depends_on", [])
            
            # Determine node status
            status_map = {
                "created": "pending",
                "queued": "running",
                "assigned": "running",
                "running": "running",
                "completed": "completed",
                "needs_review": "pending",
                "verifying": "running",
                "verified": "completed",
                "failed": "failed",
                "canceled": "blocked",
                "blocked": "blocked"
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
            
            # Track the currently running node
            if state == "running":
                current_node_id = task_id
            
            # Build edges from dependencies
            for dep in depends_on:
                edges.append((dep, task_id))
        
        # Add artifact nodes
        all_nodes = list(task_nodes)
        for artifact in artifacts:
            artifact_node = ProjectPathNode(
                id=artifact.get("id"),
                type="artifact",
                label=artifact.get("name", artifact.get("id")),
                status="completed",
                artifact_id=artifact.get("id"),
                metadata={"task_id": artifact.get("task_id")}
            )
            all_nodes.append(artifact_node)
            # Add edge from task to artifact
            task_id = artifact.get("task_id")
            if task_id:
                edges.append((task_id, artifact.get("id")))
        
        # Create the graph object
        graph = ProjectPathGraph(
            project_id=project_id,
            nodes=all_nodes,
            edges=edges,
            current_node_id=current_node_id
        )
        
        # Also store the root node for backward compatibility
        root = ProjectPathNode(
            id=f"{project_id}_root",
            type="project",
            label=project_name,
            status="running",
            children=task_nodes
        )
        self.project_paths[project_id] = graph
        
        return graph
    
    def get_project_path(self, project_id: str) -> Optional[ProjectPathGraph]:
        """Get project path graph"""
        return self.project_paths.get(project_id)
    
    def update_task_status(self, project_id: str, task_id: str, status: str) -> bool:
        """Update task status in project path"""
        graph = self.project_paths.get(project_id)
        if not graph:
            return False
        
        # Find and update the task node
        for node in graph.nodes:
            if node.id == task_id:
                # Map status to node status
                status_map = {
                    "created": "pending",
                    "queued": "running",
                    "assigned": "running",
                    "running": "running",
                    "completed": "completed",
                    "needs_review": "pending",
                    "verifying": "running",
                    "verified": "completed",
                    "failed": "failed",
                    "canceled": "blocked",
                    "blocked": "blocked"
                }
                node.status = status_map.get(status, status)
                
                # If completed, update current_node_id to next running/pending task
                if status == "completed":
                    for n in graph.nodes:
                        if n.status in ("running", "pending") and n.id != task_id:
                            graph.current_node_id = n.id
                            break
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
    
    def get_worker_metrics_by_id(self, worker_id: str) -> Optional[Dict]:
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
        metrics: Dict[str, Any] = None,
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
        
        # Handle dict parameter
        if metrics:
            if "cpu_percent" in metrics:
                self.system_metrics.cpu_percent = metrics["cpu_percent"]
            if "memory_percent" in metrics:
                self.system_metrics.memory_percent = metrics["memory_percent"]
            if "disk_percent" in metrics:
                self.system_metrics.disk_percent = metrics["disk_percent"]
            if "total_tasks" in metrics:
                total_tasks = metrics["total_tasks"]
            if "completed_tasks" in metrics:
                completed_tasks = metrics["completed_tasks"]
            if "failed_tasks" in metrics:
                failed_tasks = metrics["failed_tasks"]
            if "queue_length" in metrics:
                queue_length = metrics["queue_length"]
            if "avg_latency" in metrics:
                avg_latency = metrics["avg_latency"]
            if "api_usage" in metrics:
                api_usage = metrics["api_usage"]
        
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
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        if not self.system_metrics:
            self.update_system_metrics()
        
        return self.system_metrics
    
    def update_cost_metrics(
        self,
        metrics: Dict[str, Any] = None,
        daily: float = None,
        weekly: float = None,
        monthly: float = None,
        project_costs: Dict[str, float] = None,
        model_costs: Dict[str, float] = None
    ) -> CostMetrics:
        """Update cost metrics - accepts either a dict or individual parameters"""
        
        # Handle dict parameter
        if metrics:
            if "daily_spend_usd" in metrics:
                self.cost_metrics.daily_spend_usd = metrics["daily_spend_usd"]
            if "daily_spend" in metrics:
                self.cost_metrics.daily_spend = metrics["daily_spend"]
            if "weekly_spend_usd" in metrics:
                self.cost_metrics.weekly_spend_usd = metrics["weekly_spend_usd"]
            if "monthly_spend_usd" in metrics:
                self.cost_metrics.monthly_spend_usd = metrics["monthly_spend_usd"]
            if "api_calls" in metrics:
                self.cost_metrics.api_calls = metrics["api_calls"]
        
        # Handle individual parameters
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
    
    def get_cost_metrics(self) -> CostMetrics:
        """Get current cost metrics"""
        return self.cost_metrics
    
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
        self.execution_mode = ExecutionMode(mode)
        return True
    
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
            "path_graphs": [g.to_dict() for g in self.project_paths.values()],
            "execution_mode": self.execution_mode,
            "system_health": self.system_health,
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


# Singleton instance
_dashboard_instance: Optional[DashboardAPI] = None


def get_dashboard(config: Optional[Dict] = None) -> DashboardAPI:
    """Get or create the singleton dashboard instance"""
    global _dashboard_instance
    if _dashboard_instance is None:
        _dashboard_instance = DashboardAPI(config)
    return _dashboard_instance


# Additional helper methods for compatibility

def list_review_cards(dashboard: DashboardAPI, project_id: str = None, status: str = None, 
                       gate_type: str = None, risk_level: str = None) -> List[ReviewCard]:
    """List review cards with filters (compatibility function)"""
    cards = list(dashboard.review_cards.values())
    
    if project_id:
        cards = [c for c in cards if c.project_id == project_id]
    if status:
        cards = [c for c in cards if c.status == status]
    if gate_type:
        cards = [c for c in cards if c.type == gate_type]
    if risk_level:
        cards = [c for c in cards if c.risk_level == risk_level]
    
    # Sort by created_at descending
    cards.sort(key=lambda c: c.created_at, reverse=True)
    return cards


def approve_review_card(dashboard: DashboardAPI, card_id: str, notes: str = "") -> Optional[ReviewCard]:
    """Approve a review card (compatibility function)"""
    if dashboard.approve_review(card_id, notes):
        return dashboard.review_cards.get(card_id)
    return None


def reject_review_card(dashboard: DashboardAPI, card_id: str, notes: str) -> Optional[ReviewCard]:
    """Reject a review card (compatibility function)"""
    if dashboard.reject_review(card_id, notes):
        return dashboard.review_cards.get(card_id)
    return None


def modify_review_card(dashboard: DashboardAPI, card_id: str, notes: str, 
                       constraints_added: List[str] = None) -> Optional[ReviewCard]:
    """Modify a review card (compatibility function)"""
    if dashboard.modify_review(card_id, notes, constraints_added):
        return dashboard.review_cards.get(card_id)
    return None


def create_path_graph(dashboard: DashboardAPI, project_id: str, tasks: List[Dict],
                      artifacts: List[Dict] = None) -> ProjectPathNode:
    """Create project path graph (compatibility function)"""
    return dashboard.build_project_path(project_id, f"Project {project_id}", tasks, artifacts)


def get_path_graph(dashboard: DashboardAPI, project_id: str) -> Optional[ProjectPathGraph]:
    """Get project path graph (compatibility function)"""
    return dashboard.get_project_path(project_id)


def update_path_graph_node(dashboard: DashboardAPI, project_id: str, node_id: str,
                           status: str) -> Optional[ProjectPathGraph]:
    """Update node in path graph (compatibility function)"""
    if dashboard.update_task_status(project_id, node_id, status):
        return dashboard.get_project_path(project_id)
    return None


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
