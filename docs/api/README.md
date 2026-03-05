# API Documentation

## Core Modules

### Planner

```python
from src.planner.planner import Planner, Task, Project

# Create planner
planner = Planner({"max_concurrency": 3})

# Create project
project = Project(
    id="proj_001",
    name="My Project",
    one_sentence_goal="Build something amazing"
)
planner.projects[project.id] = project

# Create task
task = planner.create_task({
    "project_id": "proj_001",
    "title": "Implement Feature",
    "goal": "Build the feature",
    "risk_level": "medium"
})

# Queue and assign
planner.queue_task(task.id)
planner.assign_task(task.id, "worker_001")

# Complete task
planner.complete_task(task.id, success=True)
```

### Worker Registry

```python
from src.workers.registry import WorkerRegistry, create_worker

# Create registry
registry = WorkerRegistry()

# Create and register worker
worker = create_worker("builder", "my_worker")
registry.register_worker(worker)

# Update XP
registry.update_worker_xp(worker.worker_id, success=True)

# Get best worker
best = registry.get_best_worker("builder")
```

### Policy Engine

```python
from src.policy.engine import PolicyEngine

# Create engine
engine = PolicyEngine()

# Check task execution
result = engine.check_task_execution(task_data, worker_data)
if result.allowed:
    # Execute task
    pass
```

### Connection Manager

```python
from src.connections.manager import ConnectionManager

# Create manager
manager = ConnectionManager()

# Add connection
manager.add_connection({
    "provider": "openai",
    "name": "work",
    "api_key": "sk-..."
})

# Get capability token
token = manager.issue_token(
    worker_id="worker_001",
    permissions=["llm.call"]
)
```

### Experience Ledger

```python
from src.experience.ledger import ExperienceLedger

# Create ledger
ledger = ExperienceLedger()

# Add experience
ledger.add_experience(
    problem="Module import error",
    solution="Install missing dependency",
    tags=["python", "import"]
)

# Search
results = ledger.search_by_tags(["python"])
```

### Human Gate

```python
from src.policy.human_gate import HumanGate

# Create gate
gate = HumanGate()

# Create review card
card = gate.create_review_card(
    card_type=ReviewCardType.SKILL_INSTALL,
    context=context,
    risk_level="high"
)

# Approve
gate.approve_card(card.id, approver="human")
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific module
pytest tests/test_planner.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```
