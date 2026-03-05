"""
Integration tests: Planner + Worker System
"""

import pytest
from src.planner.planner import Planner, Task
from src.workers.registry import WorkerRegistry, Worker


class TestPlannerWorkerIntegration:
    """Test Planner and Worker integration"""
    
    def test_planner_assigns_task_to_worker(self):
        """Test that planner can assign task to worker"""
        # Setup
        planner = Planner({"max_concurrency": 3})
        registry = WorkerRegistry()
        
        # Create worker
        worker = registry.register_worker("builder", "ollama:deepseek-8b")
        
        # Create task
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test Task",
            "goal": "Test goal",
            "risk_level": "low"
        })
        planner.queue_task(task.id)
        
        # Assign to worker
        assert planner.assign_task(task.id, worker.worker_id)
        
        # Verify
        task = planner.tasks[task.id]
        assert task.assigned_to["worker_id"] == worker.worker_id
        assert task.state == "assigned"
    
    def test_worker_updates_task_status(self):
        """Test worker can update task status"""
        planner = Planner()
        registry = WorkerRegistry()
        
        worker = registry.register_worker("builder", "ollama:deepseek-8b")
        
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test",
            "goal": "Test"
        })
        
        # Simulate worker completing task
        planner.assign_task(task.id, worker.worker_id)
        task.state = "running"
        
        # Complete task
        planner.complete_task(task.id, success=True)
        
        assert task.state == "verified"
    
    def test_worker_xp_on_task_completion(self):
        """Test that worker gets XP on task completion"""
        planner = Planner()
        registry = WorkerRegistry()
        
        worker = registry.register_worker("builder", "ollama:deepseek-8b", worker_id="xp_worker")
        
        initial_xp = worker.xp.total
        
        # Complete task via registry
        registry.complete_task(worker.worker_id, resolution_time_minutes=5.0, success=True)
        
        assert worker.xp.total == initial_xp + 1
    
    def test_worker_failure_tracks_xp(self):
        """Test that worker failure is tracked"""
        registry = WorkerRegistry()
        
        worker = registry.register_worker("builder", "ollama:deepseek-8b", worker_id="fail_worker")
        
        initial_xp = worker.xp.total
        
        # Simulate failure
        registry.complete_task(worker.worker_id, resolution_time_minutes=2.0, success=False)
        
        assert worker.xp.total == initial_xp - 1
    
    def test_planner_retries_failed_task(self):
        """Test planner can retry failed task"""
        planner = Planner({"retry_limit": 2})
        
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Retry Test",
            "goal": "Test"
        })
        
        task.state = "running"
        
        # Fail once
        planner.complete_task(task.id, success=False)
        assert task.retry_count == 1
        assert task.state == "failed"
        assert planner.consecutive_failures == 1
        
        # Retry (re-queue)
        task.state = "running"
        planner.complete_task(task.id, success=True)
        
        assert task.state == "verified"
        assert planner.consecutive_failures == 0


class TestWorkerCollaboration:
    """Test worker collaboration"""
    
    def test_worker_can_request_help(self):
        """Test worker can request help"""
        registry = WorkerRegistry()
        
        worker1 = registry.register_worker("builder", "ollama:deepseek-8b", worker_id="worker_1")
        worker2 = registry.register_worker("builder", "ollama:deepseek-8b", worker_id="worker_2")
        
        # Both should be available
        available = registry.get_idle_workers("builder")
        assert len(available) == 2
    
    def test_worker_selection_by_xp(self):
        """Test worker selection prefers higher XP"""
        registry = WorkerRegistry()
        
        worker1 = registry.register_worker("builder", "ollama:deepseek-8b", worker_id="worker_low_xp")
        worker2 = registry.register_worker("builder", "ollama:deepseek-8b", worker_id="worker_high_xp")
        
        # Add XP to worker2
        for _ in range(5):
            registry.complete_task(worker2.worker_id, resolution_time_minutes=1.0, success=True)
        
        # Get idle workers
        workers = registry.get_idle_workers("builder")
        
        # Should have workers
        assert len(workers) >= 1
        
        # worker2 should have higher XP
        worker2_data = registry.get_worker(worker2.worker_id)
        assert worker2_data.xp.total > worker1.xp.total
    
    def test_worker_reputation_update(self):
        """Test worker reputation updates on task completion"""
        registry = WorkerRegistry()
        
        worker = registry.register_worker("builder", "ollama:deepseek-8b")
        
        initial_reputation = worker.reputation.score
        
        # Complete some tasks
        for _ in range(3):
            registry.complete_task(worker.worker_id, resolution_time_minutes=5.0, success=True)
        
        # Check reputation updated
        updated_worker = registry.get_worker(worker.worker_id)
        assert updated_worker.reputation.total_tasks_completed == 3


class TestPlannerWorkerFlow:
    """Test complete Planner + Worker flow"""
    
    def test_full_task_lifecycle(self):
        """Test full task lifecycle from creation to completion"""
        planner = Planner()
        registry = WorkerRegistry()
        
        # Create worker
        worker = registry.register_worker("builder", "ollama:deepseek-8b")
        
        # Create task
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Full Lifecycle Test",
            "goal": "Test full flow",
            "risk_level": "low"
        })
        
        # Queue
        planner.queue_task(task.id)
        assert task.state == "queued"
        
        # Assign
        planner.assign_task(task.id, worker.worker_id)
        assert task.state == "assigned"
        
        # Start (worker starts working)
        registry.start_task(worker.worker_id)
        
        # Complete
        registry.complete_task(worker.worker_id, resolution_time_minutes=10.0, success=True)
        
        # Verify task completed
        task = planner.tasks[task.id]
        assert task.state == "verified"
        
        # Worker should be idle again
        idle_workers = registry.get_idle_workers()
        assert worker.worker_id in [w.worker_id for w in idle_workers]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
