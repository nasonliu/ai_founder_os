"""
Experience Ledger Module

Manages the system knowledge base with experience storage, retrieval, and XP credits.
The Experience Ledger enables workers to learn from past successes and failures,
promoting reusable solutions across the AI organization.
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

# Configure logging
logging = logging.getLogger(__name__)


class ExperienceCategory(Enum):
    """Experience problem categories"""
    BUILD = "build"
    DEPENDENCY = "dependency"
    RUNTIME = "runtime"
    LOGIC = "logic"
    TEST = "test"
    ENV = "env"
    NETWORK = "network"
    SECURITY = "security"


class ExperienceStatus(Enum):
    """Experience status"""
    SOLVED = "solved"
    PARTIAL = "partial"
    EXPIRED = "expired"


@dataclass
class Problem:
    """Problem description in an experience"""
    title: str
    symptoms: List[str] = field(default_factory=list)
    error_signatures: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "symptoms": self.symptoms,
            "error_signatures": self.error_signatures
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Problem':
        return cls(
            title=data.get("title", ""),
            symptoms=data.get("symptoms", []),
            error_signatures=data.get("error_signatures", [])
        )


@dataclass
class Context:
    """Context information for an experience"""
    where: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    related_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "where": self.where,
            "conditions": self.conditions,
            "related_tasks": self.related_tasks
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Context':
        return cls(
            where=data.get("where"),
            conditions=data.get("conditions", []),
            related_tasks=data.get("related_tasks", [])
        )


@dataclass
class Solution:
    """Solution description for an experience"""
    steps: List[str] = field(default_factory=list)
    patch_hint: Optional[str] = None
    validation: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": self.steps,
            "patch_hint": self.patch_hint,
            "validation": self.validation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Solution':
        return cls(
            steps=data.get("steps", []),
            patch_hint=data.get("patch_hint"),
            validation=data.get("validation", [])
        )


@dataclass
class ReusablePattern:
    """Reusable pattern information"""
    when_to_apply: Optional[str] = None
    template: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "when_to_apply": self.when_to_apply,
            "template": self.template
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReusablePattern':
        return cls(
            when_to_apply=data.get("when_to_apply"),
            template=data.get("template")
        )


@dataclass
class Contributor:
    """Contributor information for an experience"""
    worker_id: Optional[str] = None
    credited_xp: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "worker_id": self.worker_id,
            "credited_xp": self.credited_xp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Contributor':
        return cls(
            worker_id=data.get("worker_id"),
            credited_xp=data.get("credited_xp", 0)
        )


@dataclass
class ReuseStats:
    """Reuse statistics for an experience"""
    count: int = 0
    reused_by_workers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "reused_by_workers": self.reused_by_workers
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReuseStats':
        return cls(
            count=data.get("count", 0),
            reused_by_workers=data.get("reused_by_workers", [])
        )


@dataclass
class Experience:
    """
    Experience entity representing a learned solution.
    
    This is the core data structure stored in the Experience Ledger,
    capturing problems, solutions, and their reusability.
    """
    id: str
    project_id: Optional[str]
    problem: Problem
    solution: Solution
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: Optional[Context] = None
    reusable_pattern: Optional[ReusablePattern] = None
    contributor: Optional[Contributor] = None
    reuse: ReuseStats = field(default_factory=ReuseStats)
    status: str = ExperienceStatus.SOLVED.value
    tags: List[str] = field(default_factory=list)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert experience to dictionary"""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "problem": self.problem.to_dict() if self.problem else None,
            "context": self.context.to_dict() if self.context else None,
            "solution": self.solution.to_dict() if self.solution else None,
            "reusable_pattern": self.reusable_pattern.to_dict() if self.reusable_pattern else None,
            "contributor": self.contributor.to_dict() if self.contributor else None,
            "reuse": self.reuse.to_dict(),
            "status": self.status,
            "tags": self.tags,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Experience':
        """Create experience from dictionary"""
        return cls(
            id=data["id"],
            project_id=data.get("project_id"),
            problem=Problem.from_dict(data["problem"]) if data.get("problem") else Problem(title=""),
            context=Context.from_dict(data["context"]) if data.get("context") else None,
            solution=Solution.from_dict(data["solution"]) if data.get("solution") else Solution(steps=[]),
            reusable_pattern=ReusablePattern.from_dict(data["reusable_pattern"]) if data.get("reusable_pattern") else None,
            contributor=Contributor.from_dict(data["contributor"]) if data.get("contributor") else None,
            reuse=ReuseStats.from_dict(data["reuse"]) if data.get("reuse") else ReuseStats(),
            status=data.get("status", ExperienceStatus.SOLVED.value),
            tags=data.get("tags", []),
            confidence=data.get("confidence", 1.0),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat())
        )

    def add_tag(self, tag: str) -> None:
        """Add a tag to the experience"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now(timezone.utc).isoformat()

    def record_reuse(self, worker_id: str) -> None:
        """Record that this experience was reused by a worker"""
        self.reuse.count += 1
        if worker_id not in self.reuse.reused_by_workers:
            self.reuse.reused_by_workers.append(worker_id)
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class HelpRequest:
    """
    Help request from a worker seeking assistance.
    
    When a worker cannot find a solution in the ledger,
    it can发起 a help request that other workers can respond to.
    """
    id: str
    requester_worker_id: str
    project_id: Optional[str]
    task_id: str
    error_summary: str
    attempts: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    desired_output: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    response: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelpRequest':
        return cls(**data)

    def resolve(self, response: str) -> None:
        """Mark help request as resolved"""
        self.status = "resolved"
        self.response = response
        self.resolved_at = datetime.now(timezone.utc).isoformat()


class ExperienceLedger:
    """
    Experience Ledger manages the system's knowledge base.
    
    Responsibilities:
    - Store and retrieve experiences
    - Search by problem description, tags, or error signatures
    - Track reuse and credit XP to contributors
    - Handle help requests from workers
    
    Storage:
    - Main storage: JSONL file for append-only ledger
    - Index: By tags, problem keywords, worker type
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Experience Ledger.
        
        Args:
            storage_path: Path to the ledger storage file (JSONL format)
        """
        self.storage_path = storage_path
        self.experiences: Dict[str, Experience] = {}
        self.help_requests: Dict[str, HelpRequest] = {}
        self._index_by_tag: Dict[str, List[str]] = {}
        self._index_by_worker: Dict[str, List[str]] = {}
        
        # Load existing experiences
        self._load_ledger()
    
    def _load_ledger(self) -> None:
        """Load experiences from storage"""
        if not self.storage_path:
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        exp = Experience.from_dict(data)
                        self.experiences[exp.id] = exp
                        self._index_experience(exp)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.info(f"No existing ledger found or error loading: {e}")
    
    def _save_experience(self, experience: Experience) -> None:
        """Save a single experience to storage"""
        if not self.storage_path:
            return
        
        # Append to JSONL file (append-only)
        with open(self.storage_path, 'a') as f:
            f.write(json.dumps(experience.to_dict()) + '\n')
    
    def _index_experience(self, experience: Experience) -> None:
        """Index an experience for fast lookup"""
        # Index by tags
        for tag in experience.tags:
            if tag not in self._index_by_tag:
                self._index_by_tag[tag] = []
            if experience.id not in self._index_by_tag[tag]:
                self._index_by_tag[tag].append(experience.id)
        
        # Index by contributor worker
        if experience.contributor and experience.contributor.worker_id:
            worker_id = experience.contributor.worker_id
            if worker_id not in self._index_by_worker:
                self._index_by_worker[worker_id] = []
            if experience.id not in self._index_by_worker[worker_id]:
                self._index_by_worker[worker_id].append(experience.id)
    
    def add_experience(
        self,
        project_id: Optional[str],
        problem: Problem,
        solution: Solution,
        contributor_id: Optional[str] = None,
        context: Optional[Context] = None,
        reusable_pattern: Optional[ReusablePattern] = None,
        tags: List[str] = None,
        error_signatures: List[str] = None,
        conditions: List[str] = None
    ) -> Experience:
        """
        Add a new experience to the ledger.
        
        Args:
            project_id: Associated project ID
            problem: Problem description
            solution: Solution description
            contributor_id: Worker ID who contributed this experience
            context: Additional context
            reusable_pattern: Reusable pattern information
            tags: Tags for categorization
            error_signatures: Error signatures for matching
            conditions: Conditions under which this solution applies
            
        Returns:
            Created Experience instance
        """
        # Generate ID
        exp_id = f"exp_{uuid.uuid4().hex[:12]}"
        
        # Build problem with error signatures if provided
        problem_obj = Problem(
            title=problem.title,
            symptoms=problem.symptoms,
            error_signatures=error_signatures or []
        )
        
        # Build context if provided
        context_obj = None
        if context or conditions:
            context_obj = Context(
                where=context.where if context else None,
                conditions=conditions or [],
                related_tasks=context.related_tasks if context else []
            )
        
        # Build contributor
        contributor = None
        if contributor_id:
            contributor = Contributor(worker_id=contributor_id, credited_xp=0)
        
        # Create experience
        experience = Experience(
            id=exp_id,
            project_id=project_id,
            problem=problem_obj,
            solution=solution,
            context=context_obj,
            reusable_pattern=reusable_pattern,
            contributor=contributor,
            tags=tags or [],
            status=ExperienceStatus.SOLVED.value
        )
        
        # Store and index
        self.experiences[exp_id] = experience
        self._index_experience(experience)
        
        # Persist
        self._save_experience(experience)
        
        logging.info(f"Added experience: {exp_id}")
        
        return experience
    
    def get_experience(self, exp_id: str) -> Optional[Experience]:
        """Get an experience by ID"""
        return self.experiences.get(exp_id)
    
    def search_by_tags(self, tags: List[str], limit: int = 10) -> List[Experience]:
        """
        Search experiences by tags.
        
        Args:
            tags: Tags to search for
            limit: Maximum number of results
            
        Returns:
            List of matching experiences
        """
        result_ids = set()
        
        for tag in tags:
            if tag in self._index_by_tag:
                result_ids.update(self._index_by_tag[tag])
        
        # Get experiences and sort by reuse count (most reused first)
        experiences = [
            self.experiences[exp_id] 
            for exp_id in result_ids 
            if exp_id in self.experiences
        ]
        
        experiences.sort(key=lambda e: e.reuse.count, reverse=True)
        
        return experiences[:limit]
    
    def search_by_error(self, error_message: str, limit: int = 10) -> List[Experience]:
        """
        Search experiences by error message/signature.
        
        Args:
            error_message: Error message to match
            limit: Maximum number of results
            
        Returns:
            List of matching experiences
        """
        results = []
        
        for exp in self.experiences.values():
            # Check error signatures
            for sig in exp.problem.error_signatures:
                if sig.lower() in error_message.lower():
                    results.append(exp)
                    break
            
            # Check symptoms
            if not any(e in results for e in [exp]):
                for symptom in exp.problem.symptoms:
                    if symptom.lower() in error_message.lower():
                        results.append(exp)
                        break
        
        # Sort by confidence and reuse count
        results.sort(key=lambda e: (e.confidence, e.reuse.count), reverse=True)
        
        return results[:limit]
    
    def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[Experience]:
        """
        Search experiences by keywords in problem title and symptoms.
        
        Args:
            keywords: Keywords to search for
            limit: Maximum number of results
            
        Returns:
            List of matching experiences
        """
        results = []
        
        keywords_lower = [k.lower() for k in keywords]
        
        for exp in self.experiences.values():
            # Check title
            title_match = any(k in exp.problem.title.lower() for k in keywords_lower)
            
            # Check symptoms
            symptom_match = any(
                k in symptom.lower() 
                for symptom in exp.problem.symptoms 
                for k in keywords_lower
            )
            
            # Check solution steps
            solution_match = any(
                k in step.lower() 
                for step in exp.solution.steps 
                for k in keywords_lower
            )
            
            if title_match or symptom_match or solution_match:
                results.append(exp)
        
        # Sort by reuse count
        results.sort(key=lambda e: e.reuse.count, reverse=True)
        
        return results[:limit]
    
    def find_solution(
        self,
        error_message: str = "",
        tags: List[str] = None,
        keywords: List[str] = None
    ) -> Optional[Experience]:
        """
        Find a solution for a given error or problem.
        
        This is the main entry point for workers seeking help.
        Searches in order: error signatures -> tags -> keywords
        
        Args:
            error_message: Error message to match
            tags: Tags to search by
            keywords: Keywords to search by
            
        Returns:
            Best matching experience or None
        """
        # Priority 1: Search by error signature
        if error_message:
            matches = self.search_by_error(error_message, limit=5)
            if matches:
                # Record the reuse
                return matches[0]
        
        # Priority 2: Search by tags
        if tags:
            matches = self.search_by_tags(tags, limit=5)
            if matches:
                return matches[0]
        
        # Priority 3: Search by keywords
        if keywords:
            matches = self.search_by_keywords(keywords, limit=5)
            if matches:
                return matches[0]
        
        return None
    
    def record_reuse(self, exp_id: str, worker_id: str) -> bool:
        """
        Record that an experience was reused.
        
        This credits XP to the contributor.
        
        Args:
            exp_id: Experience ID that was reused
            worker_id: Worker who reused the experience
            
        Returns:
            True if recorded successfully
        """
        exp = self.experiences.get(exp_id)
        if not exp:
            return False
        
        # Record reuse
        exp.record_reuse(worker_id)
        
        # Credit XP to contributor
        if exp.contributor:
            exp.contributor.credited_xp += 2  # +2 XP for reuse
        
        return True
    
    def create_help_request(
        self,
        requester_worker_id: str,
        task_id: str,
        error_summary: str,
        project_id: Optional[str] = None,
        attempts: List[str] = None,
        constraints: List[str] = None,
        desired_output: List[str] = None,
        tags: List[str] = None
    ) -> HelpRequest:
        """
        Create a new help request.
        
        Args:
            requester_worker_id: Worker requesting help
            task_id: Task ID that needs help
            error_summary: Summary of the error/problem
            project_id: Associated project ID
            attempts: What has already been tried
            constraints: Constraints on the solution
            desired_output: What kind of help is needed
            tags: Tags for categorization
            
        Returns:
            Created HelpRequest
        """
        help_id = f"help_{uuid.uuid4().hex[:12]}"
        
        request = HelpRequest(
            id=help_id,
            requester_worker_id=requester_worker_id,
            project_id=project_id,
            task_id=task_id,
            error_summary=error_summary,
            attempts=attempts or [],
            constraints=constraints or [],
            desired_output=desired_output or [],
            tags=tags or []
        )
        
        self.help_requests[help_id] = request
        
        logging.info(f"Created help request: {help_id}")
        
        return request
    
    def get_help_request(self, help_id: str) -> Optional[HelpRequest]:
        """Get a help request by ID"""
        return self.help_requests.get(help_id)
    
    def list_pending_help_requests(
        self,
        worker_type: Optional[str] = None
    ) -> List[HelpRequest]:
        """
        List pending help requests.
        
        Args:
            worker_type: Filter by worker type that can help
            
        Returns:
            List of pending help requests
        """
        pending = [
            r for r in self.help_requests.values()
            if r.status == "pending"
        ]
        
        return pending
    
    def resolve_help_request(
        self,
        help_id: str,
        response: str,
        responder_id: Optional[str] = None
    ) -> bool:
        """
        Resolve a help request with a response.
        
        Args:
            help_id: Help request ID
            response: Solution/response to the request
            responder_id: Worker who provided the response
            
        Returns:
            True if resolved successfully
        """
        request = self.help_requests.get(help_id)
        if not request:
            return False
        
        request.resolve(response)
        
        # Optionally create an experience from this help request
        if request.requester_worker_id and request.project_id:
            self.add_experience(
                project_id=request.project_id,
                problem=Problem(
                    title=request.error_summary,
                    symptoms=[request.error_summary]
                ),
                solution=Solution(
                    steps=[response]
                ),
                contributor_id=responder_id,
                tags=request.tags,
                conditions=request.constraints
            )
        
        return True
    
    def get_experiences_by_worker(self, worker_id: str) -> List[Experience]:
        """Get all experiences contributed by a worker"""
        if worker_id not in self._index_by_worker:
            return []
        
        return [
            self.experiences[exp_id]
            for exp_id in self._index_by_worker[worker_id]
            if exp_id in self.experiences
        ]
    
    def get_experiences_by_project(self, project_id: str) -> List[Experience]:
        """Get all experiences for a project"""
        return [
            exp for exp in self.experiences.values()
            if exp.project_id == project_id
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ledger statistics"""
        total_experiences = len(self.experiences)
        total_reuses = sum(exp.reuse.count for exp in self.experiences.values())
        total_help_requests = len(self.help_requests)
        pending_help = len([r for r in self.help_requests.values() if r.status == "pending"])
        
        # Top contributors
        worker_xp = {}
        for exp in self.experiences.values():
            if exp.contributor and exp.contributor.worker_id:
                worker_id = exp.contributor.worker_id
                worker_xp[worker_id] = worker_xp.get(worker_id, 0) + exp.contributor.credited_xp
        
        top_contributors = sorted(
            worker_xp.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Top tags
        tag_counts = {}
        for exp in self.experiences.values():
            for tag in exp.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_experiences": total_experiences,
            "total_reuses": total_reuses,
            "total_help_requests": total_help_requests,
            "pending_help_requests": pending_help,
            "top_contributors": [{"worker_id": w, "xp": x} for w, x in top_contributors],
            "top_tags": [{"tag": t, "count": c} for t, c in top_tags]
        }
    
    def cleanup_old_experiences(self, days: int = 90) -> int:
        """
        Clean up experiences older than specified days.
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of experiences removed
        """
        from datetime import timedelta
        
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        removed = 0
        
        to_remove = []
        for exp_id, exp in self.experiences.items():
            exp_date = datetime.fromisoformat(exp.created_at.replace('Z', '+00:00'))
            if exp_date < cutoff:
                to_remove.append(exp_id)
        
        for exp_id in to_remove:
            del self.experiences[exp_id]
            removed += 1
        
        return removed


# Default ledger instance
_default_ledger: Optional[ExperienceLedger] = None


def get_ledger(storage_path: Optional[str] = None) -> ExperienceLedger:
    """Get or create the default experience ledger"""
    global _default_ledger
    if _default_ledger is None:
        _default_ledger = ExperienceLedger(storage_path)
    return _default_ledger


def create_sample_experiences(ledger: ExperienceLedger) -> List[Experience]:
    """
    Create sample experiences for testing/demo.
    
    Returns list of created experiences
    """
    experiences = []
    
    # Sample 1: Import error
    experiences.append(ledger.add_experience(
        project_id="proj_sample",
        problem=Problem(
            title="ModuleNotFoundError when importing package",
            symptoms=["ModuleNotFoundError: No module named 'requests'", "ImportError"]
        ),
        solution=Solution(
            steps=["pip install requests", "Or add to requirements.txt"],
            validation=["Import requests succeeds"]
        ),
        contributor_id="worker_builder_01",
        tags=["importerror", "python", "dependencies"],
        error_signatures=["ModuleNotFoundError", "ImportError"]
    ))
    
    # Sample 2: Git merge conflict
    experiences.append(ledger.add_experience(
        project_id="proj_sample",
        problem=Problem(
            title="Git merge conflict in file",
            symptoms=["CONFLICT in git status", "Merge conflict markers"]
        ),
        solution=Solution(
            steps=["Open conflicting file", "Resolve conflicts manually", "git add .", "git commit"],
            patch_hint="Remove <<<<<<, ======, >>>>>>> markers"
        ),
        contributor_id="worker_builder_02",
        tags=["git", "merge", "conflict"],
        error_signatures=["CONFLICT", "merge conflict"]
    ))
    
    # Sample 3: Type error
    experiences.append(ledger.add_experience(
        project_id="proj_sample",
        problem=Problem(
            title="TypeError in Python function",
            symptoms=["TypeError: unsupported operand type(s) for +", "TypeError: 'int' object is not iterable"]
        ),
        solution=Solution(
            steps=["Check types of operands", "Add type conversion if needed", "Use isinstance() to validate"],
            validation=["Function executes without TypeError"]
        ),
        contributor_id="worker_builder_01",
        tags=["typeerror", "python", "runtime"],
        error_signatures=["TypeError"]
    ))
    
    return experiences


if __name__ == "__main__":
    # Demo usage
    import tempfile
    
    # Create temporary ledger
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        temp_path = f.name
    
    ledger = ExperienceLedger(storage_path=temp_path)
    
    # Create sample experiences
    experiences = create_sample_experiences(ledger)
    print(f"Created {len(experiences)} sample experiences")
    
    # Search for solution
    solution = ledger.find_solution(error_message="ModuleNotFoundError: No module named 'requests'")
    if solution:
        print(f"\nFound solution: {solution.problem.title}")
        print(f"Solution: {solution.solution.steps}")
    
    # Search by tags
    by_tags = ledger.search_by_tags(["git", "merge"])
    print(f"\nFound {len(by_tags)} experiences for tags 'git', 'merge'")
    
    # Get stats
    stats = ledger.get_stats()
    print(f"\nLedger stats: {stats}")
    
    # Clean up
    import os
    os.unlink(temp_path)
