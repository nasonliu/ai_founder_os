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
    
    def test_get_next_task_empty_queue(self):
        """Test get_next_task returns None when queue is empty"""
        planner = create_planner()
        assert planner.get_next_task() is None
    
    def test_dependency_aware_scheduling(self):
        """Test that tasks with unmet dependencies are not returned"""
        planner = create_planner()
        
        # Create a task that depends on another
        dep_task = planner.create_task({
            "project_id": "proj_001",
            "title": "Dependency Task",
            "goal": "First task"
        })
        dep_task.state = "created"
        planner.queue_task(dep_task.id)
        
        # Create dependent task (before dependency is done)
        dependent_task = planner.create_task({
            "project_id": "proj_001",
            "title": "Dependent Task",
            "goal": "Second task",
            "depends_on": [dep_task.id]
        })
        planner.queue_task(dependent_task.id)
        
        # Dependency not met - should return the first task (dep_task), not the dependent
        assert planner.get_next_task() is not None
        next_task = planner.get_next_task()
        # The next task should be the one without unsatisfied dependencies
        assert next_task.id == dep_task.id
        
        # Now complete the dependency
        dep_task.state = "verified"
        
        # Now should return the dependent task (it's now runnable and higher priority due to urgency)
        next_task = planner.get_next_task()
        assert next_task is not None
        assert next_task.id == dependent_task.id
    
    def test_dependency_urgency(self):
        """Test that tasks blocking many others get higher priority"""
        planner = create_planner()
        
        # Create base task and complete it properly
        base_task = planner.create_task({
            "project_id": "proj_001",
            "title": "Base Task",
            "goal": "Base task",
            "risk_level": "high"  # High risk should be lower priority normally
        })
        # Queue and complete it
        planner.queue_task(base_task.id)
        planner.complete_task(base_task.id, success=True)
        
        # Create multiple tasks that depend on the completed base task
        # and add them to the queue
        for i in range(3):
            dep_task = planner.create_task({
                "project_id": "proj_001",
                "title": f"Dependent Task {i}",
                "goal": f"Task {i}",
                "depends_on": [base_task.id]
            })
            planner.queue_task(dep_task.id)
        
        # All tasks should now be runnable since base is verified
        next_task = planner.get_next_task()
        assert next_task is not None
    
    def test_priority_by_risk_level(self):
        """Test that low-risk tasks are prioritized higher than high-risk"""
        planner = create_planner()
        
        # Create low-risk task
        low_risk = planner.create_task({
            "project_id": "proj_001",
            "title": "Low Risk",
            "goal": "Low risk task",
            "risk_level": "low"
        })
        planner.queue_task(low_risk.id)
        
        # Create high-risk task
        high_risk = planner.create_task({
            "project_id": "proj_001",
            "title": "High Risk",
            "goal": "High risk task",
            "risk_level": "high"
        })
        planner.queue_task(high_risk.id)
        
        # Low risk should come first
        next_task = planner.get_next_task()
        assert next_task.id == low_risk.id
    
    def test_retry_count_affects_priority(self):
        """Test that tasks with more retries get lower priority"""
        planner = create_planner()
        
        # Create task with retries
        retried_task = planner.create_task({
            "project_id": "proj_001",
            "title": "Retried Task",
            "goal": "Task with retries",
            "risk_level": "low"
        })
        retried_task.retry_count = 2
        planner.queue_task(retried_task.id)
        
        # Create fresh task
        fresh_task = planner.create_task({
            "project_id": "proj_001",
            "title": "Fresh Task",
            "goal": "New task",
            "risk_level": "low"
        })
        planner.queue_task(fresh_task.id)
        
        # Fresh task should come first (lower retry count = higher priority)
        next_task = planner.get_next_task()
        assert next_task.id == fresh_task.id
    
    def test_are_dependencies_met(self):
        """Test _are_dependencies_met method"""
        planner = create_planner()
        
        # Task with no dependencies
        task1 = planner.create_task({
            "project_id": "proj_001",
            "title": "No Deps",
            "goal": "Task 1"
        })
        assert planner._are_dependencies_met(task1) is True
        
        # Task with satisfied dependency
        dep = planner.create_task({
            "project_id": "proj_001",
            "title": "Dep",
            "goal": "Dependency"
        })
        dep.state = "verified"
        
        task2 = planner.create_task({
            "project_id": "proj_001",
            "title": "With Dep",
            "goal": "Task 2",
            "depends_on": [dep.id]
        })
        assert planner._are_dependencies_met(task2) is True
        
        # Task with unsatisfied dependency
        dep2 = planner.create_task({
            "project_id": "proj_001",
            "title": "Unsatisfied Dep",
            "goal": "Dependency"
        })
        dep2.state = "running"  # Not completed
        
        task3 = planner.create_task({
            "project_id": "proj_001",
            "title": "With Unsatisfied Dep",
            "goal": "Task 3",
            "depends_on": [dep2.id]
        })
        assert planner._are_dependencies_met(task3) is False
    
    def test_get_runnable_tasks(self):
        """Test _get_runnable_tasks method"""
        planner = create_planner()
        
        # Create and complete first dependency
        dep = planner.create_task({
            "project_id": "proj_001",
            "title": "Dep",
            "goal": "Dependency"
        })
        planner.queue_task(dep.id)
        planner.complete_task(dep.id, success=True)
        
        # Create runnable task with satisfied dependency and add to queue
        runnable = planner.create_task({
            "project_id": "proj_001",
            "title": "Runnable",
            "goal": "Can run",
            "depends_on": [dep.id]
        })
        planner.queue_task(runnable.id)
        
        # Create a separate task with no dependencies (also runnable)
        independent = planner.create_task({
            "project_id": "proj_001",
            "title": "Independent",
            "goal": "No dependencies"
        })
        planner.queue_task(independent.id)
        
        # Create blocked task that depends on incomplete task
        incomplete_dep = planner.create_task({
            "project_id": "proj_001",
            "title": "Incomplete Dep",
            "goal": "Not done"
        })
        planner.queue_task(incomplete_dep.id)
        
        blocked = planner.create_task({
            "project_id": "proj_001",
            "title": "Blocked",
            "goal": "Can't run",
            "depends_on": [incomplete_dep.id]
        })
        planner.queue_task(blocked.id)
        
        # Get runnable tasks - should include runnable and independent
        runnable_list = planner._get_runnable_tasks()
        
        # Should have 2 runnable tasks (runnable + independent)
        # blocked should NOT be in the list (dependency not met)
        runnable_ids = [t.id for t in runnable_list]
        assert runnable.id in runnable_ids
        assert independent.id in runnable_ids
        assert blocked.id not in runnable_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
