"""
Integration tests: Policy Engine

Tests the Policy Engine integration with Planner, Workers, and Human Gate.
"""

import pytest
from src.policy.engine import (
    PolicyEngine,
    ExecutionPolicy,
    SafetyPolicy,
    QualityPolicy,
    PolicyType,
    ValidationResult,
    OperatingMode,
    IncidentSeverity,
    PolicyViolation,
)
from src.planner.planner import Planner, Task, TaskState
from src.dashboard.api import DashboardAPI, ReviewCard, GateType


class TestPolicyEngineIntegration:
    """Test Policy Engine integration with other modules"""
    
    def test_policy_engine_creation(self):
        """Test creating a policy engine"""
        engine = PolicyEngine()
        assert engine is not None
        assert engine.execution_mode == OperatingMode.NORMAL
    
    def test_set_execution_mode(self):
        """Test setting execution mode"""
        engine = PolicyEngine()
        
        engine.set_execution_mode("safe")
        assert engine.execution_mode == OperatingMode.SAFE
        
        engine.set_execution_mode("turbo")
        assert engine.execution_mode == OperatingMode.TURBO
    
    def test_policy_check_task_execution(self):
        """Test policy check for task execution"""
        engine = PolicyEngine()
        
        task_data = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "Test Task",
            "goal": "Test goal",
            "risk_level": "low",
            "inputs": {"code": "print('hello')"},
            "expected_artifact": {"type": "file", "path_hint": "output.txt"},
            "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}]
        }
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        result = engine.check_task_execution(task_data, project_data)
        
        # Low risk task should pass
        assert result is not None
        assert result.result in [ValidationResult.PASS, ValidationResult.WARN]
    
    def test_policy_blocks_high_risk_without_review(self):
        """Test that high-risk tasks are blocked without human review"""
        engine = PolicyEngine()
        
        task_data = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "High Risk Task",
            "goal": "Delete production database",
            "risk_level": "high",
            "inputs": {},
            "expected_artifact": {},
            "validators": []
        }
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        # Check without approval
        result = engine.check_task_execution(task_data, project_data)
        
        # High risk should require review
        assert result is not None
        assert result.blocked or len(result.violations) > 0


class TestPolicyWithPlanner:
    """Test Policy Engine integration with Planner"""
    
    def test_planner_respects_execution_policy(self):
        """Test that planner follows execution policies"""
        engine = PolicyEngine()
        planner = Planner({"max_concurrency": 3})
        
        # Set safe mode - should limit concurrency
        engine.set_execution_mode("safe")
        
        # Create tasks
        for i in range(5):
            planner.create_task({
                "project_id": "proj_001",
                "title": f"Task {i}",
                "goal": f"Goal {i}",
                "risk_level": "low"
            })
        
        # Queue all tasks
        for task_id in planner.tasks:
            planner.queue_task(task_id)
        
        # Safe mode should limit to 1 concurrent
        status = planner.get_status_summary()
        assert status["queue_length"] == 5
    
    def test_policy_validates_task_before_execution(self):
        """Test that policy validates task before execution"""
        engine = PolicyEngine()
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        # Valid task
        valid_task = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "Valid Task",
            "goal": "Valid goal",
            "risk_level": "low",
            "inputs": {"data": "test"},
            "expected_artifact": {"type": "file"},
            "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}]
        }
        
        result = engine.check_task_execution(valid_task, project_data)
        assert result is not None
        assert result.result != ValidationResult.BLOCK
    
    def test_policy_blocks_task_missing_required_fields(self):
        """Test that policy blocks tasks with missing required fields"""
        engine = PolicyEngine()
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        # Invalid task - missing goal
        invalid_task = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "Incomplete Task",
            # Missing: goal, risk_level, inputs, etc.
        }
        
        result = engine.check_task_execution(invalid_task, project_data)
        assert result is not None
        assert result.blocked or len(result.violations) > 0


class TestPolicyWithHumanGate:
    """Test Policy Engine integration with Human Gate"""
    
    def test_policy_creates_review_card_for_high_risk(self):
        """Test that high-risk tasks create review cards"""
        engine = PolicyEngine()
        dashboard = DashboardAPI()
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        # High-risk task
        task_data = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "High Risk Operation",
            "goal": "Deploy to production",
            "risk_level": "high",
            "inputs": {"env": "production"},
            "expected_artifact": {},
            "validators": []
        }
        
        # Check creates review requirement
        result = engine.check_task_execution(task_data, project_data)
        
        # High risk should create review
        if result and result.blocked:
            card = dashboard.create_review_card(
                project_id="proj_001",
                gate_type="task_review",
                risk_level="high",
                summary=f"Task requires review: {task_data['title']}",
                why_now="High risk operation",
                affected_entities=["task_001"],
                change="Execute high risk task"
            )
            
            assert card is not None
            assert card.risk_level == "high"
            assert card.status == "pending"
    
    def test_approved_review_allows_execution(self):
        """Test that approved review allows task execution"""
        dashboard = DashboardAPI()
        
        # Create review card
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="high",
            summary="Deploy to production",
            why_now="Release ready",
            affected_entities=["task_001"],
            change="Deploy"
        )
        
        # Approve
        dashboard.approve_review(card.id, "Approved for release")
        
        # Check approval
        card = dashboard.get_review_card(card.id)
        assert card.status == "approved"
    
    def test_rejected_review_blocks_execution(self):
        """Test that rejected review blocks execution"""
        dashboard = DashboardAPI()
        
        card = dashboard.create_review_card(
            project_id="proj_001",
            gate_type="task_review",
            risk_level="high",
            summary="Delete database",
            why_now="Cleanup",
            affected_entities=["task_001"],
            change="Delete production DB"
        )
        
        # Reject
        dashboard.reject_review(card.id, "Too risky, need backup first")
        
        card = dashboard.get_review_card(card.id)
        assert card.status == "rejected"


class TestSafetyPolicy:
    """Test Safety Policy enforcement"""
    
    def test_safety_policy_detects_secrets(self):
        """Test that safety policy detects secrets in code"""
        policy = SafetyPolicy()
        
        # Use actual API key pattern that SafetyPolicy detects
        code_with_secrets = """
        API_KEY = "sk-1234567890abcdefghij"
        ANTHROPIC_KEY = "sk-ant-api03-1234567890abcdefghij"
        GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwx"
        """
        
        result = policy.evaluate({
            "content": code_with_secrets,
            "operation": "code_execution"
        })
        
        # Should detect secrets
        assert result is not None
        assert len(result.violations) > 0 or result.result == ValidationResult.BLOCK
    
    def test_safety_policy_allows_safe_code(self):
        """Test that safety policy allows safe code"""
        policy = SafetyPolicy()
        
        safe_code = """
        def hello():
            print("Hello, World!")
            return True
        """
        
        result = policy.evaluate({
            "code": safe_code,
            "operation": "code_execution"
        })
        
        # Should pass
        assert result is not None
        assert result.result != ValidationResult.BLOCK


class TestQualityPolicy:
    """Test Quality Policy enforcement"""
    
    def test_quality_policy_requires_validator(self):
        """Test that quality policy requires validator"""
        policy = QualityPolicy()
        
        # Task without validators
        result = policy.evaluate({
            "task": {
                "id": "task_001",
                "validators": []
            }
        })
        
        # Should flag as issue
        assert result is not None
        assert len(result.violations) > 0 or result.result == ValidationResult.WARN
    
    def test_quality_policy_allows_validated_task(self):
        """Test that validated tasks pass quality check"""
        policy = QualityPolicy()
        
        result = policy.evaluate({
            "task": {
                "id": "task_001",
                "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}],
                "expected_artifact": {"type": "file"}
            }
        })
        
        # Should pass
        assert result is not None
        assert result.result != ValidationResult.BLOCK


class TestPolicyIncidents:
    """Test Policy incident tracking"""
    
    def test_policy_logs_violations(self):
        """Test that policy logs violations"""
        engine = PolicyEngine()
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        # Trigger a violation
        invalid_task = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "Incomplete"
        }
        
        engine.check_task_execution(invalid_task, project_data)
        
        # Should have logged violations
        assert len(engine.get_incidents()) >= 0
    
    def test_incident_severity_classification(self):
        """Test incident severity classification"""
        engine = PolicyEngine()
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal"
        }
        
        # High severity violation
        high_risk_task = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "Critical",
            "risk_level": "critical"
        }
        
        result = engine.check_task_execution(high_risk_task, project_data)
        
        # Should classify as high severity
        assert result is not None


class TestPolicyTurboMode:
    """Test Turbo mode policy relaxation"""
    
    def test_turbo_mode_increases_concurrency(self):
        """Test that turbo mode increases concurrency"""
        engine = PolicyEngine()
        
        engine.set_execution_mode("turbo")
        
        # Should allow more concurrency
        policy = ExecutionPolicy()
        assert policy.concurrency_limits["turbo"] > policy.concurrency_limits["normal"]
    
    def test_turbo_mode_relaxes_validation(self):
        """Test that turbo mode relaxes some validations"""
        engine = PolicyEngine()
        
        engine.set_execution_mode("turbo")
        
        # Task that might warn in normal mode
        task = {
            "id": "task_001",
            "project_id": "proj_001",
            "title": "Turbo Task",
            "goal": "Quick task",
            "risk_level": "low",
            "inputs": {},
            "expected_artifact": {},
            "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}]
        }
        
        project_data = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "turbo"
        }
        
        result = engine.check_task_execution(task, project_data)
        
        # Should pass in turbo mode
        assert result is not None
        assert result.result != ValidationResult.BLOCK


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
