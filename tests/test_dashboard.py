"""
AI Founder OS - Dashboard API Tests

Tests for the Dashboard API module including:
- Review Card (Human Gate) functionality
- Project Path Graph
- Worker Monitor
- Observability metrics
"""

import pytest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dashboard.api import (
    DashboardAPI,
    ReviewCard,
    ProjectPathNode,
    WorkerMetrics,
    SystemMetrics,
    CostMetrics,
    GateStatus,
    ExecutionMode,
    create_dashboard
)


class TestReviewCard:
    """Tests for Review Card (Human Gate) functionality"""
    
    def test_create_review_card(self):
        """Should create a review card with correct fields"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="high",
            summary="Review code changes",
            why_now="Feature complete",
            affected_entities=["task_001"],
            change="Merge to main",
            options=[{"id": "opt1", "description": "Approve"}],
            recommended_option="opt1"
        )
        
        assert card.id.startswith("gate_")
        assert card.project_id == "proj_001"
        assert card.type == "task_review"
        assert card.risk_level == "high"
        assert card.status == "pending"
        assert card.context["summary"] == "Review code changes"
    
    def test_get_pending_reviews(self):
        """Should return pending reviews sorted by priority"""
        dashboard = create_dashboard()
        
        # Create cards with different risk levels
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="low",
            summary="Low risk review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="high",
            summary="High risk review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        
        pending = dashboard.get_pending_reviews()
        
        # High risk should come first
        assert len(pending) == 2
        assert pending[0].risk_level == "high"
    
    def test_get_pending_reviews_by_project(self):
        """Should filter pending reviews by project"""
        dashboard = create_dashboard()
        
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="low",
            summary="Project 1 review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        dashboard.create_review_card(
            project_id="proj_002",
            gate_type="task_review",
            risk_level="low",
            summary="Project 2 review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        
        pending_proj1 = dashboard.get_pending_reviews("proj_001")
        
        assert len(pending_proj1) == 1
        assert pending_proj1[0].project_id == "proj_001"
    
    def test_approve_review(self):
        """Should approve a review card"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="medium",
            summary="Test review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        
        result = dashboard.approve_review(card.id, "Looks good!")
        
        assert result is True
        updated = dashboard.get_review_card(card.id)
        assert updated.status == "approved"
        assert updated.resolution["decision"] == "approved"
        assert updated.resolution["notes"] == "Looks good!"
    
    def test_reject_review(self):
        """Should reject a review card"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="medium",
            summary="Test review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        
        result = dashboard.reject_review(card.id, "Needs changes")
        
        assert result is True
        updated = dashboard.get_review_card(card.id)
        assert updated.status == "rejected"
        assert updated.resolution["decision"] == "rejected"
    
    def test_modify_review(self):
        """Should approve with modifications"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="medium",
            summary="Test review",
            why_now="...",
            affected_entities=[],
            change="..."
        )
        
        constraints = ["require_test_coverage", "require_docs"]
        result = dashboard.modify_review(
            card.id,
            "Approved with constraints",
            constraints
        )
        
        assert result is True
        updated = dashboard.get_review_card(card.id)
        assert updated.status == "modified"
        assert updated.resolution["decision"] == "modified"
        assert updated.resolution["constraints_added"] == constraints
    
    def test_review_stats(self):
        """Should return correct review statistics"""
        dashboard = create_dashboard()
        
        # Create some cards
        c1 = dashboard.create_review_card("proj_001", "task_review", "high", "s", "w", [], "c")
        c2 = dashboard.create_review_card("proj_001", "skill_install", "medium", "s", "w", [], "c")
        
        # Approve one
        dashboard.approve_review(c1.id)
        
        stats = dashboard.get_review_stats()
        
        assert stats["total"] == 2
        assert stats["pending"] == 1
        assert stats["approved"] == 1
        assert stats["by_type"]["task_review"] == 1
        assert stats["by_type"]["skill_install"] == 1
        assert stats["by_risk_level"]["high"] == 1
    
    def test_get_next_gate(self):
        """Should return highest priority pending gate"""
        dashboard = create_dashboard()
        
        # Create cards
        dashboard.create_review_card(
            "proj_001", "task_review", "low", "low", "w", [], "c"
        )
        dashboard.create_review_card(
            "proj_001", "task_review", "high", "high", "w", [], "c"
        )
        
        next_gate = dashboard.get_next_gate()
        
        assert next_gate is not None
        assert next_gate["risk_level"] == "high"
        assert next_gate["summary"] == "high"


class TestProjectPathGraph:
    """Tests for Project Path Graph"""
    
    def test_build_project_path(self):
        """Should build project path from tasks"""
        dashboard = create_dashboard()
        
        tasks = [
            {
                "id": "task_001",
                "title": "Implement Feature",
                "goal": "Build a new feature",
                "state": "verified",
                "expected_artifact": {"path_hint": "src/feature.py"}
            },
            {
                "id": "task_002",
                "title": "Write Tests",
                "goal": "Write unit tests",
                "state": "running",
                "expected_artifact": {"path_hint": "tests/test_feature.py"}
            }
        ]
        
        path = dashboard.build_project_path(
            "proj_001",
            "My Project",
            tasks
        )
        
        assert path.id == "proj_001_root"
        assert path.type == "project"
        assert len(path.children) == 2
    
    def test_get_project_path(self):
        """Should return project path as dictionary"""
        dashboard = create_dashboard()
        
        tasks = [{"id": "task_001", "title": "Test", "goal": "...", "state": "completed"}]
        
        dashboard.build_project_path("proj_001", "Test Project", tasks)
        result = dashboard.get_project_path("proj_001")
        
        assert result is not None
        assert result["id"] == "proj_001_root"
        assert result["type"] == "project"
    
    def test_update_task_status(self):
        """Should update task status in path"""
        dashboard = create_dashboard()
        
        tasks = [{"id": "task_001", "title": "Test", "goal": "...", "state": "running"}]
        
        dashboard.build_project_path("proj_001", "Test", tasks)
        
        result = dashboard.update_task_status("proj_001", "task_001", "completed")
        
        assert result is True
        
        # Verify update
        path = dashboard.get_project_path("proj_001")
        task_node = path["children"][0]
        assert task_node["status"] == "completed"


class TestWorkerMonitor:
    """Tests for Worker Monitor"""
    
    def test_register_worker(self):
        """Should register a new worker"""
        dashboard = create_dashboard()
        
        metrics = dashboard.register_worker(
            "worker_builder_01",
            "builder",
            "ollama:deepseek-8b"
        )
        
        assert metrics.worker_id == "worker_builder_01"
        assert metrics.worker_type == "builder"
        assert metrics.status == "idle"
        assert metrics.xp_total == 0
    
    def test_update_worker_status(self):
        """Should update worker status"""
        dashboard = create_dashboard()
        dashboard.register_worker("worker_01", "builder")
        
        result = dashboard.update_worker_status(
            "worker_01",
            "busy",
            "task_001"
        )
        
        assert result is True
        
        updated = dashboard.get_worker_metrics("worker_01")
        assert updated["status"] == "busy"
        assert updated["current_task_id"] == "task_001"
    
    def test_record_worker_success(self):
        """Should record successful task completion"""
        dashboard = create_dashboard()
        dashboard.register_worker("worker_01", "builder")
        
        result = dashboard.record_worker_success("worker_01", 15.0)
        
        assert result is True
        
        metrics = dashboard.get_worker_metrics("worker_01")
        assert metrics["success_count"] == 1
        assert metrics["xp_total"] == 1
        assert metrics["success_rate"] == 1.0
    
    def test_record_worker_failure(self):
        """Should record failed task"""
        dashboard = create_dashboard()
        dashboard.register_worker("worker_01", "builder")
        
        # First record a success
        dashboard.record_worker_success("worker_01", 10.0)
        
        # Then record failure
        result = dashboard.record_worker_failure("worker_01")
        
        assert result is True
        
        metrics = dashboard.get_worker_metrics("worker_01")
        assert metrics["failure_count"] == 1
        assert metrics["success_rate"] == 0.5
    
    def test_record_experience_reuse(self):
        """Should record experience reuse for XP bonus"""
        dashboard = create_dashboard()
        dashboard.register_worker("worker_01", "builder")
        
        result = dashboard.record_experience_reuse("worker_01")
        
        assert result is True
        
        metrics = dashboard.get_worker_metrics("worker_01")
        assert metrics["reused_count"] == 1
        assert metrics["xp_total"] == 2  # 2 XP bonus
    
    def test_get_worker_stats(self):
        """Should return aggregated worker statistics"""
        dashboard = create_dashboard()
        
        dashboard.register_worker("w1", "builder")
        dashboard.register_worker("w2", "builder")
        dashboard.register_worker("w3", "verifier")
        
        dashboard.update_worker_status("w1", "busy")
        dashboard.update_worker_status("w2", "idle")
        
        stats = dashboard.get_worker_stats()
        
        assert stats["total"] == 3
        assert stats["busy"] == 1
        assert stats["idle"] == 2
        assert stats["by_type"]["builder"] == 2
        assert stats["by_type"]["verifier"] == 1


class TestObservability:
    """Tests for Observability metrics"""
    
    def test_update_system_metrics(self):
        """Should update system metrics"""
        dashboard = create_dashboard()
        
        metrics = dashboard.update_system_metrics(
            total_tasks=100,
            completed_tasks=80,
            failed_tasks=5,
            queue_length=10,
            avg_latency=5.5,
            api_usage=1000
        )
        
        assert metrics.total_tasks == 100
        assert metrics.completed_tasks == 80
        assert metrics.failed_tasks == 5
        assert metrics.queue_length == 10
        assert metrics.error_rate == 0.05
    
    def test_error_rate_calculation(self):
        """Should calculate error rate correctly"""
        dashboard = create_dashboard()
        
        dashboard.update_system_metrics(
            total_tasks=100,
            completed_tasks=90,
            failed_tasks=10
        )
        
        result = dashboard.get_system_metrics()
        
        assert result["error_rate"] == 0.1
    
    def test_cost_metrics(self):
        """Should track cost metrics"""
        dashboard = create_dashboard()
        
        dashboard.update_cost_metrics(
            daily=10.0,
            weekly=50.0,
            monthly=200.0,
            project_costs={"proj_001": 5.0, "proj_002": 5.0},
            model_costs={"gpt-4": 8.0, "deepseek-8b": 2.0}
        )
        
        result = dashboard.get_cost_metrics()
        
        assert result["daily_spend"] == 10.0
        assert result["weekly_spend"] == 50.0
        assert result["project_spend"]["proj_001"] == 5.0
        assert result["model_spend"]["gpt-4"] == 8.0
    
    def test_worker_counts_in_metrics(self):
        """Should include worker counts in system metrics"""
        dashboard = create_dashboard()
        
        dashboard.register_worker("w1", "builder")
        dashboard.register_worker("w2", "builder")
        dashboard.update_worker_status("w1", "busy")
        
        dashboard.update_system_metrics(total_tasks=10)
        
        result = dashboard.get_system_metrics()
        
        assert result["active_workers"] == 1
        assert result["idle_workers"] == 1


class TestSystemStatus:
    """Tests for System Status"""
    
    def test_get_status(self):
        """Should return overall system status"""
        dashboard = create_dashboard()
        
        dashboard.register_worker("w1", "builder")
        
        status = dashboard.get_status()
        
        assert status["system_status"] == "running"
        assert status["execution_mode"] == "normal"
        assert "uptime_seconds" in status
        assert "review_stats" in status
        assert "worker_stats" in status
    
    def test_set_execution_mode(self):
        """Should set execution mode"""
        dashboard = create_dashboard()
        
        assert dashboard.set_execution_mode("safe") is True
        assert dashboard.set_execution_mode("turbo") is True
        assert dashboard.set_execution_mode("invalid") is False
    
    def test_pause_resume_system(self):
        """Should pause and resume system"""
        dashboard = create_dashboard()
        
        dashboard.pause_system()
        assert dashboard.system_status == "paused"
        
        dashboard.resume_system()
        assert dashboard.system_status == "running"


class TestStateManagement:
    """Tests for state import/export"""
    
    def test_export_import_state(self):
        """Should export and import state"""
        dashboard = create_dashboard()
        
        # Create some data
        dashboard.create_review_card(
            "proj_001", "task_review", "high", "s", "w", [], "c"
        )
        dashboard.register_worker("w1", "builder")
        
        # Export
        state = dashboard.export_state()
        
        assert len(state["review_cards"]) == 1
        assert len(state["worker_metrics"]) == 1
        
        # Import to new dashboard
        dashboard2 = create_dashboard()
        dashboard2.import_state(state)
        
        # Verify
        pending = dashboard2.get_pending_reviews()
        assert len(pending) == 1
        
        workers = dashboard2.get_all_workers()
        assert len(workers) == 1


class TestReviewCardModel:
    """Tests for ReviewCard model directly"""
    
    def test_review_card_creation(self):
        """Should create review card with auto-generated ID"""
        card = ReviewCard(
            project_id="proj_001",
            type="task_review",
            risk_level="high",
            context={"summary": "test"},
            proposal={"change": "test"}
        )
        
        assert card.id.startswith("gate_")
        assert card.status == "pending"
    
    def test_review_card_to_dict(self):
        """Should convert to dictionary"""
        card = ReviewCard(
            project_id="proj_001",
            type="task_review",
            risk_level="high",
            context={"summary": "test"},
            proposal={"change": "test"}
        )
        
        data = card.to_dict()
        
        assert data["project_id"] == "proj_001"
        assert data["status"] == "pending"
    
    def test_review_card_from_dict(self):
        """Should create from dictionary"""
        data = {
            "id": "gate_123",
            "project_id": "proj_001",
            "type": "task_review",
            "risk_level": "high",
            "context": {"summary": "test"},
            "proposal": {"change": "test"},
            "evidence_ids": [],
            "impact_preview": {},
            "status": "pending",
            "resolution": None,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z"
        }
        
        card = ReviewCard.from_dict(data)
        
        assert card.id == "gate_123"
        assert card.project_id == "proj_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
