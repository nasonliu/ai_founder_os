"""
AI Founder OS - Policy Engine Tests

Tests for the Policy Engine module including:
- Execution Policy
- Safety Policy
- Quality Policy
- Policy Engine orchestration
"""

import pytest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from policy.engine import (
    PolicyEngine,
    ExecutionPolicy,
    SafetyPolicy,
    QualityPolicy,
    ValidationResult,
    PolicyType,
    OperatingMode,
    IncidentSeverity,
    create_policy_engine,
    validate_task,
    check_secrets
)


class TestExecutionPolicy:
    """Tests for Execution Policy"""
    
    def test_task_with_all_required_fields_passes(self):
        """Task with all required fields should pass"""
        policy = ExecutionPolicy()
        
        task = {
            "goal": "Build a feature",
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [{"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True}],
            "risk_level": "low"
        }
        
        result = policy.evaluate({"task": task})
        
        assert result.passed
        assert result.result == ValidationResult.PASS
    
    def test_task_missing_goal_fails(self):
        """Task missing goal should fail"""
        policy = ExecutionPolicy()
        
        task = {
            "goal": "",  # Empty goal
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [{"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True}],
            "risk_level": "low"
        }
        
        result = policy.evaluate({"task": task})
        
        assert not result.passed
        assert any(v.rule == "missing_required_fields" for v in result.violations)
    
    def test_task_without_validators_fails(self):
        """Task without validators should fail"""
        policy = ExecutionPolicy()
        
        task = {
            "goal": "Build a feature",
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [],
            "risk_level": "low"
        }
        
        result = policy.evaluate({"task": task})
        
        assert not result.passed
        assert any(v.rule == "no_validators" for v in result.violations)
    
    def test_task_without_blocking_validator_warns(self):
        """Task without blocking validator should warn"""
        policy = ExecutionPolicy()
        
        task = {
            "goal": "Build a feature",
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [{"id": "v1", "type": "unit_test", "command": "pytest", "blocking": False}],
            "risk_level": "low"
        }
        
        result = policy.evaluate({"task": task})
        
        # Should warn but not fail
        assert result.result == ValidationResult.WARN
    
    def test_task_with_retry_limit_exceeded_fails(self):
        """Task that exceeded retry limit should fail"""
        policy = ExecutionPolicy()
        
        task = {
            "goal": "Build a feature",
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [{"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True}],
            "risk_level": "low",
            "retry_count": 5  # Exceeds default limit of 3
        }
        
        result = policy.evaluate({"task": task})
        
        assert not result.passed
        assert any(v.rule == "retry_limit_exceeded" for v in result.violations)
    
    def test_concurrency_limit_enforced(self):
        """Concurrency limit should be enforced based on operating mode"""
        policy = ExecutionPolicy()
        
        # Test normal mode (max 3)
        result = policy.check_concurrency("normal", 3)
        assert result.result == ValidationResult.BLOCK
        
        # Test safe mode (max 1)
        result = policy.check_concurrency("safe", 2)
        assert result.result == ValidationResult.BLOCK
        
        # Test turbo mode (max 5)
        result = policy.check_concurrency("turbo", 5)
        assert result.result == ValidationResult.BLOCK
        
        # Test within limit
        result = policy.check_concurrency("normal", 2)
        assert result.passed
    
    def test_should_slowdown_triggered(self):
        """Auto-slowdown should trigger after threshold"""
        policy = ExecutionPolicy()
        
        assert policy.should_slowdown(3)  # Threshold is 3
        assert policy.should_slowdown(5)
        assert not policy.should_slowdown(2)


class TestSafetyPolicy:
    """Tests for Safety Policy"""
    
    def test_openai_key_detected(self):
        """OpenAI API key should be detected"""
        policy = SafetyPolicy()
        
        content = "My API key is sk-1234567890abcdefghijklmnop"
        
        violations = policy._detect_secrets(content)
        
        assert len(violations) > 0
        assert any("OpenAI" in v[0] for v in violations)
    
    def test_github_token_detected(self):
        """GitHub token should be detected"""
        policy = SafetyPolicy()
        
        content = "ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        
        violations = policy._detect_secrets(content)
        
        assert len(violations) > 0
    
    def test_no_secrets_passes(self):
        """Content without secrets should pass"""
        policy = SafetyPolicy()
        
        content = "This is normal content without any secrets."
        
        result = policy.evaluate({"content": content})
        
        assert result.passed
    
    def test_secret_in_log_context_blocked(self):
        """Secret in log context should be blocked"""
        policy = SafetyPolicy()
        
        content = "API key: sk-1234567890abcdefghijklmnop"
        
        result = policy.check_secret_leak(content, "log")
        
        assert not result.passed
        assert result.blocked
    
    def test_secret_in_git_context_blocked(self):
        """Secret in git context should be blocked"""
        policy = SafetyPolicy()
        
        content = "Token: ghp_abcdefghijklmnopqrstuvwxyz1234567890"
        
        result = policy.check_secret_leak(content, "git")
        
        assert not result.passed
    
    def test_capability_tokens_validated(self):
        """Worker capability tokens should be validated"""
        policy = SafetyPolicy()
        
        worker = {
            "worker_id": "worker_001",
            "capability_tokens": ["cap_code", "cap_test"]
        }
        
        # Sufficient capabilities
        result = policy._validate_capability_tokens(worker, ["cap_code"])
        assert result
        
        # Insufficient capabilities
        result = policy._validate_capability_tokens(worker, ["cap_code", "cap_deploy"])
        assert not result
    
    def test_network_access_blocked(self):
        """Network access to non-allowed domains should be blocked"""
        policy = SafetyPolicy()
        
        context = {
            "target": "https://evil.com/api",
            "allowed_domains": ["api.github.com", "api.openai.com"]
        }
        
        result = policy.evaluate(context)
        
        assert not result.passed
        assert any(v.rule == "network_blocked" for v in result.violations)
    
    def test_incident_creation(self):
        """Security incidents should be created properly"""
        policy = SafetyPolicy()
        
        incident = policy.create_incident(
            "secret_leak",
            "critical",
            {"content_preview": "sk-..."}
        )
        
        assert "id" in incident
        assert incident["type"] == "secret_leak"
        assert incident["severity"] == "critical"
        assert incident["status"] == "open"


class TestQualityPolicy:
    """Tests for Quality Policy"""
    
    def test_task_with_blocking_validator_passes(self):
        """Task with blocking validator should pass quality check"""
        policy = QualityPolicy()
        
        task = {
            "validators": [
                {"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True}
            ]
        }
        
        result = policy.evaluate({"task": task})
        
        assert result.passed
    
    def test_complete_evidence_pack_passes(self):
        """Complete evidence pack should pass"""
        policy = QualityPolicy()
        
        evidence = {
            "artifact_ids": ["artifact_001"],
            "validation": {"status": "pass"},
            "repro": {"commands": ["pytest tests/"]}
        }
        
        result = policy.evaluate({"evidence_pack": evidence})
        
        assert result.passed
    
    def test_incomplete_evidence_pack_fails(self):
        """Incomplete evidence pack should fail"""
        policy = QualityPolicy()
        
        evidence = {
            "artifact_ids": ["artifact_001"]
            # Missing validation and repro
        }
        
        result = policy.evaluate({"evidence_pack": evidence})
        
        assert not result.passed
        assert any(v.rule == "incomplete_evidence" for v in result.violations)
    
    def test_verifier_independence_check(self):
        """Verifier independence should be enforced"""
        policy = QualityPolicy()
        
        # Same builder and verifier
        result = policy.check_verifier_independence("worker_001", "worker_001")
        
        assert not result.passed
        assert any(v.rule == "verifier_not_independent" for v in result.violations)
    
    def test_verifier_independent_passes(self):
        """Independent verifier should pass"""
        policy = QualityPolicy()
        
        result = policy.check_verifier_independence("worker_builder_01", "worker_verifier_01")
        
        assert result.passed
    
    def test_kpi_gate_met_passes(self):
        """Met KPIs should pass the gate"""
        policy = QualityPolicy()
        
        project = {
            "kpis": [
                {"name": "test_coverage", "target": ">=80%", "validator": "coverage"}
            ]
        }
        
        kpi_results = {"test_coverage": 85}
        
        result = policy.evaluate({"project": project, "kpi_results": kpi_results})
        
        assert result.passed
    
    def test_kpi_gate_not_met_fails(self):
        """Unmet KPIs should fail the gate"""
        policy = QualityPolicy()
        
        project = {
            "kpis": [
                {"name": "test_coverage", "target": ">=80%", "validator": "coverage"}
            ]
        }
        
        kpi_results = {"test_coverage": 50}
        
        result = policy.evaluate({"project": project, "kpi_results": kpi_results})
        
        assert not result.passed
        assert any(v.rule == "kpi_not_met" for v in result.violations)


class TestPolicyEngine:
    """Tests for the main Policy Engine"""
    
    def test_engine_initialization(self):
        """Policy engine should initialize with all policies"""
        engine = create_policy_engine()
        
        assert engine.execution_policy is not None
        assert engine.safety_policy is not None
        assert engine.quality_policy is not None
        assert engine.operating_mode == OperatingMode.NORMAL
    
    def test_full_policy_evaluation_passes(self):
        """Valid task should pass all policy checks"""
        engine = create_policy_engine()
        
        task = {
            "goal": "Build feature",
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [{"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True}],
            "risk_level": "low"
        }
        
        project = {
            "id": "proj_001",
            "name": "Test Project",
            "operating_mode": "normal",
            "execution_limits": {"max_concurrency": 3, "retry_limit": 3},
            "kpis": []
        }
        
        result = engine.check_task_execution(task, project, current_concurrency=1)
        
        assert result.passed
    
    def test_policy_blocked_on_violation(self):
        """Engine should block on critical violations"""
        engine = create_policy_engine()
        
        # Task missing required fields
        task = {
            "goal": "",  # Invalid
            "validators": []  # Missing validators
        }
        
        project = {"id": "proj_001"}
        
        result = engine.check_task_execution(task, project)
        
        assert not result.passed
        assert result.blocked
    
    def test_worker_assignment_check(self):
        """Worker assignment should be validated"""
        engine = create_policy_engine()
        
        task = {
            "id": "task_001",
            "required_capabilities": ["cap_code", "cap_test"]
        }
        
        worker = {
            "worker_id": "worker_001",
            "capability_tokens": ["cap_code"]  # Missing cap_test
        }
        
        project = {"id": "proj_001"}
        
        result = engine.check_worker_assignment(task, worker, project)
        
        # Should fail on safety policy
        assert not result.passed
    
    def test_evidence_pack_check(self):
        """Evidence pack should be validated"""
        engine = create_policy_engine()
        
        evidence = {
            "artifact_ids": ["artifact_001"],
            "validation": {"status": "pass"},
            "repro": {"commands": ["pytest"]}
        }
        
        task = {"validators": []}
        
        result = engine.check_evidence_pack(evidence, task, "worker_001", "worker_002")
        
        assert result.passed
    
    def test_kpi_gate_check(self):
        """KPI gate should be validated"""
        engine = create_policy_engine()
        
        project = {
            "kpis": [{"name": "coverage", "target": ">=80%", "validator": "cov"}]
        }
        
        kpi_results = {"coverage": 90}
        
        result = engine.check_kpi_gate(project, kpi_results)
        
        assert result.passed
    
    def test_secret_leakage_check(self):
        """Secret leakage should be detected"""
        engine = create_policy_engine()
        
        content = "API key: sk-1234567890abcdefghijklmnop"
        
        result = engine.check_secret_leakage(content, "log")
        
        assert not result.passed
        assert result.blocked
    
    def test_slowdown_trigger(self):
        """Slowdown should trigger after consecutive failures"""
        engine = create_policy_engine()
        
        # Simulate 3 consecutive failures
        for i in range(3):
            result = engine.trigger_slowdown()
        
        assert result["slowdown_triggered"]
        assert engine.operating_mode == OperatingMode.SAFE
    
    def test_slowdown_reset(self):
        """Slowdown should reset properly"""
        engine = create_policy_engine()
        
        # Trigger slowdown
        for i in range(3):
            engine.trigger_slowdown()
        
        # Reset
        engine.reset_slowdown()
        
        assert engine.operating_mode == OperatingMode.NORMAL
        assert engine.consecutive_failures == 0
    
    def test_kill_switch(self):
        """Kill switch should activate properly"""
        engine = create_policy_engine()
        
        result = engine.activate_kill_switch("Critical security issue")
        
        assert result["kill_switch_armed"]
        assert engine.kill_switch_armed
    
    def test_violation_summary(self):
        """Violation summary should be generated"""
        engine = create_policy_engine()
        
        # Run some evaluations that will produce violations
        task = {"goal": "", "validators": []}
        project = {"id": "proj_001"}
        
        for i in range(5):
            engine.check_task_execution(task, project)
        
        summary = engine.get_violation_summary()
        
        assert "total_violations" in summary
        assert summary["total_violations"] > 0
    
    def test_status(self):
        """Engine status should be retrievable"""
        engine = create_policy_engine()
        
        status = engine.get_status()
        
        assert "operating_mode" in status
        assert "consecutive_failures" in status
        assert "kill_switch_armed" in status
        assert "violation_summary" in status


class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_validate_task(self):
        """validate_task helper should work"""
        task = {
            "goal": "Build feature",
            "inputs": {},
            "expected_artifact": {"type": "code"},
            "validators": [{"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True}],
            "risk_level": "low"
        }
        
        project = {
            "id": "proj_001",
            "operating_mode": "normal",
            "execution_limits": {"max_concurrency": 3}
        }
        
        result = validate_task(task, project)
        
        assert result is not None
        assert result.passed
    
    def test_check_secrets(self):
        """check_secrets helper should detect secrets"""
        # With secret
        result = check_secrets("sk-1234567890abcdefghijklmnop", "log")
        assert not result
        
        # Without secret
        result = check_secrets("normal content", "log")
        assert result


class TestPolicyEvaluationOrder:
    """Tests for policy evaluation order"""
    
    def test_execution_then_safety_then_quality(self):
        """Policies should be evaluated in order"""
        engine = create_policy_engine()
        
        # First violation in execution should block
        task = {"goal": ""}  # Missing goal
        project = {}
        
        result = engine.evaluate({
            "task": task,
            "project": project,
            "content": "normal"  # No secret issues
        }, policy_types=[
            PolicyType.EXECUTION,
            PolicyType.SAFETY,
            PolicyType.QUALITY
        ])
        
        # Should be blocked by execution policy
        assert not result.passed
        
        # Verify execution violations are present
        exec_violations = [v for v in result.violations 
                         if "ExecutionPolicy" in v.policy_type]
        assert len(exec_violations) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
