"""
Unit tests for Human Gate System
"""

import pytest
from src.policy.human_gate import (
    HumanGate,
    ReviewCard,
    ReviewCardType,
    ReviewCardStatus,
    ResolutionDecision,
    GateTrigger,
    ReviewCardContext,
    create_human_gate
)


class TestReviewCard:
    """Test ReviewCard model"""
    
    def test_review_card_creation(self):
        """Test creating a review card"""
        card = ReviewCard(
            id="gate_001",
            project_id="proj_001",
            type=ReviewCardType.TASK_REVIEW,
            risk_level="high",
            context={"summary": "Test"},
            proposal={"change": "Test change"}
        )
        assert card.id == "gate_001"
        assert card.status == ReviewCardStatus.PENDING
    
    def test_to_dict(self):
        """Test serialization to dict"""
        card = ReviewCard(
            id="gate_001",
            project_id="proj_001",
            type=ReviewCardType.TASK_REVIEW,
            risk_level="low",
            context={"summary": "Test"},
            proposal={"change": "Test"}
        )
        d = card.to_dict()
        assert "id" in d
        assert d["project_id"] == "proj_001"


class TestHumanGate:
    """Test HumanGate system"""
    
    def test_create_human_gate(self):
        """Test creating a human gate system"""
        gate = create_human_gate()
        assert gate is not None
        assert len(gate.review_cards) == 0
    
    def test_create_review_card(self):
        """Test creating a review card"""
        gate = create_human_gate()
        
        context = ReviewCardContext(
            project_id="proj_001",
            summary="Install Skill",
            why_now="Need search capability",
            affected_entities=["skill_brave_search"],
            change="Install brave search skill",
            options=[],
            recommended_option=None
        )
        
        card = gate.create_review_card(
            card_type=ReviewCardType.SKILL_INSTALL,
            context=context,
            risk_level="high"
        )
        
        assert card.id in gate.review_cards
    
    def test_get_pending_cards(self):
        """Test getting pending cards"""
        gate = create_human_gate()
        
        context1 = ReviewCardContext("Test1", "Why1", [], "Change1", [], None)
        context2 = ReviewCardContext("Test2", "Why2", [], "Change2", [], None)
        
        gate.create_review_card(ReviewCardType.TASK_REVIEW, context1, "low")
        gate.create_review_card(ReviewCardType.SKILL_INSTALL, context2, "high")
        
        pending = gate.get_pending_cards()
        assert len(pending) == 2
    
    def test_approve_card(self):
        """Test approving a card"""
        gate = create_human_gate()
        
        context = ReviewCardContext("Test", "Why", [], "Change", [], None)
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        result = gate.approve_card(card.id, approver="human", notes="Approved")
        
        assert result.status == ReviewCardStatus.APPROVED
        assert result.resolution["decision"] == "approved"
    
    def test_reject_card(self):
        """Test rejecting a card"""
        gate = create_human_gate()
        
        context = ReviewCardContext("Test", "Why", [], "Change", [], None)
        card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "low")
        
        result = gate.reject_card(card.id, approver="human", notes="Rejected")
        
        assert result.status == ReviewCardStatus.REJECTED
        assert result.resolution["decision"] == "rejected"
    
    def test_should_trigger_gate(self):
        """Test gate trigger detection"""
        gate = create_human_gate()
        
        context = {"risk_level": "high"}
        
        assert gate.should_trigger_gate(ReviewCardType.SKILL_INSTALL, context) is True
        assert gate.should_trigger_gate(ReviewCardType.REPO_WRITE, context) is True
    
    def test_should_trigger_gate(self):
        """Test gate trigger detection"""
        gate = create_human_gate()
        
        context = {"risk_level": "high"}
        
        assert gate.should_trigger_gate(ReviewCardType.SKILL_INSTALL, context) is True
        assert gate.should_trigger_gate(ReviewCardType.REPO_WRITE, context) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
