"""
AI Founder OS - Human Gate System Tests

Tests for the Human Gate System including:
- Review Card creation
- Approval workflow
- Gate trigger rules
- Integration with tasks and projects
"""

import pytest
import json
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from policy.human_gate import (
    HumanGate,
    ReviewCard,
    ReviewCardType,
    ReviewCardStatus,
    ReviewCardContext,
    GateTrigger,
    ResolutionDecision,
    create_human_gate,
    create_task_review_card,
    get_pending_approvals
)


class TestReviewCardCreation:
    """Tests for Review Card creation"""
    
    def test_create_task_review_card(self):
        """Create a basic task review card"""
        gate = HumanGate()
        
        context = ReviewCardContext(
            project_id="proj_001",
            task_id="task_001",
            summary="Review task: Implement Feature X",
            why_now="High-risk task requires approval",
            affected_entities=["task_001"],
            evidence_ids=["evp_001"]
        )
        
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "high")
        
        assert card.id.startswith("gate_task_review_")
        assert card.project_id == "proj_001"
        assert card.type == ReviewCardType.TASK_REVIEW
        assert card.risk_level == "high"
        assert card.status == ReviewCardStatus.PENDING
        assert card.context["summary"] == "Review task: Implement Feature X"
    
    def test_create_skill_install_card(self):
        """Create a skill installation review card"""
        gate = HumanGate()
        
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Install skill: GitHub Integration",
            why_now="New skill requested",
            affected_entities=["skill_github"],
            permissions=["exec", "network"],
            change="Install GitHub integration skill"
        )
        
        card = gate.create_review_card(ReviewCardType.SKILL_INSTALL, context, "medium")
        
        assert card.type == ReviewCardType.SKILL_INSTALL
        assert card.risk_level == "medium"
        assert "GitHub" in card.context["summary"]
    
    def test_create_connection_scope_card(self):
        """Create a connection scope review card"""
        gate = HumanGate()
        
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Add connection: OpenAI API",
            why_now="New API connection needed",
            permissions=["api_key"],
            scopes=["chat", "completions"]
        )
        
        card = gate.create_review_card(ReviewCardType.CONNECTION_SCOPE, context, "medium")
        
        assert card.type == ReviewCardType.CONNECTION_SCOPE
        assert card.impact_preview["permissions"] == ["api_key"]
    
    def test_card_id_unique(self):
        """Each card should have a unique ID"""
        gate = HumanGate()
        
        cards = []
        for i in range(5):
            context = ReviewCardContext(
                project_id="proj_001",
                summary=f"Task {i}"
            )
            card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
            cards.append(card)
        
        ids = [c.id for c in cards]
        assert len(ids) == len(set(ids))


class TestApprovalWorkflow:
    """Tests for approval workflow"""
    
    def test_approve_pending_card(self):
        """Approve a pending review card"""
        gate = HumanGate()
        
        # Create card
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Test approval"
        )
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        # Approve
        approved = gate.approve_card(card.id, "human_operator", "Looks good")
        
        assert approved.status == ReviewCardStatus.APPROVED
        assert approved.resolution["by"] == "human_operator"
        assert approved.resolution["decision"] == "approved"
        assert approved.resolution["notes"] == "Looks good"
        assert approved.resolution["resolved_at"] is not None
    
    def test_reject_pending_card(self):
        """Reject a pending review card"""
        gate = HumanGate()
        
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Test rejection"
        )
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "medium")
        
        rejected = gate.reject_card(
            card.id, 
            "human_operator", 
            "Not ready for review",
            constraints=["Need more testing"]
        )
        
        assert rejected.status == ReviewCardStatus.REJECTED
        assert rejected.resolution["decision"] == "rejected"
        assert rejected.resolution["constraints_added"] == ["Need more testing"]
    
    def test_modify_pending_card(self):
        """Modify and approve a card with constraints"""
        gate = HumanGate()
        
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Test modification"
        )
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "high")
        
        modified = gate.modify_card(
            card.id,
            "human_operator",
            "Approved with constraints",
            constraints=["max_retries=1", "require_code_review=true"]
        )
        
        assert modified.status == ReviewCardStatus.MODIFIED
        assert modified.resolution["decision"] == "modified"
        assert len(modified.resolution["constraints_added"]) == 2
    
    def test_cannot_approve_non_pending_card(self):
        """Cannot approve a card that is not pending"""
        gate = HumanGate()
        
        context = ReviewCardContext(project_id="proj_001", summary="Test")
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        # First approve
        gate.approve_card(card.id, "operator", "OK")
        
        # Try to approve again
        with pytest.raises(ValueError, match="not pending"):
            gate.approve_card(card.id, "operator", "OK again")
    
    def test_cannot_approve_nonexistent_card(self):
        """Cannot approve a card that doesn't exist"""
        gate = HumanGate()
        
        with pytest.raises(ValueError, match="not found"):
            gate.approve_card("gate_nonexistent", "operator", "OK")


class TestGateTriggers:
    """Tests for gate trigger logic"""
    
    def test_auto_trigger_for_skill_install(self):
        """Skill install should auto-trigger gate"""
        gate = HumanGate()
        
        should_trigger = gate.should_trigger_gate(
            ReviewCardType.SKILL_INSTALL,
            {"risk_level": "low"}
        )
        
        assert should_trigger is True
    
    def test_auto_trigger_for_repo_write(self):
        """Repo write should auto-trigger gate"""
        gate = HumanGate()
        
        should_trigger = gate.should_trigger_gate(
            ReviewCardType.REPO_WRITE,
            {"risk_level": "low"}
        )
        
        assert should_trigger is True
    
    def test_risk_based_trigger_for_task_review(self):
        """Task review should trigger based on risk"""
        gate = HumanGate()
        
        # Low risk should not trigger
        should_not_trigger = gate.should_trigger_gate(
            ReviewCardType.TASK_REVIEW,
            {"risk_level": "low"}
        )
        
        # High risk should trigger
        should_trigger = gate.should_trigger_gate(
            ReviewCardType.TASK_REVIEW,
            {"risk_level": "high"}
        )
        
        assert should_not_trigger is False
        assert should_trigger is True
    
    def test_manual_trigger_only_with_flag(self):
        """Manual trigger should only work with explicit flag"""
        gate = HumanGate()
        
        # Without flag
        should_not_trigger = gate.should_trigger_gate(
            ReviewCardType.TASK_REVIEW,
            {"risk_level": "low", "manual_trigger": False}
        )
        
        # With flag
        should_trigger = gate.should_trigger_gate(
            ReviewCardType.TASK_REVIEW,
            {"risk_level": "low", "manual_trigger": True}
        )
        
        assert should_not_trigger is False
        assert should_trigger is True


class TestTaskGate:
    """Tests for task gate checks"""
    
    def test_task_with_human_review_validator_triggers_gate(self):
        """Task with human_review validator should trigger gate"""
        gate = HumanGate()
        
        task = {
            "id": "task_001",
            "goal": "Implement feature",
            "risk_level": "low",
            "validators": [
                {"id": "v1", "type": "unit_test", "command": "pytest", "blocking": True},
                {"id": "v2", "type": "human_review", "blocking": True}
            ],
            "retry_count": 0
        }
        
        project = {
            "id": "proj_001",
            "execution_limits": {"retry_limit": 3}
        }
        
        card = gate.check_task_gate(task, project)
        
        assert card is not None
        assert card.type == ReviewCardType.TASK_REVIEW
    
    def test_high_risk_task_triggers_gate(self):
        """High risk task should trigger gate"""
        gate = HumanGate()
        
        task = {
            "id": "task_001",
            "goal": "Implement critical feature",
            "risk_level": "high",
            "validators": [
                {"id": "v1", "type": "unit_test", "blocking": True}
            ],
            "retry_count": 0
        }
        
        project = {
            "id": "proj_001",
            "execution_limits": {"retry_limit": 3}
        }
        
        card = gate.check_task_gate(task, project)
        
        assert card is not None
        assert card.risk_level == "high"
    
    def test_low_risk_task_no_gate(self):
        """Low risk task with regular validators should not trigger gate"""
        gate = HumanGate()
        
        task = {
            "id": "task_001",
            "goal": "Simple task",
            "risk_level": "low",
            "validators": [
                {"id": "v1", "type": "unit_test", "blocking": True}
            ],
            "retry_count": 0
        }
        
        project = {
            "id": "proj_001",
            "execution_limits": {"retry_limit": 3}
        }
        
        card = gate.check_task_gate(task, project)
        
        assert card is None
    
    def test_max_retry_exceeded_triggers_gate(self):
        """Task exceeding retry limit should trigger gate"""
        gate = HumanGate()
        
        task = {
            "id": "task_001",
            "goal": "Failing task",
            "risk_level": "medium",
            "validators": [
                {"id": "v1", "type": "unit_test", "blocking": True}
            ],
            "retry_count": 5  # Exceeds limit
        }
        
        project = {
            "id": "proj_001",
            "execution_limits": {"retry_limit": 3}
        }
        
        card = gate.check_task_gate(task, project)
        
        assert card is not None
        assert "exceeded" in card.context["why_now"].lower()


class TestSkillGate:
    """Tests for skill gate checks"""
    
    def test_skill_with_dangerous_permissions(self):
        """Skill with dangerous permissions triggers high risk gate"""
        gate = HumanGate()
        
        skill = {
            "id": "skill_exec",
            "name": "Execute Command",
            "permissions": ["exec", "file_write"]
        }
        
        project = {"id": "proj_001"}
        
        card = gate.check_skill_gate(skill, project)
        
        assert card is not None
        assert card.type == ReviewCardType.SKILL_INSTALL
        assert card.risk_level == "high"
    
    def test_skill_with_safe_permissions(self):
        """Skill with safe permissions triggers medium risk gate"""
        gate = HumanGate()
        
        skill = {
            "id": "skill_read",
            "name": "Read Files",
            "permissions": ["file_read"]
        }
        
        project = {"id": "proj_001"}
        
        card = gate.check_skill_gate(skill, project)
        
        assert card is not None
        assert card.risk_level == "medium"


class TestKpiGate:
    """Tests for KPI gate checks"""
    
    def test_critical_kpi_failure_triggers_high_risk(self):
        """Critical KPI failure should trigger high risk gate"""
        gate = HumanGate()
        
        project = {"id": "proj_001"}
        
        failed_kpis = [
            {"name": "uptime", "target": "99.9%", "actual": "95%", "severity": "critical"}
        ]
        
        card = gate.check_kpi_gate(project, failed_kpis)
        
        assert card is not None
        assert card.type == ReviewCardType.KPI_FAILURE
        assert card.risk_level == "high"
    
    def test_no_kpis_no_gate(self):
        """No failed KPIs should not trigger gate"""
        gate = HumanGate()
        
        project = {"id": "proj_001"}
        
        card = gate.check_kpi_gate(project, [])
        
        assert card is None


class TestRepoWriteGate:
    """Tests for repository write gate checks"""
    
    def test_sensitive_files_high_risk(self):
        """Write to sensitive files should trigger high risk gate"""
        gate = HumanGate()
        
        files = [".env", "src/credentials.py", "config/keys.json"]
        project = {"id": "proj_001"}
        
        card = gate.check_repo_write_gate("/repo", files, project)
        
        assert card is not None
        assert card.type == ReviewCardType.REPO_WRITE
        assert card.risk_level == "high"
    
    def test_regular_files_medium_risk(self):
        """Regular file writes should trigger medium risk gate"""
        gate = HumanGate()
        
        files = ["src/main.py", "tests/test_main.py"]
        project = {"id": "proj_001"}
        
        card = gate.check_repo_write_gate("/repo", files, project)
        
        assert card is not None
        assert card.risk_level == "medium"


class TestQueries:
    """Tests for querying review cards"""
    
    def test_get_pending_cards(self):
        """Get all pending cards"""
        gate = HumanGate()
        
        # Create multiple cards
        for i in range(3):
            context = ReviewCardContext(project_id="proj_001", summary=f"Task {i}")
            gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        # Approve one
        cards = gate.get_pending_cards()
        gate.approve_card(cards[0].id, "operator", "OK")
        
        pending = gate.get_pending_cards()
        
        assert len(pending) == 2
    
    def test_get_pending_cards_by_project(self):
        """Filter pending cards by project"""
        gate = HumanGate()
        
        # Create cards for different projects
        for i in range(2):
            context = ReviewCardContext(project_id="proj_001", summary=f"Task {i}")
            gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        context = ReviewCardContext(project_id="proj_002", summary="Other task")
        gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        pending_proj1 = gate.get_pending_cards("proj_001")
        
        assert len(pending_proj1) == 2
    
    def test_get_cards_by_project(self):
        """Get all cards for a project"""
        gate = HumanGate()
        
        # Create and approve some cards
        context1 = ReviewCardContext(project_id="proj_001", summary="Task 1")
        card1 = gate.create_review_card(ReviewCardType.TASK_REVIEW, context1, "low")
        gate.approve_card(card1.id, "operator", "OK")
        
        context2 = ReviewCardContext(project_id="proj_001", summary="Task 2")
        gate.create_review_card(ReviewCardType.TASK_REVIEW, context2, "low")
        
        cards = gate.get_cards_by_project("proj_001")
        
        assert len(cards) == 2
    
    def test_approval_summary(self):
        """Get approval summary"""
        gate = HumanGate()
        
        # Create cards
        for i in range(3):
            context = ReviewCardContext(project_id="proj_001", summary=f"Task {i}")
            gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        # Approve one
        pending = gate.get_pending_cards()
        gate.approve_card(pending[0].id, "operator", "OK")
        
        # Reject one
        gate.reject_card(pending[1].id, "operator", "Not OK")
        
        summary = gate.get_approval_summary()
        
        assert summary["total"] == 3
        assert summary["pending"] == 1
        assert summary["approved"] == 1
        assert summary["rejected"] == 1


class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_create_human_gate(self):
        """Test factory function"""
        gate = create_human_gate()
        
        assert gate is not None
        assert isinstance(gate, HumanGate)
    
    def test_create_task_review_card_convenience(self):
        """Test convenience function for task review card"""
        card = create_task_review_card(
            project_id="proj_001",
            task_id="task_001",
            summary="Quick review",
            risk_level="medium"
        )
        
        assert card.project_id == "proj_001"
        assert card.type == ReviewCardType.TASK_REVIEW
        assert card.risk_level == "medium"


class TestReviewCardSerialization:
    """Tests for ReviewCard serialization"""
    
    def test_to_dict(self):
        """Test converting card to dictionary"""
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Test card"
        )
        
        gate = HumanGate()
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "medium")
        
        card_dict = card.to_dict()
        
        assert card_dict["id"] == card.id
        assert card_dict["project_id"] == "proj_001"
        assert card_dict["type"] == "task_review"
        assert card_dict["risk_level"] == "medium"
        assert card_dict["status"] == "pending"
    
    def test_from_dict(self):
        """Test creating card from dictionary"""
        data = {
            "id": "gate_task_review_123",
            "project_id": "proj_001",
            "type": "task_review",
            "risk_level": "high",
            "status": "pending",
            "context": {"summary": "Test"},
            "proposal": {},
            "evidence_ids": [],
            "impact_preview": {},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        card = ReviewCard.from_dict(data)
        
        assert card.id == "gate_task_review_123"
        assert card.project_id == "proj_001"
        assert card.type == ReviewCardType.TASK_REVIEW
        assert card.risk_level == "high"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
