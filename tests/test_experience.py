"""
Unit tests for Experience Ledger Module

Tests experience storage, retrieval, XP credits, and help request handling.
"""
import pytest
import tempfile
import os
import json
from datetime import datetime

from src.experience.ledger import (
    ExperienceLedger,
    Experience,
    Problem,
    Context,
    Solution,
    ReusablePattern,
    Contributor,
    ReuseStats,
    HelpRequest,
    ExperienceCategory,
    ExperienceStatus,
    get_ledger,
    create_sample_experiences
)


class TestProblem:
    """Tests for Problem dataclass"""
    
    def test_problem_creation(self):
        problem = Problem(
            title="Test Error",
            symptoms=["error1", "error2"],
            error_signatures=["Error: test failed"]
        )
        
        assert problem.title == "Test Error"
        assert len(problem.symptoms) == 2
        assert problem.error_signatures[0] == "Error: test failed"
    
    def test_problem_to_dict(self):
        problem = Problem(title="Test", symptoms=["sym1"])
        
        result = problem.to_dict()
        
        assert result["title"] == "Test"
        assert result["symptoms"] == ["sym1"]
    
    def test_problem_from_dict(self):
        data = {"title": "Test", "symptoms": ["s1", "s2"], "error_signatures": []}
        
        problem = Problem.from_dict(data)
        
        assert problem.title == "Test"
        assert len(problem.symptoms) == 2


class TestContext:
    """Tests for Context dataclass"""
    
    def test_context_creation(self):
        ctx = Context(
            where="src/module.py",
            conditions=["python 3.11"],
            related_tasks=["task_001"]
        )
        
        assert ctx.where == "src/module.py"
        assert "python 3.11" in ctx.conditions
        assert "task_001" in ctx.related_tasks
    
    def test_context_to_dict(self):
        ctx = Context(where="test.py", conditions=["test"])
        
        result = ctx.to_dict()
        
        assert result["where"] == "test.py"
        assert result["conditions"] == ["test"]


class TestSolution:
    """Tests for Solution dataclass"""
    
    def test_solution_creation(self):
        solution = Solution(
            steps=["step1", "step2"],
            patch_hint="fix.patch",
            validation=["test passes"]
        )
        
        assert len(solution.steps) == 2
        assert solution.patch_hint == "fix.patch"
    
    def test_solution_to_dict(self):
        solution = Solution(steps=["do this"])
        
        result = solution.to_dict()
        
        assert result["steps"] == ["do this"]


class TestExperience:
    """Tests for Experience dataclass"""
    
    def test_experience_creation(self):
        problem = Problem(title="Error", symptoms=["symptom"])
        solution = Solution(steps=["fix"])
        
        exp = Experience(
            id="exp_001",
            project_id="proj_001",
            problem=problem,
            solution=solution
        )
        
        assert exp.id == "exp_001"
        assert exp.problem.title == "Error"
        assert exp.status == ExperienceStatus.SOLVED.value
    
    def test_experience_to_dict(self):
        problem = Problem(title="Error")
        solution = Solution(steps=["fix"])
        
        exp = Experience(
            id="exp_001",
            project_id="proj_001",
            problem=problem,
            solution=solution
        )
        
        result = exp.to_dict()
        
        assert result["id"] == "exp_001"
        assert result["problem"]["title"] == "Error"
    
    def test_experience_from_dict(self):
        data = {
            "id": "exp_001",
            "project_id": "proj_001",
            "problem": {"title": "Error", "symptoms": [], "error_signatures": []},
            "solution": {"steps": ["fix"], "patch_hint": None, "validation": []},
            "reuse": {"count": 0, "reused_by_workers": []},
            "status": "solved",
            "tags": ["test"],
            "confidence": 1.0,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        
        exp = Experience.from_dict(data)
        
        assert exp.id == "exp_001"
        assert exp.tags == ["test"]
    
    def test_record_reuse(self):
        problem = Problem(title="Error")
        solution = Solution(steps=["fix"])
        
        exp = Experience(
            id="exp_001",
            project_id="proj_001",
            problem=problem,
            solution=solution
        )
        
        exp.record_reuse("worker_001")
        
        assert exp.reuse.count == 1
        assert "worker_001" in exp.reuse.reused_by_workers
        
        exp.record_reuse("worker_001")  # Same worker again
        
        assert exp.reuse.count == 2  # Count increments, but worker list doesn't duplicate
    
    def test_add_tag(self):
        problem = Problem(title="Error")
        solution = Solution(steps=["fix"])
        
        exp = Experience(
            id="exp_001",
            project_id="proj_001",
            problem=problem,
            solution=solution
        )
        
        exp.add_tag("python")
        exp.add_tag("error")
        exp.add_tag("python")  # Duplicate
        
        assert len(exp.tags) == 2
        assert "python" in exp.tags


class TestHelpRequest:
    """Tests for HelpRequest dataclass"""
    
    def test_help_request_creation(self):
        request = HelpRequest(
            id="help_001",
            requester_worker_id="worker_001",
            project_id="proj_001",
            task_id="task_001",
            error_summary="Need help with error"
        )
        
        assert request.id == "help_001"
        assert request.status == "pending"
    
    def test_resolve_help_request(self):
        request = HelpRequest(
            id="help_001",
            requester_worker_id="worker_001",
            project_id="proj_001",
            task_id="task_001",
            error_summary="Need help"
        )
        
        request.resolve("Here is the solution")
        
        assert request.status == "resolved"
        assert request.response == "Here is the solution"
        assert request.resolved_at is not None
    
    def test_help_request_to_dict(self):
        request = HelpRequest(
            id="help_001",
            requester_worker_id="worker_001",
            project_id="proj_001",
            task_id="task_001",
            error_summary="Error"
        )
        
        result = request.to_dict()
        
        assert result["id"] == "help_001"
        assert result["status"] == "pending"


class TestExperienceLedger:
    """Tests for ExperienceLedger class"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage file"""
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def ledger(self, temp_storage):
        """Create an experience ledger with temporary storage"""
        return ExperienceLedger(storage_path=temp_storage)
    
    def test_ledger_creation(self, ledger):
        assert len(ledger.experiences) == 0
    
    def test_add_experience(self, ledger):
        problem = Problem(title="Test Error", symptoms=["symptom"])
        solution = Solution(steps=["fix this"])
        
        exp = ledger.add_experience(
            project_id="proj_001",
            problem=problem,
            solution=solution,
            contributor_id="worker_001",
            tags=["test", "error"]
        )
        
        assert exp.id.startswith("exp_")
        assert exp.id in ledger.experiences
        assert "test" in exp.tags
    
    def test_get_experience(self, ledger):
        problem = Problem(title="Error")
        solution = Solution(steps=["fix"])
        
        created = ledger.add_experience(
            project_id="proj_001",
            problem=problem,
            solution=solution
        )
        
        result = ledger.get_experience(created.id)
        
        assert result is not None
        assert result.id == created.id
    
    def test_get_nonexistent_experience(self, ledger):
        result = ledger.get_experience("exp_nonexistent")
        
        assert result is None
    
    def test_search_by_tags(self, ledger):
        # Add experiences with different tags
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 1"),
            solution=Solution(steps=["fix1"]),
            tags=["python", "error"]
        )
        
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 2"),
            solution=Solution(steps=["fix2"]),
            tags=["python", "runtime"]
        )
        
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 3"),
            solution=Solution(steps=["fix3"]),
            tags=["javascript", "error"]
        )
        
        # Search for python tag
        results = ledger.search_by_tags(["python"])
        
        assert len(results) == 2
    
    def test_search_by_error(self, ledger):
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(
                title="Import Error",
                symptoms=["ModuleNotFoundError"]
            ),
            solution=Solution(steps=["pip install"]),
            error_signatures=["ModuleNotFoundError", "ImportError"]
        )
        
        results = ledger.search_by_error("ModuleNotFoundError: No module named")
        
        assert len(results) >= 1
        assert "ModuleNotFoundError" in results[0].problem.error_signatures
    
    def test_search_by_keywords(self, ledger):
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Git merge conflict"),
            solution=Solution(steps=["resolve conflicts"])
        )
        
        results = ledger.search_by_keywords(["git", "merge"])
        
        assert len(results) >= 1
    
    def test_find_solution(self, ledger):
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Type Error"),
            solution=Solution(steps=["check types"]),
            error_signatures=["TypeError"],
            tags=["python", "type"]
        )
        
        # Find by error
        solution = ledger.find_solution(error_message="TypeError: unsupported operand")
        
        assert solution is not None
        assert solution.problem.title == "Type Error"
    
    def test_find_solution_no_match(self, ledger):
        solution = ledger.find_solution(error_message="Unknown error xyz123")
        
        assert solution is None
    
    def test_record_reuse(self, ledger):
        problem = Problem(title="Error")
        solution = Solution(steps=["fix"])
        
        exp = ledger.add_experience(
            project_id="proj_001",
            problem=problem,
            solution=solution,
            contributor_id="worker_001"
        )
        
        result = ledger.record_reuse(exp.id, "worker_002")
        
        assert result is True
        assert exp.reuse.count == 1
        assert exp.contributor.credited_xp == 2  # +2 for reuse
    
    def test_record_reuse_nonexistent(self, ledger):
        result = ledger.record_reuse("exp_nonexistent", "worker_001")
        
        assert result is False
    
    def test_create_help_request(self, ledger):
        request = ledger.create_help_request(
            requester_worker_id="worker_001",
            task_id="task_001",
            error_summary="Cannot solve this problem",
            project_id="proj_001",
            tags=["help", "urgent"]
        )
        
        assert request.id.startswith("help_")
        assert request.id in ledger.help_requests
        assert request.status == "pending"
    
    def test_get_help_request(self, ledger):
        created = ledger.create_help_request(
            requester_worker_id="worker_001",
            task_id="task_001",
            error_summary="Help needed"
        )
        
        result = ledger.get_help_request(created.id)
        
        assert result is not None
        assert result.id == created.id
    
    def test_list_pending_help_requests(self, ledger):
        # Create multiple requests
        ledger.create_help_request(
            requester_worker_id="worker_001",
            task_id="task_001",
            error_summary="Error 1"
        )
        
        ledger.create_help_request(
            requester_worker_id="worker_002",
            task_id="task_002",
            error_summary="Error 2"
        )
        
        pending = ledger.list_pending_help_requests()
        
        assert len(pending) == 2
    
    def test_resolve_help_request(self, ledger):
        request = ledger.create_help_request(
            requester_worker_id="worker_001",
            task_id="task_001",
            error_summary="Need help"
        )
        
        result = ledger.resolve_help_request(
            request.id,
            "Here is the solution",
            responder_id="worker_002"
        )
        
        assert result is True
        assert request.status == "resolved"
        assert request.response == "Here is the solution"
    
    def test_get_experiences_by_worker(self, ledger):
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 1"),
            solution=Solution(steps=["fix"]),
            contributor_id="worker_001"
        )
        
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 2"),
            solution=Solution(steps=["fix"]),
            contributor_id="worker_001"
        )
        
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 3"),
            solution=Solution(steps=["fix"]),
            contributor_id="worker_002"
        )
        
        worker1_exp = ledger.get_experiences_by_worker("worker_001")
        
        assert len(worker1_exp) == 2
    
    def test_get_experiences_by_project(self, ledger):
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 1"),
            solution=Solution(steps=["fix"])
        )
        
        ledger.add_experience(
            project_id="proj_002",
            problem=Problem(title="Error 2"),
            solution=Solution(steps=["fix"])
        )
        
        proj1_exp = ledger.get_experiences_by_project("proj_001")
        
        assert len(proj1_exp) == 1
    
    def test_get_stats(self, ledger):
        # Add some experiences
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 1"),
            solution=Solution(steps=["fix"]),
            contributor_id="worker_001",
            tags=["test"]
        )
        
        ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 2"),
            solution=Solution(steps=["fix"]),
            contributor_id="worker_002",
            tags=["test", "python"]
        )
        
        # Record a reuse
        exp = ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 3"),
            solution=Solution(steps=["fix"]),
            contributor_id="worker_001"
        )
        ledger.record_reuse(exp.id, "worker_002")
        
        # Create help request
        ledger.create_help_request(
            requester_worker_id="worker_001",
            task_id="task_001",
            error_summary="Need help"
        )
        
        stats = ledger.get_stats()
        
        assert stats["total_experiences"] == 3
        assert stats["total_reuses"] == 1
        assert stats["total_help_requests"] == 1
        assert stats["pending_help_requests"] == 1
    
    def test_persistence(self, temp_storage):
        """Test that experiences are persisted to disk"""
        ledger1 = ExperienceLedger(storage_path=temp_storage)
        
        problem = Problem(title="Test Error")
        solution = Solution(steps=["fix"])
        
        ledger1.add_experience(
            project_id="proj_001",
            problem=problem,
            solution=solution,
            contributor_id="worker_001",
            tags=["test"]
        )
        
        # Create new ledger instance with same storage
        ledger2 = ExperienceLedger(storage_path=temp_storage)
        
        assert len(ledger2.experiences) == 1
        
        # Verify the stored data
        exp = list(ledger2.experiences.values())[0]
        assert exp.problem.title == "Test Error"
        assert exp.tags == ["test"]


class TestHelperFunctions:
    """Tests for helper functions"""
    
    @pytest.fixture
    def temp_storage(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        yield path
        os.unlink(path)
    
    def test_create_sample_experiences(self, temp_storage):
        ledger = ExperienceLedger(storage_path=temp_storage)
        
        experiences = create_sample_experiences(ledger)
        
        assert len(experiences) == 3
        
        # Check tags
        all_tags = set()
        for exp in experiences:
            all_tags.update(exp.tags)
        
        assert "importerror" in all_tags
        assert "git" in all_tags
        assert "typeerror" in all_tags
    
    def test_get_ledger_singleton(self, temp_storage):
        """Test that get_ledger returns a singleton"""
        ledger1 = get_ledger(temp_storage)
        ledger2 = get_ledger(temp_storage)
        
        assert ledger1 is ledger2


class TestExperienceIntegration:
    """Integration tests for experience workflow"""
    
    @pytest.fixture
    def temp_storage(self):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def ledger(self, temp_storage):
        return ExperienceLedger(storage_path=temp_storage)
    
    def test_full_experience_workflow(self, ledger):
        """Test complete workflow: add -> find -> reuse -> credit"""
        # 1. Add experience
        exp = ledger.add_experience(
            project_id="proj_story_engine",
            problem=Problem(
                title="Import error with missing dependency",
                symptoms=["ModuleNotFoundError: No module named 'requests'"]
            ),
            solution=Solution(
                steps=["pip install requests", "Add to requirements.txt"]
            ),
            contributor_id="worker_builder_01",
            tags=["importerror", "python", "dependencies"],
            error_signatures=["ModuleNotFoundError"]
        )
        
        # 2. Worker searches for solution
        solution = ledger.find_solution(
            error_message="ModuleNotFoundError: No module named 'requests'"
        )
        
        assert solution is not None
        assert solution.id == exp.id
        
        # 3. Worker reuses the experience
        ledger.record_reuse(exp.id, "worker_builder_02")
        
        # 4. Verify XP credited
        assert exp.reuse.count == 1
        assert exp.contributor.credited_xp == 2
        
        # 5. Check stats
        stats = ledger.get_stats()
        
        assert stats["total_experiences"] == 1
        assert stats["total_reuses"] == 1
        assert stats["top_contributors"][0]["worker_id"] == "worker_builder_01"
        assert stats["top_contributors"][0]["xp"] == 2
    
    def test_help_request_workflow(self, ledger):
        """Test help request workflow"""
        # 1. Worker can't find solution
        solution = ledger.find_solution(error_message="Completely unknown error XYZ123")
        
        assert solution is None
        
        # 2. Worker creates help request
        help_req = ledger.create_help_request(
            requester_worker_id="worker_researcher_01",
            task_id="task_001",
            error_summary="Cannot connect to database",
            project_id="proj_db",
            attempts=["Checked connection string", "Verified credentials"],
            tags=["database", "connection"]
        )
        
        assert help_req.status == "pending"
        
        # 3. Another worker responds
        ledger.resolve_help_request(
            help_req.id,
            "Update your connection string to: postgresql://user:pass@host/db",
            responder_id="worker_builder_02"
        )
        
        # 4. Verify resolved
        assert help_req.status == "resolved"
        assert "postgresql" in help_req.response
        
        # 5. New experience was created from help request
        # (Only if contributor_id and project_id were provided)
        # In this case, they were, so an experience should be created
        assert len(ledger.experiences) >= 1
    
    def test_tag_search_with_sorting(self, ledger):
        """Test that results are sorted by reuse count"""
        # Add multiple experiences with same tag
        exp1 = ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 1"),
            solution=Solution(steps=["fix"]),
            tags=["python"]
        )
        
        exp2 = ledger.add_experience(
            project_id="proj_001",
            problem=Problem(title="Error 2"),
            solution=Solution(steps=["fix"]),
            tags=["python"]
        )
        
        # Reuse exp2 multiple times
        ledger.record_reuse(exp2.id, "worker_001")
        ledger.record_reuse(exp2.id, "worker_002")
        
        # Search - exp2 should be first due to higher reuse count
        results = ledger.search_by_tags(["python"])
        
        assert results[0].id == exp2.id
        assert results[0].reuse.count == 2
