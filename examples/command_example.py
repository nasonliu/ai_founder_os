"""
Example: Command Interface Usage

Demonstrates how to use the natural language command interface.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from planner.planner import create_planner, Project
from planner.commands import create_command_interface


def main():
    # Setup
    planner = create_planner({"max_concurrency": 3, "retry_limit": 3})
    
    # Add a project
    project = Project(
        id="proj_demo",
        name="Demo Project",
        one_sentence_goal="Test commands"
    )
    planner.projects[project.id] = project
    
    # Create command interface
    cmd = create_command_interface(planner)
    
    # Test commands
    commands = [
        "help",
        "create task Write documentation",
        "status",
        "create project New Project",
    ]
    
    print("=== Command Interface Demo ===\n")
    
    for cmd_str in commands:
        print(f"> {cmd_str}")
        result = cmd.execute(cmd_str)
        print(f"  Success: {result.success}")
        print(f"  Message: {result.message}")
        if result.data:
            import json
            print(f"  Data: {json.dumps(result.data, indent=2)}")
        print()


if __name__ == "__main__":
    main()
