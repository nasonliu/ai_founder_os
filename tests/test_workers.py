"""
Unit tests for Worker Registry Module

Tests worker registration, XP tracking, reputation, and scheduling.
"""
import pytest
import tempfile
import os
import json
from datetime import datetime

from src.workers.registry import (
    WorkerRegistry,
    Worker,
    WorkerType,
    WorkerStatus,
    XPStats,
    Reputation,
    WORKER_CAPABILITIES,
    get_registry,
    create_default_workers
)


class TestXPStats:
    """Tests for XPStats dataclass"""
    
    def test_initial_xp_is_zero(self):
        xp = XPStats()
        assert xp.total == 0
        assert xp.success == 0
        assert xp.failure == 0
        assert xp.reused == 0
    
    def test_add_success_increments_total(self):
        xp = XPStats()
        xp.add_success()
        assert xp.success == 1
        assert xp.total == 1
    
    def test_add_reuse_increments_total_by_2(self):
        xp = XPStats()
        xp.add_reuse()
        assert xp.reused == 1
        assert xp.total == 2
    
    def test_add_failure_decrements_total(self):
        xp = XPStats()
        xp.add_failure()
        assert xp.failure == 1
        assert xp.total == -1
    
    def test_xp_calculation_formula(self):
        """Test the XP formula: success * 1 + reused * 2 - failure * 1"""
        xp = XPStats()
        xp.success = 5
        xp.reused = 3
        xp.failure = 2
        assert xp.calculate_total() == 5 + 6 - 2  # 9
    
    def test_to_dict(self):
        xp = XPStats()
        xp.success = 2
        xp.reused = 1
        xp.failure = 1
        
        result = xp.to_dict()
        
        assert result["total"] == 2 + 2 - 1  # 3
        assert result["success"] == 2
        assert result["reused"] == 1
        assert result["failure"] == 1


class TestReputation:
    """Tests for Reputation dataclass"""
    
    def test_initial_reputation(self):
        rep = Reputation()
        assert rep.score == 1.0
        assert rep.success_rate == 0.0
        assert rep.avg_resolution_time_minutes == 0.0
        assert rep.total_tasks_completed == 0
    
    def test_update_from_completion_success(self):
        rep = Reputation()
        rep.update_from_completion(resolution_time_minutes=30.0, success=True)
        
        assert rep.success_rate == 1.0
        assert rep.avg_resolution_time_minutes == 30.0
        assert rep.total_tasks_completed == 1
    
    def test_update_from_completion_failure(self):
        rep = Reputation()
        rep.update_from_completion(resolution_time_minutes=15.0, success=False)
        
        assert rep.success_rate == 0.0
        assert rep.avg_resolution_time_minutes == 15.0
    
    def test_ema_for_multiple_completions(self):
        """Test exponential moving average for multiple task completions"""
        rep = Reputation()
        
        # First success
        rep.update_from_completion(10.0, True)
        assert rep.success_rate == 1.0
        
        # Second failure (EMA with alpha=0.1)
        # expected: 0.9 * 1.0 + 0.1 * 0.0 = 0.9
        rep.update_from_completion(20.0, False)
        assert abs(rep.success_rate - 0.9) < 0.001
        
        # Third success
        # expected: 0.9 * 0.9 + 0.1 * 1.0 = 0.81 + 0.1 = 0.91
        rep.update_from_completion(30.0, True)
        assert abs(rep.success_rate - 0.91) < 0.001
    
    def test_to_dict(self):
        rep = Reputation()
        rep.score = 0.85
        rep.success_rate = 0.85
        rep.avg_resolution_time_minutes = 25.5
        rep.total_tasks_completed = 10
        
        result = rep.to_dict()
        
        assert result["score"] == 0.85
        assert result["success_rate"] == 0.85
        assert result["avg_resolution_time_minutes"] == 25.5
        assert result["total_tasks_completed"] == 10


class TestWorker:
    """Tests for Worker dataclass"""
    
    def test_worker_creation(self):
        worker = Worker(
            worker_id="worker_builder_01",
            worker_type="builder",
            model_source="local_ollama:deepseek-8b"
        )
        
        assert worker.worker_id == "worker_builder_01"
        assert worker.worker_type == "builder"
        assert worker.model_source == "local_ollama:deepseek-8b"
        assert worker.status == "idle"
    
    def test_worker_auto_populates_capabilities(self):
        """Test that capabilities are auto-populated based on worker type"""
        builder = Worker(
            worker_id="test_builder",
            worker_type="builder",
            model_source="test"
        )
        
        assert "cap_code" in builder.capabilities
        assert "cap_test" in builder.capabilities
        
        researcher = Worker(
            worker_id="test_researcher",
            worker_type="researcher",
            model_source="test"
        )
        
        assert "cap_search" in researcher.capabilities
        assert "cap_analysis" in researcher.capabilities
    
    def test_worker_to_dict(self):
        worker = Worker(
            worker_id="test_worker",
            worker_type="builder",
            model_source="test"
        )
        
        result = worker.to_dict()
        
        assert result["worker_id"] == "test_worker"
        assert result["worker_type"] == "builder"
        assert result["model_source"] == "test"
        assert result["status"] == "idle"
        assert "xp" in result
        assert "reputation" in result
    
    def test_worker_from_dict(self):
        data = {
            "worker_id": "test_worker",
            "worker_type": "builder",
            "model_source": "test",
            "status": "idle",
            "xp": {"total": 5, "success": 5, "failure": 0, "reused": 0},
            "reputation": {"score": 1.0, "success_rate": 1.0, "avg_resolution_time_minutes": 10.0, "total_tasks_completed": 1}
        }
        
        worker = Worker.from_dict(data)
        
        assert worker.worker_id == "test_worker"
        assert worker.xp.total == 5
        assert worker.reputation.success_rate == 1.0


class TestWorkerRegistry:
    """Tests for WorkerRegistry class"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage file"""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def registry(self, temp_storage):
        """Create a worker registry with temporary storage"""
        return WorkerRegistry(storage_path=temp_storage)
    
    def test_registry_creation(self, registry):
        assert len(registry.workers) == 0
    
    def test_register_worker(self, registry):
        worker = registry.register_worker(
            worker_type="builder",
            model_source="local_ollama:deepseek-8b"
        )
        
        assert worker.worker_id.startswith("worker_builder_")
        assert worker.worker_type == "builder"
        assert worker.status == "idle"
        assert worker.worker_id in registry.workers
    
    def test_register_worker_with_custom_id(self, registry):
        worker = registry.register_worker(
            worker_type="builder",
            model_source="test",
            worker_id="my_custom_builder"
        )
        
        assert worker.worker_id == "my_custom_builder"
    
    def test_register_invalid_worker_type(self, registry):
        with pytest.raises(ValueError):
            registry.register_worker(
                worker_type="invalid_type",
                model_source="test"
            )
    
    def test_get_worker(self, registry):
        worker = registry.register_worker(
            worker_type="builder",
            model_source="test",
            worker_id="test_builder"
        )
        
        result = registry.get_worker("test_builder")
        
        assert result is not None
        assert result.worker_id == worker.worker_id
    
    def test_get_nonexistent_worker(self, registry):
        result = registry.get_worker("nonexistent")
        assert result is None
    
    def test_list_workers(self, registry):
        registry.register_worker("builder", "test1")
        registry.register_worker("researcher", "test2")
        registry.register_worker("builder", "test3")
        
        all_workers = registry.list_workers()
        assert len(all_workers) == 3
        
        builders = registry.list_workers(worker_type="builder")
        assert len(builders) == 2
    
    def test_list_workers_by_status(self, registry):
        w1 = registry.register_worker("builder", "test1")
        w2 = registry.register_worker("builder", "test2")
        
        registry.update_worker_status(w1.worker_id, "running")
        
        idle = registry.list_workers(status="idle")
        assert len(idle) == 1
        
        running = registry.list_workers(status="running")
        assert len(running) == 1
    
    def test_get_idle_workers(self, registry):
        registry.register_worker("builder", "test1")
        w2 = registry.register_worker("builder", "test2")
        
        registry.update_worker_status(w2.worker_id, "running")
        
        idle = registry.get_idle_workers()
        assert len(idle) == 1
    
    def test_update_worker_status(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.update_worker_status(worker.worker_id, "running")
        
        assert result is True
        assert worker.status == "running"
    
    def test_update_invalid_status(self, registry):
        worker = registry.register_worker("builder", "test")
        
        with pytest.raises(ValueError):
            registry.update_worker_status(worker.worker_id, "invalid_status")
    
    def test_assign_task(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.assign_task(worker.worker_id, "task_123")
        
        assert result is True
        assert worker.status == "assigned"
        assert worker.current_task_id == "task_123"
    
    def test_start_task(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.start_task(worker.worker_id)
        
        assert result is True
        assert worker.status == "running"
    
    def test_complete_task_success(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.complete_task(
            worker.worker_id,
            resolution_time_minutes=30.0,
            success=True
        )
        
        assert result is True
        assert worker.status == "idle"
        assert worker.xp.success == 1
        assert worker.xp.total == 1
        assert worker.reputation.success_rate == 1.0
    
    def test_complete_task_failure(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.complete_task(
            worker.worker_id,
            resolution_time_minutes=30.0,
            success=False
        )
        
        assert result is True
        assert worker.xp.failure == 1
        assert worker.xp.total == -1
        assert worker.reputation.success_rate == 0.0
    
    def test_record_experience_reuse(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.record_experience_reuse(worker.worker_id)
        
        assert result is True
        assert worker.xp.reused == 1
        assert worker.xp.total == 2
    
    def test_calculate_priority(self, registry):
        worker = registry.register_worker("builder", "test")
        
        priority = registry.calculate_priority(worker, task_type_hint="builder")
        
        # Base: 0 + idle bonus: 3 + success_rate: 0 + type match: 5 = 8
        assert priority == 8
    
    def test_calculate_priority_no_match(self, registry):
        worker = registry.register_worker("builder", "test")
        
        priority = registry.calculate_priority(worker, task_type_hint="researcher")
        
        # Base: 0 + idle bonus: 3 + success_rate: 0 + no type match = 3
        assert priority == 3
    
    def test_select_best_worker(self, registry):
        w1 = registry.register_worker("builder", "test1")
        w2 = registry.register_worker("builder", "test2")
        
        # Complete a task for w1 to give it XP
        registry.complete_task(w1.worker_id, 10.0, True)
        
        selected = registry.select_best_worker(task_type_hint="builder")
        
        # w1 should be selected due to higher XP
        assert selected.worker_id == w1.worker_id
    
    def test_select_best_worker_by_capabilities(self, registry):
        registry.register_worker("builder", "test")
        
        selected = registry.select_best_worker(
            required_capabilities=["cap_code", "cap_test"]
        )
        
        assert selected is not None
    
    def test_select_best_worker_no_idle(self, registry):
        worker = registry.register_worker("builder", "test")
        registry.update_worker_status(worker.worker_id, "running")
        
        selected = registry.select_best_worker()
        
        assert selected is None
    
    def test_get_worker_stats(self, registry):
        registry.register_worker("builder", "test1")
        registry.register_worker("researcher", "test2")
        
        stats = registry.get_worker_stats()
        
        assert stats["total_workers"] == 2
        assert stats["idle_workers"] == 2
        assert stats["type_breakdown"]["builder"] == 1
        assert stats["type_breakdown"]["researcher"] == 1
    
    def test_remove_worker(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.remove_worker(worker.worker_id)
        
        assert result is True
        assert worker.worker_id not in registry.workers
    
    def test_remove_nonexistent_worker(self, registry):
        result = registry.remove_worker("nonexistent")
        assert result is False
    
    def test_pause_worker(self, registry):
        worker = registry.register_worker("builder", "test")
        
        result = registry.pause_worker(worker.worker_id)
        
        assert result is True
        assert worker.status == "paused"
    
    def test_resume_worker(self, registry):
        worker = registry.register_worker("builder", "test")
        registry.pause_worker(worker.worker_id)
        
        result = registry.resume_worker(worker.worker_id)
        
        assert result is True
        assert worker.status == "idle"
    
    def test_persistence(self, temp_storage):
        """Test that workers are persisted to disk"""
        registry1 = WorkerRegistry(storage_path=temp_storage)
        worker = registry1.register_worker("builder", "test")
        
        # Create new registry instance with same storage
        registry2 = WorkerRegistry(storage_path=temp_storage)
        
        assert len(registry2.workers) == 1
        assert registry2.get_worker(worker.worker_id) is not None


class TestWorkerCapabilities:
    """Tests for worker capabilities mapping"""
    
    def test_all_worker_types_have_capabilities(self):
        for worker_type in WorkerType:
            assert worker_type in WORKER_CAPABILITIES
            assert len(WORKER_CAPABILITIES[worker_type]) > 0
    
    def test_builder_capabilities(self):
        caps = WORKER_CAPABILITIES[WorkerType.BUILDER]
        assert "cap_code" in caps
        assert "cap_test" in caps
    
    def test_researcher_capabilities(self):
        caps = WORKER_CAPABILITIES[WorkerType.RESEARCHER]
        assert "cap_search" in caps
        assert "cap_analysis" in caps
    
    def test_verifier_capabilities(self):
        caps = WORKER_CAPABILITIES[WorkerType.VERIFIER]
        assert "cap_test" in caps
        assert "cap_review" in caps
    
    def test_documenter_capabilities(self):
        caps = WORKER_CAPABILITIES[WorkerType.DOCUMENTER]
        assert "cap_doc" in caps
    
    def test_evaluator_capabilities(self):
        caps = WORKER_CAPABILITIES[WorkerType.EVALUATOR]
        assert "cap_metrics" in caps


class TestWorkerType:
    """Tests for WorkerType enum"""
    
    def test_all_worker_types(self):
        assert WorkerType.BUILDER.value == "builder"
        assert WorkerType.RESEARCHER.value == "researcher"
        assert WorkerType.DOCUMENTER.value == "documenter"
        assert WorkerType.VERIFIER.value == "verifier"
        assert WorkerType.EVALUATOR.value == "evaluator"


class TestWorkerStatus:
    """Tests for WorkerStatus enum"""
    
    def test_all_statuses(self):
        assert WorkerStatus.IDLE.value == "idle"
        assert WorkerStatus.ASSIGNED.value == "assigned"
        assert WorkerStatus.RUNNING.value == "running"
        assert WorkerStatus.VERIFYING.value == "verifying"
        assert WorkerStatus.COMPLETED.value == "completed"
        assert WorkerStatus.FAILED.value == "failed"
        assert WorkerStatus.BLOCKED.value == "blocked"
        assert WorkerStatus.PAUSED.value == "paused"
        assert WorkerStatus.ERROR.value == "error"


class TestHelperFunctions:
    """Tests for helper functions"""
    
    @pytest.fixture
    def temp_storage(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        os.unlink(path)
    
    def test_create_default_workers(self, temp_storage):
        registry = WorkerRegistry(storage_path=temp_storage)
        
        workers = create_default_workers(registry)
        
        assert len(workers) == 5
        
        types = [w.worker_type for w in workers]
        assert "builder" in types
        assert "researcher" in types
        assert "documenter" in types
        assert "verifier" in types
        assert "evaluator" in types
    
    def test_get_registry_singleton(self, temp_storage):
        """Test that get_registry returns a singleton"""
        reg1 = get_registry(temp_storage)
        reg2 = get_registry(temp_storage)
        
        assert reg1 is reg2
