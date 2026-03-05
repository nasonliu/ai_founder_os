"""
AI Founder OS - Dashboard API Tests

Tests for the Dashboard API including:
- Review Card Management (Human Gate)
- Project Path Graph
- Observability Metrics
- Dashboard State
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
    GateType,
    GateStatus,
    ExecutionMode,
    ProjectStatus,
    get_dashboard,
    create_dashboard
)


class TestReviewCardManagement:
    """Tests for Review Card management"""
    
    def test_create_review_card(self):
        """Should create a review card with correct ID format"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            summary="Test review",
            why_now="Testing",
            affected_entities=[],
            change="test change",
            risk_level="medium"
        )
        
        assert card.id.startswith("gate_")
        assert card.project_id == "proj_001"
        assert card.status == GateStatus.PENDING.value
        assert card.risk_level == "medium"
    
    def test_get_review_card(self):
        """Should retrieve a review card by ID"""
        dashboard = create_dashboard()
        
        created = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.SKILL_INSTALL.value,
            context={"summary": "Test", "why_now": "Testing"}
        )
        
        retrieved = dashboard.get_review_card(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.gate_type == GateType.SKILL_INSTALL.value
    
    def test_list_review_cards_by_status(self):
        """Should filter review cards by status"""
        dashboard = create_dashboard()
        
        # Create cards with different statuses
        card1 = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Card 1", "why_now": "Test"}
        )
        
        card2 = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Card 2", "why_now": "Test"}
        )
        
        # Approve one card
        dashboard.approve_review_card(card1.id, "Approved")
        
        # List pending
        pending = dashboard.list_review_cards(status=GateStatus.PENDING.value)
        assert len(pending) == 1
        assert pending[0].id == card2.id
        
        # List approved
        approved = dashboard.list_review_cards(status=GateStatus.APPROVED.value)
        assert len(approved) == 1
        assert approved[0].id == card1.id
    
    def test_list_review_cards_by_project(self):
        """Should filter review cards by project"""
        dashboard = create_dashboard()
        
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Project 1", "why_now": "Test"}
        )
        
        dashboard.create_review_card(
            project_id="proj_002",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Project 2", "why_now": "Test"}
        )
        
        proj1_cards = dashboard.list_review_cards(project_id="proj_001")
        
        assert len(proj1_cards) == 1
        assert proj1_cards[0].project_id == "proj_001"
    
    def test_list_review_cards_by_type(self):
        """Should filter review cards by type"""
        dashboard = create_dashboard()
        
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Task", "why_now": "Test"}
        )
        
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.SKILL_INSTALL.value,
            context={"summary": "Skill", "why_now": "Test"}
        )
        
        task_reviews = dashboard.list_review_cards(gate_type=GateType.TASK_REVIEW.value)
        
        assert len(task_reviews) == 1
        assert task_reviews[0].gate_type == GateType.TASK_REVIEW.value
    
    def test_get_pending_reviews(self):
        """Should return all pending review cards"""
        dashboard = create_dashboard()
        
        for i in range(3):
            dashboard.create_review_card(
                project_id=f"proj_{i:03d}",
                gate_type=GateType.TASK_REVIEW.value,
                context={"summary": f"Card {i}", "why_now": "Test"}
            )
        
        pending = dashboard.get_pending_reviews()
        
        assert len(pending) == 3
    
    def test_approve_review_card(self):
        """Should approve a review card"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Test", "why_now": "Test"}
        )
        
        approved = dashboard.approve_review_card(card.id, "Looks good!")
        
        assert approved is not None
        assert approved.status == GateStatus.APPROVED.value
        assert approved.resolution["decision"] == "approved"
        assert approved.resolution["notes"] == "Looks good!"
        assert "resolved_at" in approved.resolution
    
    def test_reject_review_card(self):
        """Should reject a review card"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Test", "why_now": "Test"}
        )
        
        rejected = dashboard.reject_review_card(card.id, "Not ready yet")
        
        assert rejected is not None
        assert rejected.status == GateStatus.REJECTED.value
        assert rejected.resolution["decision"] == "rejected"
        assert rejected.resolution["notes"] == "Not ready yet"
    
    def test_modify_review_card(self):
        """Should modify a review card with constraints"""
        dashboard = create_dashboard()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Test", "why_now": "Test"}
        )
        
        constraints = ["must_verify", "limit_concurrency"]
        
        modified = dashboard.modify_review_card(
            card.id,
            "Approved with constraints",
            constraints
        )
        
        assert modified is not None
        assert modified.status == GateStatus.MODIFIED.value
        assert modified.resolution["decision"] == "modified"
        assert modified.resolution["constraints_added"] == constraints
    
    def test_review_stats(self):
        """Should return correct review statistics"""
        dashboard = create_dashboard()
        
        # Create various cards
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "1", "why_now": "Test"},
            risk_level="high"
        )
        
        card2 = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.SKILL_INSTALL.value,
            context={"summary": "2", "why_now": "Test"},
            risk_level="medium"
        )
        
        card3 = dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "3", "why_now": "Test"}
        )
        
        # Approve one
        dashboard.approve_review_card(card2.id)
        
        # Reject one
        dashboard.reject_review_card(card3.id, "Rejected")
        
        stats = dashboard.get_review_stats()
        
        assert stats["total_cards"] == 3
        assert stats["pending_count"] == 1
        assert stats["by_status"]["pending"] == 1
        assert stats["by_status"]["approved"] == 1
        assert stats["by_status"]["rejected"] == 1
        assert stats["by_type"]["task_review"] == 2
        assert stats["by_type"]["skill_install"] == 1
        assert stats["by_risk"]["high"] == 1
        assert stats["by_risk"]["medium"] == 1


class TestProjectPathGraph:
    """Tests for Project Path Graph"""
    
    def test_create_path_graph(self):
        """Should create path graph from tasks"""
        dashboard = create_dashboard()
        
        tasks = [
            {
                "id": "task_001",
                "title": "Implement Core",
                "state": "completed",
                "depends_on": []
            },
            {
                "id": "task_002",
                "title": "Build Feature",
                "state": "running",
                "depends_on": ["task_001"]
            },
            {
                "id": "task_003",
                "title": "Write Tests",
                "state": "pending",
                "depends_on": ["task_002"]
            }
        ]
        
        graph = dashboard.create_path_graph("proj_001", tasks)
        
        assert graph.project_id == "proj_001"
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2  # task_001 -> task_002, task_002 -> task_003
        
        # Check node statuses
        node_dict = {n.id: n for n in graph.nodes}
        assert node_dict["task_001"].status == "completed"
        assert node_dict["task_002"].status == "running"
        assert node_dict["task_003"].status == "pending"
        
        # Current node should be the running one
        assert graph.current_node_id == "task_002"
    
    def test_create_path_graph_with_artifacts(self):
        """Should create path graph with artifacts"""
        dashboard = create_dashboard()
        
        tasks = [
            {
                "id": "task_001",
                "title": "Implement Feature",
                "state": "completed",
                "depends_on": []
            }
        ]
        
        artifacts = [
            {
                "id": "artifact_001",
                "name": "feature.py",
                "task_id": "task_001"
            }
        ]
        
        graph = dashboard.create_path_graph("proj_001", tasks, artifacts)
        
        assert len(graph.nodes) == 2  # task + artifact
        
        # Check artifact node
        artifact_node = next(n for n in graph.nodes if n.node_type == "artifact")
        assert artifact_node.artifact_id == "artifact_001"
        assert artifact_node.status == "completed"
        
        # Check edge
        assert len(graph.edges) == 1
    
    def test_get_path_graph(self):
        """Should retrieve path graph by project ID"""
        dashboard = create_dashboard()
        
        tasks = [{"id": "task_001", "title": "Test", "state": "completed", "depends_on": []}]
        
        created = dashboard.create_path_graph("proj_001", tasks)
        retrieved = dashboard.get_path_graph("proj_001")
        
        assert retrieved is not None
        assert retrieved.project_id == created.project_id
    
    def test_update_path_graph_node(self):
        """Should update node status in path graph"""
        dashboard = create_dashboard()
        
        tasks = [
            {
                "id": "task_001",
                "title": "Task 1",
                "state": "running",
                "depends_on": []
            },
            {
                "id": "task_002",
                "title": "Task 2",
                "state": "pending",
                "depends_on": ["task_001"]
            }
        ]
        
        graph = dashboard.create_path_graph("proj_001", tasks)
        
        # Update task_001 to completed
        updated = dashboard.update_path_graph_node("proj_001", "task_001", "completed")
        
        assert updated is not None
        node_dict = {n.id: n for n in updated.nodes}
        assert node_dict["task_001"].status == "completed"
        # Current should now be task_002 (the next pending/running)
        assert updated.current_node_id == "task_002"
    
    def test_task_state_to_node_status_mapping(self):
        """Should correctly map task states to node statuses"""
        dashboard = create_dashboard()
        
        test_cases = [
            ("created", "pending"),
            ("queued", "running"),
            ("assigned", "running"),
            ("running", "running"),
            ("needs_review", "pending"),
            ("verifying", "running"),
            ("verified", "completed"),
            ("completed", "completed"),
            ("failed", "failed"),
            ("canceled", "blocked"),
            ("blocked", "blocked"),
        ]
        
        for task_state, expected_status in test_cases:
            tasks = [{"id": "task_test", "title": "Test", "state": task_state, "depends_on": []}]
            graph = dashboard.create_path_graph("proj_temp", tasks)
            
            assert graph.nodes[0].status == expected_status, f"Failed for state: {task_state}"


class TestWorkerMetrics:
    """Tests for Worker Metrics"""
    
    def test_update_worker_metrics(self):
        """Should update worker metrics"""
        dashboard = create_dashboard()
        
        dashboard.update_worker_metrics({
            "success_rate": 0.85,
            "total_tasks": 100,
            "idle_count": 3
        })
        
        metrics = dashboard.get_worker_metrics()
        
        assert metrics.success_rate == 0.85
        assert metrics.total_tasks == 100
        assert metrics.idle_count == 3
    
    def test_record_task_completion(self):
        """Should record task completion and update metrics"""
        dashboard = create_dashboard()
        
        dashboard.record_task_completion(success=True, latency_seconds=100.0)
        dashboard.record_task_completion(success=True, latency_seconds=200.0)
        dashboard.record_task_completion(success=False, latency_seconds=50.0)
        
        metrics = dashboard.get_worker_metrics()
        
        assert metrics.tasks_completed == 2
        assert metrics.tasks_failed == 1
        # Average should be (100 + 200) / 2 = 150
        assert metrics.avg_latency_seconds == 150.0


class TestSystemMetrics:
    """Tests for System Metrics"""
    
    def test_update_system_metrics(self):
        """Should update system metrics"""
        dashboard = create_dashboard()
        
        dashboard.update_system_metrics({
            "cpu_percent": 45.5,
            "memory_percent": 62.3,
            "disk_percent": 30.0
        })
        
        metrics = dashboard.get_system_metrics()
        
        assert metrics.cpu_percent == 45.5
        assert metrics.memory_percent == 62.3
        assert metrics.disk_percent == 30.0


class TestCostMetrics:
    """Tests for Cost Metrics"""
    
    def test_update_cost_metrics(self):
        """Should update cost metrics"""
        dashboard = create_dashboard()
        
        dashboard.update_cost_metrics({
            "daily_spend_usd": 25.50,
            "monthly_spend_usd": 500.0,
            "api_calls": 10000
        })
        
        metrics = dashboard.get_cost_metrics()
        
        assert metrics.daily_spend_usd == 25.50
        assert metrics.monthly_spend_usd == 500.0
        assert metrics.api_calls == 10000
    
    def test_record_api_call(self):
        """Should record API calls and update cost"""
        dashboard = create_dashboard()
        
        dashboard.record_api_call(cost_usd=0.01)
        dashboard.record_api_call(cost_usd=0.02)
        
        metrics = dashboard.get_cost_metrics()
        
        assert metrics.api_calls == 2
        assert metrics.daily_spend_usd == 0.03


class TestDashboardState:
    """Tests for Dashboard State"""
    
    def test_get_dashboard_state(self):
        """Should return complete dashboard state"""
        dashboard = create_dashboard()
        
        # Add some data
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Test", "why_now": "Test"}
        )
        
        dashboard.set_system_health("degraded")
        dashboard.set_execution_mode("turbo")
        
        state = dashboard.get_dashboard_state(
            ideas_count=10,
            projects_count=5,
            tasks_count=20,
            workers_idle=3
        )
        
        assert state.system_health == "degraded"
        assert state.execution_mode == "turbo"
        assert state.total_ideas == 10
        assert state.active_projects == 5
        assert state.pending_tasks == 20
        assert state.idle_workers == 3
        assert state.pending_reviews == 1
    
    def test_set_system_health(self):
        """Should set valid system health"""
        dashboard = create_dashboard()
        
        dashboard.set_system_health("degraded")
        assert dashboard.system_health == "degraded"
        
        dashboard.set_system_health("unhealthy")
        assert dashboard.system_health == "unhealthy"
    
    def test_set_execution_mode(self):
        """Should set valid execution mode"""
        dashboard = create_dashboard()
        
        dashboard.set_execution_mode("safe")
        assert dashboard.execution_mode == "safe"
        
        dashboard.set_execution_mode("normal")
        assert dashboard.execution_mode == "normal"
        
        dashboard.set_execution_mode("turbo")
        assert dashboard.execution_mode == "turbo"
    
    def test_set_execution_mode_invalid(self):
        """Should raise error for invalid mode"""
        dashboard = create_dashboard()
        
        with pytest.raises(ValueError):
            dashboard.set_execution_mode("invalid_mode")


class TestExportImport:
    """Tests for State Export/Import"""
    
    def test_export_state(self):
        """Should export complete dashboard state"""
        dashboard = create_dashboard()
        
        dashboard.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Test", "why_now": "Test"}
        )
        
        dashboard.set_execution_mode("turbo")
        
        tasks = [{"id": "task_001", "title": "Test", "state": "completed", "depends_on": []}]
        dashboard.create_path_graph("proj_001", tasks)
        
        state = dashboard.export_state()
        
        assert "review_cards" in state
        assert "path_graphs" in state
        assert "system_health" in state
        assert "execution_mode" in state
        assert len(state["review_cards"]) == 1
        assert state["execution_mode"] == "turbo"
    
    def test_import_state(self):
        """Should import dashboard state"""
        dashboard = create_dashboard()
        
        # Create source data
        source = create_dashboard()
        source.create_review_card(
            project_id="proj_001",
            gate_type=GateType.TASK_REVIEW.value,
            context={"summary": "Test", "why_now": "Test"}
        )
        source.set_execution_mode("turbo")
        
        exported = source.export_state()
        
        # Import into dashboard
        dashboard.import_state(exported)
        
        # Verify imported state
        cards = dashboard.list_review_cards()
        assert len(cards) == 1
        assert dashboard.execution_mode == "turbo"


class TestFactoryFunctions:
    """Tests for factory functions"""
    
    def test_get_dashboard_singleton(self):
        """Should return same instance for get_dashboard"""
        dashboard1 = get_dashboard()
        dashboard2 = get_dashboard()
        
        assert dashboard1 is dashboard2
    
    def test_create_dashboard_new_instance(self):
        """Should create new instance with create_dashboard"""
        dashboard = create_dashboard()
        
        assert isinstance(dashboard, DashboardAPI)


class TestReviewCardTypes:
    """Tests for Review Card types"""
    
    def test_all_review_card_types(self):
        """Should support all defined card types"""
        dashboard = create_dashboard()
        
        types = [
            GateType.TASK_REVIEW.value,
            GateType.SKILL_INSTALL.value,
            GateType.CONNECTION_SCOPE.value,
            GateType.POLICY_CHANGE.value,
            GateType.KPI_FAILURE.value,
            GateType.REPO_WRITE.value,
        ]
        
        for gate_type in types:
            card = dashboard.create_review_card(
                project_id="proj_001",
                gate_type=gate_type,
                context={"summary": "Test", "why_now": "Test"}
            )
            assert card.gate_type == gate_type


class TestEdgeCases:
    """Tests for edge cases"""
    
    def test_get_nonexistent_review_card(self):
        """Should return None for nonexistent card"""
        dashboard = create_dashboard()
        
        result = dashboard.get_review_card("gate_nonexistent")
        
        assert result is None
    
    def test_approve_nonexistent_card(self):
        """Should return None when approving nonexistent card"""
        dashboard = create_dashboard()
        
        result = dashboard.approve_review_card("gate_nonexistent")
        
        assert result is None
    
    def test_get_nonexistent_path_graph(self):
        """Should return None for nonexistent path graph"""
        dashboard = create_dashboard()
        
        result = dashboard.get_path_graph("proj_nonexistent")
        
        assert result is None
    
    def test_update_nonexistent_path_graph(self):
        """Should return None when updating nonexistent graph"""
        dashboard = create_dashboard()
        
        result = dashboard.update_path_graph_node("proj_nonexistent", "node_001", "completed")
        
        assert result is None
    
    def test_empty_review_list(self):
        """Should return empty list when no review cards"""
        dashboard = create_dashboard()
        
        result = dashboard.list_review_cards()
        
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
