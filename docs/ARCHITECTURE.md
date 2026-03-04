# AI Founder OS - Architecture Specification

## 1. Architecture Overview

AI Founder OS 是一个多 agent orchestration 系统，核心思想是：

```
Planner + Worker Pool + Policy Engine = 可治理的 AI 执行系统
```

### 1.1 System Structure

```
Founder
   │
   ▼
Dashboard UI
   │
   ▼
Planner Engine
   │
   ├── Worker Pool
   │     ├─ Builder
   │     ├─ Researcher
   │     ├─ Documenter
   │     ├─ Verifier
   │     └─ Evaluator
   │
   ├── Skill Hub
   │
   ├── Experience Ledger
   │
   ├── Policy Engine
   │
   └── Connection Manager
```

### 1.2 Core Execution Loop

```
1. Read Project State
       ↓
2. Planner Generate Tasks
       ↓
3. Assign Worker
       ↓
4. Worker Execute
       ↓
5. Verification
       ↓
6. Update State
       ↓
7. Dashboard Update
       ↓
8. Repeat
```

---

## 2. Data Core Structures

### 2.1 Entity Relationship

```
Idea
  └─ Project
       └─ Task
            ├─ Subtask
            ├─ Artifact
            └─ EvidencePack
                  │
                  ├─ Validator
                  └─ ReviewCard (Human Gate)
```

### 2.2 Key Data Objects

| Object | Description |
|--------|-------------|
| Idea | 想法记录 |
| Project | 执行单元 |
| Task | 执行任务 |
| Artifact | 产物登记 |
| EvidencePack | 证据包 |
| Experience | 经验条目 |
| Skill | 技能模块 |
| Connection | 服务连接 |
| Worker | 执行节点 |

---

## 3. Planner Architecture

### 3.1 Planner Components

```
Planner
├── Task Generator
├── Task Scheduler
├── Worker Router
├── Human Gate Trigger
├── Policy Enforcer
└── State Manager
```

### 3.2 Task Generation Pipeline

```
Input: Project Card + Roadmap + Experience
        │
        ▼
Analyze Bottleneck
        │
        ▼
Generate Tasks
        │
        ▼
Validate Task Schema
        │
        ▼
Assign Priority
        │
        ▼
Queue Tasks
```

### 3.3 Scheduling Algorithm

```python
def calculate_priority(task, workers, experience):
    base_priority = task.base_priority
    
    # XP Bonus - 优先分配给有经验的 worker
    assigned_worker = find_best_worker(task, workers)
    xp_bonus = assigned_worker.xp * 0.1
    
    # Urgency Factor - 依赖链紧迫度
    urgency = calculate_dependency_urgency(task)
    
    # Risk Penalty - 高风险任务降权
    risk_penalty = task.risk_level == 'high' ? 0.2 : 0
    
    return base_priority + xp_bonus + urgency - risk_penalty
```

### 3.4 Failure Handling

```
Worker Fails
       ↓
Retry Count < Limit?
       │
       ├─ Yes → Retry with same worker
       │
       └─ No → Check failure type
                   │
                   ├─ validation_fail → Diagnostic Task
                   ├─ runtime_error → Request Help
                   ├─ missing_dependency → Block + Notify
                   └─ hallucination → Human Review
```

---

## 4. Worker Pool Architecture

### 4.1 Worker Lifecycle

```
IDLE → ASSIGNED → RUNNING → VERIFYING → COMPLETED
                ↓                    ↓
              FAILED              BLOCKED
                ↓
            RETRY/REQUEST_HELP
```

### 4.2 Worker Communication Protocol

```
Worker A                    Planner                    Worker B
   │                           │                          │
   │──Task Assignment─────────▶│                          │
   │                           │                          │
   │──Execute Task────────────▶│                          │
   │                           │                          │
   │──Fail + Help Request─────▶│                          │
   │                           │──Help Request───────────▶│
   │                           │                          │
   │                           │◀──Solution──────────────│
   │◀──Solution────────────────│                          │
   │                           │                          │
   │──Apply Solution─────────▶│                          │
   │                           │                          │
```

### 4.3 Worker Types & Capabilities

| Type | Model Source | Capabilities |
|------|-------------|--------------|
| Builder | Strong Model | code, config, api |
| Researcher | Cheap Model | search, analysis |
| Documenter | Expressive Model | doc, prd |
| Verifier | Reliable Model | test, validate |
| Evaluator | Data Model | metrics, benchmark |

---

## 5. Experience Ledger Architecture

### 5.1 Storage Structure

```
experience/
├── ledger.jsonl          # 经验主存储
├── index/                # 向量索引
│   ├── by_problem.jsonl
│   ├── by_solution.jsonl
│   └── by_pattern.jsonl
├── patterns/             # 提炼的模式
│   └── *.md
└── help_requests/        # 求助记录
    └── *.json
```

### 5.2 Retrieval Flow

```
Query: Error Message / Problem Description
        │
        ▼
Semantic Search (Vector Index)
        │
        ▼
Filter by Project / Worker Type
        │
        ▼
Rank by Reuse Count + XP
        │
        ▼
Return Top-K Experiences
```

---

## 6. Skill Hub Architecture

### 6.1 Skill Runtime

```
Skill Execution Environment
├── Filesystem Sandbox
│   ├── Read: project-specific paths
│   └── Write: experiments/ outputs/
├── Network Sandbox
│   ├── Allow: manifest whitelist
│   └── Deny: all else
├── Process Sandbox
│   └── Allow: declared commands only
└── Secrets
    └── Capability Tokens Only
```

### 6.2 Security Pipeline

```
Skill Installation Request
        │
        ▼
1. Manifest Validation
   - Required fields present
   - Permissions declared
   - Dependencies resolved
        │
        ▼
2. Static Security Scan
   - Detect: rm -rf, curl | bash
   - Detect: suspicious paths
   - Detect: dangerous dependencies
        │
        ▼
3. LLM Semantic Review
   - Intent analysis
   - Hidden risk detection
   - Permission over-request detection
        │
        ▼
4. Sandbox Execution
   - Run with mock data
   - Monitor file/network access
   - Verify behavior matches manifest
        │
        ▼
5. Human Approval (if required)
   - Generate Review Card
   - Founder decision
        │
        ▼
6. Activate / Quarantine
```

---

## 7. Policy Engine Architecture

### 7.1 Policy Layers

```
Policy Engine
├── Execution Policy
│   ├── Task Validation
│   ├── Concurrency Control
│   ├── Retry Management
│   └── Slowdown Logic
│
├── Safety Policy
│   ├── Secret Isolation
│   ├── Network Control
│   ├── Capability Enforcement
│   └── Incident Response
│
└── Quality Policy
    ├── Validator Requirements
    ├── Evidence Pack Standards
    ├── Verifier Independence
    └── KPI Gate
```

### 7.2 Policy Evaluation Flow

```
Action Request (Task / Skill / Connection)
        │
        ▼
Execution Policy Check
        │
        ├─ Pass → Safety Policy Check
        │
        └─ Fail → Reject + Log
                  │
                  ▼
           Safety Policy Check
                  │
                  ├─ Pass → Quality Policy Check
                  │
                  └─ Fail → Reject + Log
                            │
                            ▼
                     Quality Policy Check
                            │
                            ├─ Pass → Execute
                            │
                            └─ Fail → Reject + Log
```

---

## 8. Connection Manager Architecture

### 8.1 Connection Types

```
Connection Manager
├── LLM Connections
│   ├── Cloud (OpenAI, Anthropic, DeepSeek)
│   └── Local (Ollama, vLLM)
│
├── Search Connections
│   ├── Brave Search
│   ├── SerpAPI
│   └── Tavily
│
├── Repository Connections
│   ├── GitHub
│   └── GitLab
│
└── OAuth Connections
    ├── Google
    ├── Notion
    └── Slack
```

### 8.2 Token Generation Flow

```
Worker Request (Task with required_capabilities)
        │
        ▼
Validate Worker Permissions
        │
        ▼
Check Connection Quota
        │
        ▼
Generate Capability Token
        │
        ├─ Short-lived (15 min default)
        ├─ Scoped to task
        └─ Rate limited
        │
        ▼
Issue Token to Worker
```

---

## 9. Dashboard Architecture

### 9.1 UI Components

```
Dashboard
├── Header
│   ├── System Status
│   ├── Execution Mode
│   └── Quick Actions
│
├── Sidebar
│   ├── Ideas
│   ├── Projects
│   ├── Tasks
│   ├── Workers
│   ├── Experience
│   └── Settings
│
├── Main Content
│   ├── Project Path Graph
│   ├── Task Board
│   ├── Worker Monitor
│   └── Review Inbox
│
└── Footer
    ├── Cost Tracker
    └── System Health
```

### 9.2 Project Path Graph

```
Visual DAG Representation

Story Engine
│
├─ Skeleton Extraction
│     ├─ LLM Generate ✓
│     ├─ Schema Validator ✓
│     ├─ Conflict Curve Check ✓
│     └─ [HUMAN REVIEW] ← Current
│
├─ Skeleton Dataset
│
└─ Narrative Embedding
     ├─ Dataset Prepare ⚙
     └─ Model Train ⚙
```

---

## 10. Storage Layer

### 10.1 Recommended Storage

| Data Type | Storage |
|-----------|---------|
| Projects, Tasks | PostgreSQL |
| Artifacts | Object Storage (S3/MinIO) |
| Experience | PostgreSQL + Vector Index |
| Logs | Elasticsearch/Loki |
| Config | Git + Encrypted Secrets |

### 10.2 Data Flow

```
User Input → API Server → PostgreSQL
                          │
                          ▼
                    Cache Layer (Redis)
                          │
                          ▼
                    Object Storage
```

---

## 11. Security Architecture

### 11.1 Defense Layers

```
Outer Layer
├── Network Firewall
└── VPN/SSH Tunnel

Middle Layer
├── Authentication
├── Authorization
└── Capability Tokens

Inner Layer
├── Sandbox Execution
├── Secret Isolation
└── Audit Logging
```

### 11.2 Secret Management

```
Secrets never go to:
✗ Git repository
✗ Logs
✗ Prompts
✗ Worker memory

Secrets only go to:
✓ Connection Manager
✓ Encrypted Vault
✓ Capability Tokens (short-lived)
```

---

## 12. Observability Stack

### 12.1 Metrics

| Category | Metrics |
|----------|---------|
| System | Uptime, CPU, Memory, Disk |
| Workers | Active, Idle, Success Rate |
| Tasks | Queue Time, Execution Time, Success Rate |
| API | Latency, Throughput, Error Rate |
| Cost | Daily Spend, Budget Usage |

### 12.2 Logging

```
Log Levels:
- ERROR: System failures
- WARNING: Policy violations
- INFO: Normal operations
- DEBUG: Detailed traces

Log Structure:
{
  timestamp,
  level,
  component,
  action,
  actor,
  details,
  trace_id
}
```

---

## 13. Disaster Recovery

### 13.1 Kill Switch Procedures

```
1. Stop all new task dispatch
2. Cancel running tasks (graceful)
3. Revoke all capability tokens
4. Freeze execution
5. Notify founder
6. Generate incident report
```

### 13.2 Backup Strategy

```
Daily:
- Database snapshot
- Configuration backup

Weekly:
- Full artifact backup
- Experience ledger backup

On Change:
- Policy changes
- Connection updates
```

---

*Document Version: 1.0*
*Last Updated: 2026-03-04*
