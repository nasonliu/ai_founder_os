"""
AI Founder OS - Human Gate System

The Human Gate System manages review cards and approval workflows for human governance.
It creates Review Cards at key decision points and tracks their resolution.

Key features:
- Review Card generation for different gate types
- Approval workflow (pending -> approved/rejected/modified)
- Gate trigger rules based on risk levels and policy
- Integration with Policy Engine
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from abc import ABC, ABCMeta
import uuid
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReviewCardType(Enum):
    """Types of review cards that can be generated"""
    TASK_REVIEW = "task_review"
    SKILL_INSTALL = "skill_install"
    CONNECTION_SCOPE = "connection_scope"
    POLICY_CHANGE = "policy_change"
    KPI_FAILURE = "kpi_failure"
    REPO_WRITE = "repo_write"


class ReviewCardStatus(Enum):
    """Status of a review card"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class ResolutionDecision(Enum):
    """Decision made on a review card"""
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class GateTrigger(Enum):
    """When to trigger human gate"""
    AUTO = "auto"          # Always trigger automatically
    RISK_BASED = "risk_based"  # Trigger based on risk level
    MANUAL = "manual"       # Only manual trigger


# Gate trigger rules - which types require human approval
GATE_RULES = {
    ReviewCardType.TASK_REVIEW: {
        "auto_on_high_risk": True,
        "blocking_validators": True,
        "max_retry_exceeded": True
    },
    ReviewCardType.SKILL_INSTALL: {
        "auto_on_any": True,
        "requires_human": True
    },
    ReviewCardType.CONNECTION_SCOPE: {
        "auto_on_any": True,
        "requires_human": True
    },
    ReviewCardType.POLICY_CHANGE: {
        "auto_on_any": True,
        "requires_human": True
    },
    ReviewCardType.KPI_FAILURE: {
        "auto_on_any": True,
        "critical_kpis_only": False
    },
    ReviewCardType.REPO_WRITE: {
        "auto_on_any": True,
        "requires_human": True
    }
}


@dataclass
class ReviewCardContext:
    """Context for generating a review card"""
    project_id: str
    task_id: Optional[str] = None
    summary: str = ""
    why_now: str = ""
    affected_entities: List[str] = field(default_factory=list)
    change: str = ""
    options: List[Dict[str, Any]] = field(default_factory=list)
    recommended_option: Optional[str] = None
    evidence_ids: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    cost_estimate: Optional[str] = None
    time_estimate: Optional[str] = None


@dataclass
class ReviewCard:
    """
    Review Card for human approval.
    
    Generated when the system needs human decision at key governance points.
    """
    id: str
    project_id: str
    type: ReviewCardType
    risk_level: str  # "low", "medium", "high"
    status: ReviewCardStatus = ReviewCardStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    proposal: Dict[str, Any] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)
    impact_preview: Dict[str, Any] = field(default_factory=dict)
    resolution: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "type": self.type.value,
            "risk_level": self.risk_level,
            "status": self.status.value,
            "context": self.context,
            "proposal": self.proposal,
            "evidence_ids": self.evidence_ids,
            "impact_preview": self.impact_preview,
            "resolution": self.resolution,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReviewCard":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            project_id=data["project_id"],
            type=ReviewCardType(data["type"]),
            risk_level=data["risk_level"],
            status=ReviewCardStatus(data.get("status", "pending")),
            context=data.get("context", {}),
            proposal=data.get("proposal", {}),
            evidence_ids=data.get("evidence_ids", []),
            impact_preview=data.get("impact_preview", {}),
            resolution=data.get("resolution"),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z")
        )


class HumanGate:
    """
    Human Gate System for managing review cards and approval workflows.
    
    The Human Gate acts as a checkpoint before critical operations,
    ensuring human oversight at key decision points.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.review_cards: Dict[str, ReviewCard] = {}
        self.gate_triggers: Dict[str, GateTrigger] = {}
        
        # Initialize default gate triggers
        self._init_gate_triggers()
    
    def _init_gate_triggers(self):
        """Initialize default gate trigger rules"""
        default_triggers = {
            "task_review": GateTrigger.RISK_BASED,
            "skill_install": GateTrigger.AUTO,
            "connection_scope": GateTrigger.AUTO,
            "policy_change": GateTrigger.AUTO,
            "kpi_failure": GateTrigger.RISK_BASED,
            "repo_write": GateTrigger.AUTO
        }
        self.gate_triggers = self.config.get("gate_triggers", default_triggers)
    
    def _generate_card_id(self, card_type: ReviewCardType) -> str:
        """Generate unique review card ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"gate_{card_type.value}_{timestamp}_{unique_id}"
    
    def should_trigger_gate(self, card_type: ReviewCardType, 
                           context: Dict[str, Any]) -> bool:
        """
        Determine if a human gate should be triggered.
        
        Args:
            card_type: Type of review card
            context: Context including task, risk_level, etc.
            
        Returns:
            True if gate should be triggered
        """
        trigger = self.gate_triggers.get(card_type.value, GateTrigger.MANUAL)
        
        if trigger == GateTrigger.AUTO:
            return True
        
        if trigger == GateTrigger.MANUAL:
            # Manual trigger requires explicit flag
            return context.get("manual_trigger", False)
        
        # Risk-based trigger
        if trigger == GateTrigger.RISK_BASED:
            risk_level = context.get("risk_level", "low")
            # Trigger for medium and high risk
            if risk_level in ["medium", "high"]:
                return True
            # Also check for manual override
            return context.get("manual_trigger", False)
        
        return False
    
    def create_review_card(self, card_type: ReviewCardType, 
                          context: ReviewCardContext,
                          risk_level: str = "medium") -> ReviewCard:
        """
        Create a new review card.
        
        Args:
            card_type: Type of review card
            context: Context information for the review
            risk_level: Risk level of the operation
            
        Returns:
            Created ReviewCard
        """
        card_id = self._generate_card_id(card_type)
        
        # Build context dict
        context_dict = {
            "summary": context.summary,
            "why_now": context.why_now,
            "affected_entities": context.affected_entities
        }
        
        # Build proposal dict
        proposal_dict = {
            "change": context.change,
            "options": context.options,
            "recommended_option": context.recommended_option
        }
        
        # Build impact preview
        impact_preview = {
            "files": context.files,
            "permissions": context.permissions,
            "cost_estimate": context.cost_estimate,
            "time_estimate": context.time_estimate
        }
        
        card = ReviewCard(
            id=card_id,
            project_id=context.project_id,
            type=card_type,
            risk_level=risk_level,
            context=context_dict,
            proposal=proposal_dict,
            evidence_ids=context.evidence_ids,
            impact_preview=impact_preview
        )
        
        self.review_cards[card_id] = card
        
        logger.info(f"Review card created: {card_id} (type: {card_type.value}, risk: {risk_level})")
        
        return card
    
    def get_review_card(self, card_id: str) -> Optional[ReviewCard]:
        """Get a review card by ID"""
        return self.review_cards.get(card_id)
    
    def get_pending_cards(self, project_id: Optional[str] = None) -> List[ReviewCard]:
        """Get all pending review cards, optionally filtered by project"""
        cards = [c for c in self.review_cards.values() 
                 if c.status == ReviewCardStatus.PENDING]
        
        if project_id:
            cards = [c for c in cards if c.project_id == project_id]
        
        return cards
    
    def get_cards_by_project(self, project_id: str) -> List[ReviewCard]:
        """Get all review cards for a project"""
        return [c for c in self.review_cards.values() 
                if c.project_id == project_id]
    
    def approve_card(self, card_id: str, approver: str, 
                   notes: Optional[str] = None) -> ReviewCard:
        """
        Approve a review card.
        
        Args:
            card_id: ID of the review card
            approver: Who approved it
            notes: Optional notes
            
        Returns:
            Updated ReviewCard
            
        Raises:
            ValueError: If card not found or not pending
        """
        card = self.get_review_card(card_id)
        if not card:
            raise ValueError(f"Review card not found: {card_id}")
        
        if card.status != ReviewCardStatus.PENDING:
            raise ValueError(f"Card {card_id} is not pending (status: {card.status.value})")
        
        card.status = ReviewCardStatus.APPROVED
        card.resolution = {
            "by": approver,
            "decision": ResolutionDecision.APPROVED.value,
            "notes": notes or "",
            "resolved_at": datetime.utcnow().isoformat() + "Z"
        }
        card.updated_at = datetime.utcnow().isoformat() + "Z"
        
        logger.info(f"Review card approved: {card_id} by {approver}")
        
        return card
    
    def reject_card(self, card_id: str, approver: str,
                   notes: str, constraints: Optional[List[str]] = None) -> ReviewCard:
        """
        Reject a review card.
        
        Args:
            card_id: ID of the review card
            approver: Who rejected it
            notes: Reason for rejection
            constraints: Optional constraints added
            
        Returns:
            Updated ReviewCard
            
        Raises:
            ValueError: If card not found or not pending
        """
        card = self.get_review_card(card_id)
        if not card:
            raise ValueError(f"Review card not found: {card_id}")
        
        if card.status != ReviewCardStatus.PENDING:
            raise ValueError(f"Card {card_id} is not pending (status: {card.status.value})")
        
        card.status = ReviewCardStatus.REJECTED
        card.resolution = {
            "by": approver,
            "decision": ResolutionDecision.REJECTED.value,
            "notes": notes,
            "constraints_added": constraints or [],
            "resolved_at": datetime.utcnow().isoformat() + "Z"
        }
        card.updated_at = datetime.utcnow().isoformat() + "Z"
        
        logger.info(f"Review card rejected: {card_id} by {approver}")
        
        return card
    
    def modify_card(self, card_id: str, approver: str,
                   notes: str, constraints: List[str]) -> ReviewCard:
        """
        Modify and approve a review card with constraints.
        
        Args:
            card_id: ID of the review card
            approver: Who approved with modifications
            notes: Notes about the modifications
            constraints: Constraints added
            
        Returns:
            Updated ReviewCard
            
        Raises:
            ValueError: If card not found or not pending
        """
        card = self.get_review_card(card_id)
        if not card:
            raise ValueError(f"Review card not found: {card_id}")
        
        if card.status != ReviewCardStatus.PENDING:
            raise ValueError(f"Card {card_id} is not pending (status: {card.status.value})")
        
        card.status = ReviewCardStatus.MODIFIED
        card.resolution = {
            "by": approver,
            "decision": ResolutionDecision.MODIFIED.value,
            "notes": notes,
            "constraints_added": constraints,
            "resolved_at": datetime.utcnow().isoformat() + "Z"
        }
        card.updated_at = datetime.utcnow().isoformat() + "Z"
        
        logger.info(f"Review card modified: {card_id} by {approver}")
        
        return card
    
    def get_approval_summary(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of approval status"""
        cards = list(self.review_cards.values())
        
        if project_id:
            cards = [c for c in cards if c.project_id == project_id]
        
        total = len(cards)
        pending = len([c for c in cards if c.status == ReviewCardStatus.PENDING])
        approved = len([c for c in cards if c.status == ReviewCardStatus.APPROVED])
        rejected = len([c for c in cards if c.status == ReviewCardStatus.REJECTED])
        modified = len([c for c in cards if c.status == ReviewCardStatus.MODIFIED])
        
        by_type = {}
        for card in cards:
            type_key = card.type.value
            if type_key not in by_type:
                by_type[type_key] = {"total": 0, "pending": 0, "approved": 0, "rejected": 0, "modified": 0}
            by_type[type_key]["total"] += 1
            by_type[type_key][card.status.value] += 1
        
        return {
            "total": total,
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "modified": modified,
            "by_type": by_type
        }
    
    def check_task_gate(self, task: Dict, project: Dict,
                       evidence_pack: Optional[Dict] = None) -> Optional[ReviewCard]:
        """
        Check if a task requires human gate approval.
        
        This is called by the Planner when evaluating whether to proceed
        with a task that has blocking validators.
        
        Args:
            task: Task dictionary
            project: Project dictionary
            evidence_pack: Optional evidence pack from task execution
            
        Returns:
            ReviewCard if gate is triggered, None otherwise
        """
        # Check if task has blocking validators that need human review
        validators = task.get("validators", [])
        blocking_validators = [v for v in validators if v.get("blocking", False)]
        has_human_review = any(v.get("type") == "human_review" for v in validators)
        
        # Check retry count
        retry_count = task.get("retry_count", 0)
        retry_limit = project.get("execution_limits", {}).get("retry_limit", 3)
        max_retry_exceeded = retry_count >= retry_limit
        
        # Determine if gate should be triggered
        risk_level = task.get("risk_level", "low")
        task_id = task.get("id", "unknown")
        project_id = project.get("id", "unknown")
        
        context_dict = {
            "task_id": task_id,
            "risk_level": risk_level,
            "has_blocking_validators": len(blocking_validators) > 0,
            "has_human_review": has_human_review,
            "max_retry_exceeded": max_retry_exceeded
        }
        
        # Determine card type and if we should trigger
        # These conditions always trigger regardless of risk level:
        # - max_retry_exceeded
        # - has_human_review validator
        always_trigger = max_retry_exceeded or has_human_review
        
        if always_trigger:
            card_type = ReviewCardType.TASK_REVIEW
            # Use the risk level from task, but ensure at least medium
            card_risk = risk_level if risk_level in ["medium", "high"] else "medium"
        elif risk_level == "high":
            card_type = ReviewCardType.TASK_REVIEW
            card_risk = "high"
        else:
            return None  # No gate needed
        
        # Build context for review card
        context = ReviewCardContext(
            project_id=project_id,
            task_id=task_id,
            summary=task.get("title", task.get("goal", "Task Review")),
            why_now=_generate_why_now(card_type, context_dict),
            affected_entities=[task_id],
            evidence_ids=evidence_pack.get("evidence_ids", []) if evidence_pack else []
        )
        
        return self.create_review_card(card_type, context, card_risk)
    
    def check_skill_gate(self, skill: Dict, project: Dict) -> Optional[ReviewCard]:
        """
        Check if skill installation requires human approval.
        
        Args:
            skill: Skill manifest
            project: Project dictionary
            
        Returns:
            ReviewCard if gate is triggered, None otherwise
        """
        project_id = project.get("id", "unknown")
        skill_name = skill.get("name", "Unknown Skill")
        skill_id = skill.get("id", "unknown")
        
        # Check if skill has dangerous permissions
        permissions = skill.get("permissions", [])
        has_dangerous = any(p in permissions for p in ["exec", "file_write", "network"])
        
        context = ReviewCardContext(
            project_id=project_id,
            summary=f"Install skill: {skill_name}",
            why_now="New skill installation requested",
            affected_entities=[skill_id],
            change=f"Install skill '{skill_name}' with permissions: {permissions}",
            permissions=permissions
        )
        
        risk_level = "high" if has_dangerous else "medium"
        
        return self.create_review_card(ReviewCardType.SKILL_INSTALL, context, risk_level)
    
    def check_connection_gate(self, connection: Dict, project: Dict) -> Optional[ReviewCard]:
        """
        Check if new connection scope requires human approval.
        
        Args:
            connection: Connection configuration
            project: Project dictionary
            
        Returns:
            ReviewCard if gate is triggered, None otherwise
        """
        project_id = project.get("id", "unknown")
        connection_name = connection.get("name", "Unknown Connection")
        connection_type = connection.get("type", "api")
        
        permissions = connection.get("permissions", [])
        scopes = connection.get("scopes", [])
        
        context = ReviewCardContext(
            project_id=project_id,
            summary=f"Add connection: {connection_name}",
            why_now="New connection requested",
            affected_entities=[connection_name],
            change=f"Add {connection_type} connection with scopes: {scopes}",
            permissions=permissions,
            scopes=scopes
        )
        
        risk_level = "high" if connection_type in ["oauth", "webhook"] else "medium"
        
        return self.create_review_card(ReviewCardType.CONNECTION_SCOPE, context, risk_level)
    
    def check_kpi_gate(self, project: Dict, failed_kpis: List[Dict]) -> Optional[ReviewCard]:
        """
        Check if KPI failure requires human attention.
        
        Args:
            project: Project dictionary
            failed_kpis: List of failed KPIs
            
        Returns:
            ReviewCard if gate is triggered, None otherwise
        """
        if not failed_kpis:
            return None
        
        project_id = project.get("id", "unknown")
        
        # Determine risk level based on critical KPIs
        has_critical = any(kpi.get("severity") == "critical" for kpi in failed_kpis)
        risk_level = "high" if has_critical else "medium"
        
        kpi_names = [kpi.get("name", "unknown") for kpi in failed_kpis]
        
        context = ReviewCardContext(
            project_id=project_id,
            summary=f"KPI failure: {', '.join(kpi_names)}",
            why_now="One or more KPIs have failed to meet targets",
            affected_entities=kpi_names,
            change=f"Failed KPIs: {kpi_names}"
        )
        
        return self.create_review_card(ReviewCardType.KPI_FAILURE, context, risk_level)
    
    def check_repo_write_gate(self, repo_path: str, files: List[str],
                             project: Dict) -> Optional[ReviewCard]:
        """
        Check if repository write operations require human approval.
        
        Args:
            repo_path: Path to repository
            files: Files to be modified
            project: Project dictionary
            
        Returns:
            ReviewCard if gate is triggered, None otherwise
        """
        project_id = project.get("id", "unknown")
        
        # Check if any files are sensitive
        sensitive_patterns = [".env", "credentials", "secrets", "keys", "password"]
        has_sensitive = any(any(p in f.lower() for p in sensitive_patterns) for f in files)
        
        risk_level = "high" if has_sensitive else "medium"
        
        context = ReviewCardContext(
            project_id=project_id,
            summary=f"Write to repository: {len(files)} files",
            why_now="Repository write operation requested",
            affected_entities=files,
            files=files,
            change=f"Write {len(files)} files to {repo_path}"
        )
        
        return self.create_review_card(ReviewCardType.REPO_WRITE, context, risk_level)


def _generate_why_now(card_type: ReviewCardType, context: Dict[str, Any]) -> str:
    """Generate 'why now' explanation based on context"""
    if card_type == ReviewCardType.TASK_REVIEW:
        if context.get("max_retry_exceeded"):
            return "Task has exceeded maximum retry limit and requires human intervention"
        if context.get("has_human_review"):
            return "Task has a human review validator that requires approval"
        if context.get("risk_level") == "high":
            return "High-risk task requires human approval before execution"
        return "Task requires human review"
    return "Human approval required"


def create_human_gate(config: Optional[Dict] = None) -> HumanGate:
    """Factory function to create a Human Gate"""
    return HumanGate(config)


# Convenience functions
def create_task_review_card(project_id: str, task_id: str,
                            summary: str, risk_level: str = "medium") -> ReviewCard:
    """Quick creation of a task review card"""
    gate = create_human_gate()
    context = ReviewCardContext(
        project_id=project_id,
        task_id=task_id,
        summary=summary,
        why_now="Task review required"
    )
    return gate.create_review_card(ReviewCardType.TASK_REVIEW, context, risk_level)


def get_pending_approvals(project_id: str) -> List[Dict]:
    """Quick function to get pending approvals for a project"""
    gate = create_human_gate()
    cards = gate.get_pending_cards(project_id)
    return [card.to_dict() for card in cards]


if __name__ == "__main__":
    # Demo usage
    gate = create_human_gate()
    
    # Create a review card
    context = ReviewCardContext(
        project_id="proj_001",
        task_id="task_001",
        summary="Review task: Implement User Authentication",
        why_now="High-risk task requires human approval",
        affected_entities=["task_001", "src/auth.py"],
        change="Implement user authentication with JWT",
        options=[
            {"id": "opt1", "description": "Use JWT tokens", "tradeoffs": ["Simple but needs token refresh"]},
            {"id": "opt2", "description": "Use OAuth2", "tradeoffs": ["More secure but complex"]}
        ],
        recommended_option="opt1",
        evidence_ids=["evp_001"],
        files=["src/auth.py", "tests/auth_test.py"],
        cost_estimate="$0",
        time_estimate="2 hours"
    )
    
    card = gate.create_review_card(ReviewCardType.TASK_REVIEW, context, "high")
    print(f"Created card: {card.id}")
    print(f"Status: {card.status.value}")
    
    # Approve the card
    approved = gate.approve_card(card.id, "human_operator", "Looks good, proceed")
    print(f"\nApproved card: {approved.status.value}")
    print(f"Resolution: {approved.resolution}")
    
    # Get summary
    summary = gate.get_approval_summary()
    print(f"\nSummary: {summary}")
