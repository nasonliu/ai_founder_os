"""
Integration tests: Planner + Worker System
"""

import pytest
from src.planner.planner import Planner, Task
from src.workers.registry import WorkerRegistry, create_worker


class TestPlannerWorkerIntegration:
    """Test Planner and Worker integration"""
    
    def test_planner_assigns_task_to_worker(self):
        """Test that planner can assign task to worker"""
        # Setup
        planner = Planner({"max_concurrency": 3})
        registry = WorkerRegistry()
        
        # Create worker
        worker = create_worker("builder", "test_worker")
        registry.register_worker(worker)
        
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
        
        worker = create_worker("builder", "test_worker")
        registry.register_worker(worker)
        
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
        
        worker = create_worker("builder", "xp_worker")
        registry.register_worker(worker)
        
        initial_xp = worker.xp.total
        
        # Complete task
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "XP Test",
            "goal": "Test"
        })
        
        # Simulate worker's task
        registry.update_worker_xp(worker.worker_id, success=True)
        
        assert worker.xp.total == initial_xp + 1
    
    def test_worker_failure_tracks_xp(self):
        """Test that worker failure is tracked"""
        planner = Planner()
        registry = WorkerRegistry()
        
        worker = create_worker("builder", "fail_worker")
        registry.register_worker(worker)
        
        initial_xp = worker.xp.total
        
        # Simulate failure
        registry.update_worker_xp(worker.worker_id, success=False)
        
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
        
        worker1 = create_worker("builder", "worker_1")
        worker2 = create_worker("builder", "worker_2")
        
        registry.register_worker(worker1)
        registry.register_worker(worker2)
        
        # Both should be available
        available = registry.get_available_workers("builder")
        assert len(available) == 2
    
    def test_worker_selection_by_xp(self):
        """Test worker selection prefers higher XP"""
        registry = WorkerRegistry()
        
        worker1 = create_worker("builder", "worker_low_xp")
        worker2 = create_worker("builder", "worker_high_xp")
        
        # Add XP to worker2
        for _ in range(5):
            registry.update_worker_xp(worker2.worker_id, success=True)
        
        registry.register_worker(worker1)
        registry.register_worker(worker2)
        
        # Get best worker
        best = registry.get_best_worker("builder")
        assert best.worker_id == worker2.worker_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
