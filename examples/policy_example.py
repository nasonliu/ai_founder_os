"""
Example: Policy Engine Usage

Demonstrates how to use the policy engine for task validation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from policy.engine import PolicyEngine


def main():
    # Create policy engine
    engine = PolicyEngine()
    print("Created Policy Engine")
    
    # Define a low-risk task
    low_risk_task = {
        "id": "task_001",
        "title": "Simple computation",
        "goal": "Run a simple computation",
        "risk_level": "low",
        "inputs": {"code": "print('hello')"},
        "expected_artifact": {"type": "file", "path_hint": "output.txt"},
        "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}]
    }
    
    project_data = {
        "id": "proj_001",
        "name": "Demo Project",
        "operating_mode": "normal"
    }
    
    # Check low risk task
    print("\n--- Low Risk Task ---")
    result = engine.check_task_execution(low_risk_task, project_data)
    print(f"Passed: {result.passed}")
    print(f"Blocked: {result.blocked}")
    
    # Define high risk task
    high_risk_task = {
        "id": "task_002",
        "title": "Delete production database",
        "goal": "Delete the database",
        "risk_level": "high",
        "inputs": {"action": "delete", "target": "production_db"},
        "expected_artifact": {},
        "validators": [{"id": "val_002", "type": "manual_review", "blocking": True}]
    }
    
    # Check high risk task
    print("\n--- High Risk Task ---")
    result = engine.check_task_execution(high_risk_task, project_data)
    print(f"Passed: {result.passed}")
    print(f"Blocked: {result.blocked}")
    print(f"Violations: {len(result.violations)}")
    
    # Show violations
    for v in result.violations:
        print(f"  - {v.rule}: {v.message}")


if __name__ == "__main__":
    main()
