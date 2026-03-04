"""
Unit tests for Planner module
"""

import pytest
import json
from src.planner.planner import (
    Planner, Task, Project, TaskState, TaskRiskLevel, WorkerType,
    create_planner
)


class TestTask:
    """Test Task model"""
    
    def test_task_creation(self):
        """Test creating a task"""
        task = Task(
            id="task_001",
            project_id="proj_001",
            title="Test Task",
            goal="Test goal"
        )
        assert task.id == "task_001"
        assert task.state == "created"
        assert task.retry_count == 0
    
    def test_task_state_transition(self):
        """Test valid state transitions"""
        task = Task(
            id="task_001",
            project_id="proj_001",
            title="Test",
            goal="Test"
        )
        
        # created -> queued
        assert task.transition_to(TaskState.QUEUED)
        assert task.state == "queued"
        
        # queued -> assigned
        assert task.transition_to(TaskState.ASSIGNED)
        assert task.state == "assigned"
        
    def test_invalid_state_transition(self):
        """Test invalid state transition"""
        task = Task(
            id="task_001",
            project_id="proj_001",
            title="Test",
            goal="Test"
        )
        
        # Can't go directly from created to verified
        assert not task.transition_to(TaskState.VERIFIED)
    
    def test_can_retry(self):
        """Test retry logic"""
        task = Task(
            id="task_001",
            project_id="proj_001",
            title="Test",
            goal="Test"
        )
        
        # Initially in created state - can't retry
        assert not task.can_retry(max_retries=3)
        
        # After failure - can retry
        task.state = "failed"
        assert task.can_retry(max_retries=3)
        
        # After too many retries - can't retry
        task.retry_count = 3
        assert not task.can_retry(max_retries=3)


class TestProject:
    """Test Project model"""
    
    def test_project_creation(self):
        """Test creating a project"""
        project = Project(
            id="proj_001",
            name="Test Project",
            one_sentence_goal="A test project"
        )
        assert project.id == "proj_001"
        assert project.status == "active"
        assert project.operating_mode == "normal"


class TestPlanner:
    """Test Planner"""
    
    def test_planner_creation(self):
        """Test creating a planner"""
        planner = create_planner({"max_concurrency": 3})
        assert planner.max_concurrency == 3
        assert planner.retry_limit == 3
    
    def test_create_task(self):
        """Test creating a task via planner"""
        planner = create_planner()
        
        task_data = {
            "project_id": "proj_001",
            "title": "Test Task",
            "goal": "Test goal",
            "risk_level": "low"
        }
        
        task = planner.create_task(task_data)
        assert task.id.startswith("task_")
        assert task.id in planner.tasks
    
    def test_queue_task(self):
        """Test queueing a task"""
        planner = create_planner()
        
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test",
            "goal": "Test"
        })
        
        assert planner.queue_task(task.id)
        assert task.id in planner.task_queue
        assert task.state == "queued"
    
    def test_assign_task(self):
        """Test assigning a task"""
        planner = create_planner()
        
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test",
            "goal": "Test"
        })
        planner.queue_task(task.id)
        
        assert planner.assign_task(task.id, "worker_001")
        assert task.assigned_to["worker_id"] == "worker_001"
        assert task.state == "assigned"
    
    def test_complete_task(self):
        """Test completing a task"""
        planner = create_planner()
        
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test",
            "goal": "Test"
        })
        
        # Set task to running state first
        task.state = "running"
        
        # Success
        assert planner.complete_task(task.id, success=True)
        assert task.state == "verified"
        
    def test_complete_task_failure(self):
        """Test task failure handling"""
        planner = create_planner()
        
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test",
            "goal": "Test"
        })
        
        # Set to running first
        task.state = "running"
        
        # Failure
        assert planner.complete_task(task.id, success=False)
        assert task.state == "failed"
        assert task.retry_count == 1
    
    def test_slowdown_trigger(self):
        """Test auto slowdown on repeated failures"""
        planner = create_planner({"max_concurrency": 3, "retry_limit": 2})
        original_concurrency = planner.max_concurrency
        
        # Create and fail task multiple times
        for i in range(3):
            task = planner.create_task({
                "project_id": "proj_001",
                "title": f"Test {i}",
                "goal": "Test"
            })
            # Set to running state
            task.state = "running"
            planner.complete_task(task.id, success=False)
        
        assert planner.slowdown_triggered
        assert planner.max_concurrency < original_concurrency
    
    def test_get_status_summary(self):
        """Test status summary"""
        planner = create_planner()
        
        # Add some tasks
        for i in range(3):
            task = planner.create_task({
                "project_id": "proj_001",
                "title": f"Task {i}",
                "goal": "Test"
            })
            planner.queue_task(task.id)
        
        status = planner.get_status_summary()
        assert status["total_tasks"] == 3
        assert status["queue_length"] == 3
    
    def test_get_blockers(self):
        """Test getting blockers"""
        planner = create_planner()
        
        # Create blocked task
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Blocked Task",
            "goal": "Test"
        })
        task.state = "blocked"
        
        blockers = planner.get_blockers()
        assert len(blockers) == 1
        assert blockers[0]["task_id"] == task.id
    
    def test_export_import_state(self):
        """Test state persistence"""
        planner = create_planner()
        
        # Create task
        task = planner.create_task({
            "project_id": "proj_001",
            "title": "Test",
            "goal": "Test"
        })
        
        # Export
        state = planner.export_state()
        assert "tasks" in state
        assert len(state["tasks"]) == 1
        
        # Create new planner and import
        new_planner = create_planner()
        new_planner.import_state(state)
        
        assert len(new_planner.tasks) == 1
        assert "task_" in list(new_planner.tasks.keys())[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
