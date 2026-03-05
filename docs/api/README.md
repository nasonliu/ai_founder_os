# AI Founder OS - API Documentation

This document provides comprehensive API documentation for all core modules in AI Founder OS.

## Table of Contents

- [Planner Module](#planner-module)
- [Workers Module](#workers-module)
- [Policy Engine](#policy-engine)
- [Connections Manager](#connections-manager)
- [Experience Ledger](#experience-ledger)
- [Dashboard API](#dashboard-api)

---

## Planner Module

The Planner is the orchestration core that manages task generation, worker scheduling, and execution flow.

### Installation & Setup

```python
from src.planner.planner import Planner, Task, Project, create_planner
```

### Core Classes

#### TaskState Enum
Represents the lifecycle states of a task.

```python
from src.planner.planner import TaskState

states = [
    TaskState.IDLE,
    TaskState.CREATED,
    TaskState.QUEUED,
    TaskState.ASSIGNED,
    TaskState.RUNNING,
    TaskState.NEEDS_REVIEW,
    TaskState.VERIFYING,
    TaskState.VERIFIED,
    TaskState.FAILED,
    TaskState.CANCELED,
    TaskState.BLOCKED,
]
```

#### Task Class
The main task data model.

```python
from src.planner.planner import Task

# Create a task
task = Task(
    id="task_001",
    project_id="proj_001",
    title="Implement Feature",
    goal="Build the core feature implementation",
    inputs={"files": ["feature.py"]},
    expected_artifact={"type": "code", "path_hint": "src/feature.py"},
    validators=[{"id": "val_001", "type": "unit_test", "command": "pytest", "blocking": True}],
    risk_level="medium",
    required_capabilities=["cap_code", "cap_test"],
    routing_hints={"worker_type": "builder"}
)

# Convert to dictionary
task_dict = task.to_dict()

# Create from dictionary
task = Task.from_dict(task_dict)
```

#### Project Class
Represents a project that contains tasks.

```python
from src.planner.planner import Project

project = Project(
    id="proj_001",
    name="AI Founder OS",
    one_sentence_goal="Build an AI-native operating system",
    kpis=[{"name": "test_coverage", "target": ">=80%"}],
    definition_of_done=["Tests pass", "Code reviewed", "Documentation updated"],
    constraints={"risk": ["no_production_db"]},
    operating_mode="normal",
    execution_limits={"max_concurrency": 3, "retry_limit": 3}
)
```

### Planner API

```python
from src.planner.planner import Planner, create_planner

# Create planner with configuration
planner = create_planner({
    "max_concurrency": 3,
    "retry_limit": 3
})

# Create a task
task = planner.create_task({
    "project_id": "proj_001",
    "title": "Implement API",
    "goal": "Build REST API endpoints",
    "risk_level": "medium",
    "validators": [
        {"id": "val_001", "type": "unit_test", "command": "pytest", "blocking": True}
    ]
})

# Queue task for execution
planner.queue_task(task.id)

# Get next task from queue
next_task = planner.get_next_task()

# Assign task to worker
planner.assign_task(task.id, "worker_builder_01")

# Mark task as completed
planner.complete_task(task.id, success=True)

# Get task status
status = planner.get_task_status(task.id)

# Get project status
project_status = planner.get_project_status("proj_001")

# Get blockers
blockers = planner.get_blockers()

# Get overall status
status_summary = planner.get_status_summary()

# Export/Import state for persistence
state = planner.export_state()
planner.import_state(state)
```

### State Transitions

Valid task state transitions:
- `CREATED` → `QUEUED`
- `QUEUED` → `ASSIGNED`, `CANCELED`
- `ASSIGNED` → `RUNNING`, `IDLE`
- `RUNNING` → `VERIFYING`, `NEEDS_REVIEW`, `FAILED`, `BLOCKED`
- `VERIFYING` → `VERIFIED`, `FAILED`, `NEEDS_REVIEW`
- `NEEDS_REVIEW` → `QUEUED`, `CANCELED`, `BLOCKED`
- `FAILED` → `QUEUED`, `BLOCKED`
- `VERIFIED` → `ASSIGNED`
- `BLOCKED` → `RUNNING`

---

## Workers Module

Manages the AI Worker pool with XP tracking, reputation, and scheduling.

### Installation & Setup

```python
from src.workers.registry import (
    WorkerRegistry, Worker, WorkerType, WorkerStatus,
    XPStats, Reputation, get_registry, create_default_workers
)
```

### Core Classes

#### WorkerType Enum
```python
from src.workers.registry import WorkerType

types = [
    WorkerType.BUILDER,      # Code implementation
    WorkerType.RESEARCHER,   # Research and analysis
    WorkerType.DOCUMENTER,    # Documentation writing
    WorkerType.VERIFIER,     # Testing and verification
    WorkerType.EVALUATOR,    # Performance evaluation
]
```

#### Worker Class
```python
worker = Worker(
    worker_id="worker_builder_01",
    worker_type="builder",
    model_source="local_ollama:deepseek-8b",
    fallback_model="cloud_openai:gpt-4",
    capabilities=["cap_code", "cap_test"]
)
```

### WorkerRegistry API

```python
from src.workers.registry import WorkerRegistry, get_registry

# Create registry
registry = WorkerRegistry(storage_path="workers.json")

# Register a new worker
worker = registry.register_worker(
    worker_type="builder",
    model_source="local_ollama:deepseek-8b",
    fallback_model="cloud_openai:gpt-4",
    worker_id="worker_builder_01"
)

# Get worker by ID
worker = registry.get_worker("worker_builder_01")

# List workers with filters
all_workers = registry.list_workers()
builders = registry.list_workers(worker_type="builder")
idle = registry.list_workers(status="idle")

# Get idle workers
idle_workers = registry.get_idle_workers(worker_type="builder")

# Update worker status
registry.update_worker_status("worker_builder_01", "running")
registry.assign_task("worker_builder_01", "task_001")
registry.start_task("worker_builder_01")

# Complete task and update XP
registry.complete_task(
    "worker_builder_01",
    resolution_time_minutes=15.5,
    success=True
)

# Record experience reuse
registry.record_experience_reuse("worker_builder_01")

# Select best worker for a task
best_worker = registry.select_best_worker(
    task_type_hint="builder",
    required_capabilities=["cap_code"]
)

# Get worker statistics
stats = registry.get_worker_stats()

# Worker management
registry.pause_worker("worker_builder_01")
registry.resume_worker("worker_builder_01")
registry.remove_worker("worker_builder_01")
```

### XP and Reputation System

```python
from src.workers.registry import XPStats, Reputation

# XP calculation: success * 1 + reused * 2 - failure * 1
xp = XPStats()
xp.add_success()      # +1 XP
xp.add_reuse()       # +2 XP  
xp.add_failure()     # -1 XP
print(xp.calculate_total())

# Reputation updates based on task completion
rep = Reputation()
rep.update_from_completion(resolution_time_minutes=30.0, success=True)
print(rep.to_dict())
```

---

## Policy Engine

Three-layer policy system for Execution, Safety, and Quality governance.

### Installation & Setup

```python
from src.policy.engine import (
    PolicyEngine, ExecutionPolicy, SafetyPolicy, QualityPolicy,
    PolicyType, ValidationResult, create_policy_engine
)
```

### Core Classes

#### ValidationResult Enum
```python
from src.policy.engine import ValidationResult

results = [
    ValidationResult.PASS,   # All checks passed
    ValidationResult.WARN,   # Warnings but no violations
    ValidationResult.FAIL,   # Non-blocking violations
    ValidationResult.BLOCK,  # Blocking violations
]
```

### Policy Engine API

```python
from src.policy.engine import PolicyEngine, create_policy_engine

# Create policy engine
engine = create_policy_engine()

# Define task and project
task = {
    "id": "task_001",
    "project_id": "proj_001",
    "goal": "Implement feature",
    "inputs": {"files": ["feature.py"]},
    "expected_artifact": {"type": "code"},
    "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}],
    "risk_level": "medium"
}

project = {
    "id": "proj_001",
    "name": "AI Founder OS",
    "operating_mode": "normal",
    "execution_limits": {"max_concurrency": 3, "retry_limit": 3},
    "kpis": []
}

# Check task execution
result = engine.check_task_execution(task, project, current_concurrency=1)
print(f"Result: {result.result.value}")
print(f"Passed: {result.passed}")
print(f"Blocked: {result.blocked}")
print(f"Violations: {result.violations}")
print(f"Warnings: {result.warnings}")

# Check worker assignment
result = engine.check_worker_assignment(task, worker, project)

# Check evidence pack quality
result = engine.check_evidence_pack(evidence, task, builder_id, verifier_id)

# Check KPI gate
result = engine.check_kpi_gate(project, kpi_results)

# Check for secret leakage
result = engine.check_secret_leakage(
    content="My API key is sk-1234567890",
    context_type="log"
)

# Trigger auto-slowdown
slowdown = engine.trigger_slowdown()
print(slowdown)

# Activate kill switch
kill_switch = engine.activate_kill_switch("Critical security issue")

# Get status
status = engine.get_status()
```

### Policy Rules Summary

#### Execution Policy
- Task must have: goal, inputs, expected_artifact, validators, risk_level
- Must have at least one blocking validator
- Retry limit based on project configuration
- Concurrency limits based on operating mode

#### Safety Policy
- Detects API keys, tokens, secrets using regex patterns
- Prevents secrets in git, logs, prompts
- Validates worker capability tokens
- Controls network access via whitelist

#### Quality Policy
- Requires blocking validator
- Evidence Pack must be complete
- Verifier must be independent from Builder
- KPI Gate: Project KPIs must be met

---

## Connections Manager

Manages external service connections with credential management, capability tokens, and budget control.

### Installation & Setup

```python
from src.connections.manager import (
    ConnectionManager, Connection, CapabilityToken,
    ProviderType, ConnectionStatus, create_connection_manager
)
```

### Core Classes

#### ProviderType Enum
```python
from src.connections.manager import ProviderType

# LLM Providers
ProviderType.OPENAI, ProviderType.ANTHROPIC, ProviderType.DEEPSEEK
ProviderType.OLLAMA, ProviderType.VLLM

# Search Providers  
ProviderType.BRAVE_SEARCH, ProviderType.SERPAPI, ProviderType.TAVILY

# Repository Providers
ProviderType.GITHUB, ProviderType.GITLAB

# OAuth Services
ProviderType.GOOGLE, ProviderType.NOTION, ProviderType.SLACK
```

### ConnectionManager API

```python
from src.connections.manager import ConnectionManager, create_connection_manager

# Create connection manager
cm = create_connection_manager()

# Add a connection
conn = cm.add_connection({
    "connection_id": "conn_openai_001",
    "provider": "openai",
    "name": "Work OpenAI",
    "auth_type": "api_key",
    "scopes": ["chat_completions", "embeddings"],
    "quota": {"quota_type": "monthly", "limit": "100", "current": "25"},
    "allowed_workers": ["worker_builder_01"]
})

# Add local Ollama connection
ollama = cm.add_connection({
    "connection_id": "conn_ollama_001",
    "provider": "ollama",
    "name": "Local DeepSeek",
    "auth_type": "local",
    "local_config": {
        "endpoint": "http://localhost:11434",
        "models": [
            {"name": "deepseek-r1:8b", "context_limit": 32768}
        ],
        "concurrency_limit": 2
    }
})

# Get connection
conn = cm.get_connection("conn_openai_001")

# List connections
all_conns = cm.list_connections()
active_conns = cm.list_connections(status="active")

# Generate capability token for worker
token = cm.generate_token(
    connection_id="conn_ollama_001",
    worker_id="worker_builder_01",
    task_id="task_001",
    permissions=["llm.call"],
    restrictions={"max_rpm": 30},
    ttl_minutes=15
)

# Validate token
is_valid = cm.validate_token(token.token_id)

# Revoke token
cm.revoke_token(token.token_id)

# Get worker tokens
worker_tokens = cm.get_worker_tokens("worker_builder_01")

# Cleanup expired tokens
cm.cleanup_expired_tokens()

# Get connection for worker type
builder_conn = cm.get_connection_for_worker("builder")

# Check budget
budget = cm.check_budget("proj_001", estimated_cost=2.0)
if budget["allowed"]:
    # Proceed with task
    
# Record spend
cm.record_spend("proj_001", 2.0)

# Get budget status
budget_status = cm.get_budget_status()

# Perform health check
health = cm.perform_health_check("conn_ollama_001")

# Get status summary
status = cm.get_status_summary()
```

---

## Experience Ledger

System knowledge base for storing and retrieving learned solutions.

### Installation & Setup

```python
from src.experience.ledger import (
    ExperienceLedger, Experience, HelpRequest,
    Problem, Solution, Context, get_ledger
)
```

### Core Classes

#### ExperienceCategory Enum
```python
from src.experience.ledger import ExperienceCategory

categories = [
    ExperienceCategory.BUILD,
    ExperienceCategory.DEPENDENCY,
    ExperienceCategory.RUNTIME,
    ExperienceCategory.LOGIC,
    ExperienceCategory.TEST,
    ExperienceCategory.ENV,
    ExperienceCategory.NETWORK,
    ExperienceCategory.SECURITY,
]
```

### ExperienceLedger API

```python
from src.experience.ledger import (
    ExperienceLedger, Problem, Solution, Context,
    ReusablePattern, get_ledger
)

# Create ledger
ledger = ExperienceLedger(storage_path="experience.jsonl")

# Add an experience
experience = ledger.add_experience(
    project_id="proj_001",
    problem=Problem(
        title="ModuleNotFoundError when importing package",
        symptoms=["ModuleNotFoundError: No module named 'requests'"]
    ),
    solution=Solution(
        steps=["pip install requests", "Add to requirements.txt"],
        validation=["Import requests succeeds"]
    ),
    contributor_id="worker_builder_01",
    tags=["python", "import", "dependency"],
    error_signatures=["ModuleNotFoundError"]
)

# Get experience by ID
exp = ledger.get_experience("exp_abc123")

# Search by tags
results = ledger.search_by_tags(["python", "import"], limit=5)

# Search by error message
results = ledger.search_by_error("ModuleNotFoundError: No module named", limit=5)

# Search by keywords
results = ledger.search_by_keywords(["import error", "module"], limit=5)

# Find solution (main entry point)
solution = ledger.find_solution(
    error_message="ImportError: cannot import",
    tags=["python"],
    keywords=["import", "module"]
)

if solution:
    print(f"Solution: {solution.solution.steps}")
    # Record reuse
    ledger.record_reuse(solution.id, "worker_builder_01")

# Create help request
help_request = ledger.create_help_request(
    requester_worker_id="worker_builder_01",
    task_id="task_001",
    error_summary="Cannot connect to database",
    project_id="proj_001",
    attempts=["Tried restarting", "Checked config"],
    constraints=["Must use existing DB"],
    desired_output=["Connection string format"],
    tags=["database", "connection"]
)

# List pending help requests
pending = ledger.list_pending_help_requests(worker_type="builder")

# Resolve help request
ledger.resolve_help_request(
    help_id=help_request.id,
    response="Use connection string: postgresql://user:pass@host:5432/db",
    responder_id="worker_verifier_01"
)

# Get experiences by worker
worker_exps = ledger.get_experiences_by_worker("worker_builder_01")

# Get experiences by project
project_exps = ledger.get_experiences_by_project("proj_001")

# Get statistics
stats = ledger.get_stats()

# Cleanup old experiences
removed = ledger.cleanup_old_experiences(days=90)
```

---

## Dashboard API

Backend API for dashboard UI with project paths, human gates, and observability.

### Installation & Setup

```python
from src.dashboard.api import (
    DashboardAPI, ReviewCard, ProjectPathNode,
    WorkerMetrics, SystemMetrics, create_dashboard
)
```

### Dashboard API

```python
from src.dashboard.api import DashboardAPI, create_dashboard

# Create dashboard
dashboard = create_dashboard()

# Create review card for human gate
card = dashboard.create_review_card(
    project_id="proj_001",
    gate_type="task_review",
    risk_level="high",
    summary="Review code changes for new feature",
    why_now="Feature is complete and needs review",
    affected_entities=["task_001"],
    change="Merge feature branch to main",
    options=[
        {"id": "opt1", "description": "Approve and merge"},
        {"id": "opt2", "description": "Request changes"}
    ],
    recommended_option="opt1"
)

# Get pending reviews
pending = dashboard.get_pending_reviews()
pending_for_project = dashboard.get_pending_reviews(project_id="proj_001")

# Approve/Reject/Modify review
dashboard.approve_review(card.id, notes="LGTM!")
dashboard.reject_review(card.id, notes="Needs changes")
dashboard.modify_review(card.id, notes="Approved with constraints", 
                       constraints_added=["max_file_size: 1MB"])

# Build project path graph
dashboard.build_project_path(
    project_id="proj_001",
    project_name="AI Founder OS",
    tasks=[
        {"id": "task_001", "title": "Setup", "state": "verified"},
        {"id": "task_002", "title": "Implement", "state": "running"}
    ]
)

# Get project path
path = dashboard.get_project_path("proj_001")

# Register workers
dashboard.register_worker("worker_builder_01", "builder", "ollama:deepseek")
dashboard.register_worker("worker_verifier_01", "verifier", "openai:gpt-4")

# Update worker status
dashboard.update_worker_status("worker_builder_01", "busy", "task_001")

# Record task completion
dashboard.record_worker_success("worker_builder_01", resolution_time_minutes=15.0)
dashboard.record_worker_failure("worker_builder_01")
dashboard.record_experience_reuse("worker_builder_01")

# Get worker metrics
metrics = dashboard.get_worker_metrics("worker_builder_01")
all_metrics = dashboard.get_all_workers()
stats = dashboard.get_worker_stats()

# Update system metrics
dashboard.update_system_metrics(
    total_tasks=100,
    completed_tasks=80,
    failed_tasks=5,
    queue_length=15,
    api_usage=5000
)

# Get observability metrics
observability = dashboard.get_observability_metrics()

# Cost metrics
dashboard.update_cost_metrics(daily=10.5, weekly=73.0, monthly=292.0)
costs = dashboard.get_cost_metrics()

# System status
status = dashboard.get_status()
dashboard.set_execution_mode("turbo")
dashboard.pause_system()
dashboard.resume_system()

# Get next gate requiring attention
next_gate = dashboard.get_next_gate()
```

---

## Quick Start Example

Here's a complete example using all modules together:

```python
from src.planner.planner import Planner, create_planner
from src.workers.registry import WorkerRegistry, create_default_workers
from src.policy.engine import PolicyEngine, create_policy_engine
from src.connections.manager import ConnectionManager, create_connection_manager
from src.experience.ledger import ExperienceLedger, get_ledger
from src.dashboard.api import DashboardAPI, create_dashboard

# Initialize all components
planner = create_planner({"max_concurrency": 3})
workers = WorkerRegistry()
policy = create_policy_engine()
connections = create_connection_manager()
ledger = get_ledger("experience.jsonl")
dashboard = create_dashboard()

# Create default workers
create_default_workers(workers)

# Create a project
from src.planner.planner import Project
project = Project(
    id="proj_001",
    name="Demo Project",
    one_sentence_goal="Build a demo"
)
planner.projects[project.id] = project

# Create a task
task = planner.create_task({
    "project_id": "proj_001",
    "title": "Implement Feature",
    "goal": "Build demo feature",
    "risk_level": "low",
    "validators": [{"id": "val_001", "type": "unit_test", "blocking": True}]
})

# Check policy before execution
result = policy.check_task_execution(task.to_dict(), project.to_dict())
if result.passed:
    planner.queue_task(task.id)
    
    # Assign to best worker
    worker = workers.select_best_worker(task_type_hint="builder")
    if worker:
        planner.assign_task(task.id, worker.worker_id)
        
print(f"Status: {planner.get_status_summary()}")
```

---

## Error Handling

All modules use Python exceptions. Common patterns:

```python
try:
    worker = registry.register_worker(
        worker_type="invalid_type",  # Will raise ValueError
        model_source="ollama:test"
    )
except ValueError as e:
    print(f"Invalid worker type: {e}")

# Check before operations
if task.can_retry(max_retries=3):
    # Retry logic
    pass

if connection.is_active() and not connection.is_expired():
    # Use connection
    pass
```

---

## Testing

Run tests with pytest:

```bash
# Run all tests
pytest tests/

# Run specific module tests
pytest tests/test_planner.py
pytest tests/test_workers.py
pytest tests/test_policy.py

# Run with coverage
pytest --cov=src tests/
```

---

## License

AI Founder OS - MIT License
