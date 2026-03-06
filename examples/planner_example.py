"""
Example: Basic Planner Usage

Demonstrates how to create tasks and manage the planner.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from planner.planner import create_planner, Project, TaskState


def main():
    # Create planner with config
    config = {
        "max_concurrency": 3,
        "retry_limit": 3,
        "slowdown_threshold": 5
    }
    planner = create_planner(config)
    
    # Create a project
    project = Project(
        id="proj_demo",
        name="Demo Project",
        one_sentence_goal="Build an AI agent"
    )
    planner.projects[project.id] = project
    print(f"Created project: {project.name}")
    
    # Create tasks
    tasks_data = [
        {
            "id": "task_001",
            "project_id": project.id,
            "title": "Research AI frameworks",
            "goal": "Find best AI agent frameworks",
            "risk_level": "low"
        },
        {
            "id": "task_002",
            "project_id": project.id,
            "title": "Implement agent",
            "goal": "Build the AI agent",
            "risk_level": "medium"
        },
        {
            "id": "task_003",
            "project_id": project.id,
            "title": "Write tests",
            "goal": "Test the agent",
            "risk_level": "low"
        }
    ]
    
    planner.load_tasks(tasks_data)
    print(f"Created {len(tasks_data)} tasks")
    
    # Show all tasks
    print("\nAll tasks:")
    for task_id, task in planner.tasks.items():
        print(f"  - {task.title} ({task.state})")
    
    # Queue and get next task
    planner.queue_task("task_001")
    next_task = planner.get_next_task()
    print(f"\nNext task: {next_task.title if next_task else 'None'}")
    
    # Get status summary
    status = planner.get_status_summary()
    print(f"\nStatus: {status}")
    
    # Complete a task
    planner.complete_task("task_001", success=True)
    print("\nCompleted task_001")
    
    # Show final status
    print("\nFinal tasks:")
    for task_id, task in planner.tasks.items():
        print(f"  - {task.title} ({task.state})")


if __name__ == "__main__":
    main()
