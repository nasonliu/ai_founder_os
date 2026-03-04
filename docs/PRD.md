# AI Founder OS - Product Requirements Document

## 1. Vision

AI Founder OS 是一个 AI-native 创业操作系统。

**目标**：不是提供 AI 工具，而是构建一个由 AI Worker 组成的工程组织。

Founder 通过系统可以：
- 管理想法 (Idea Management)
- 创建项目 (Project Creation)
- 调度 AI Worker (Worker Orchestration)
- 自动执行任务 (Autonomous Execution)
- 在关键节点进行决策 (Human Governance)

**最终目标**：让一个创始人拥有一支 AI 工程团队。

---

## 2. Problem Statement

当前 AI 工具存在三个核心问题：

### 2.1 AI 无法长期执行复杂项目

LLM 只能：
- 回答问题
- 生成内容

但无法：
- 管理任务
- 控制进度
- 协调团队

### 2.2 Agent 系统容易产生幻觉

例如：
- AI 生成错误代码
- AI 生成错误架构
- AI 生成无效数据

但系统仍然继续执行，导致大量无用计算。

### 2.3 缺乏治理系统

大多数 Agent 框架没有：
- 安全机制 (Security)
- 经验系统 (Experience)
- 错误恢复 (Error Recovery)
- 人类决策节点 (Human Gate)

---

## 3. Core Principles

AI Founder OS 设计遵循六个原则：

### 3.1 Artifact First
所有任务必须产生 Artifact：
- 代码 (Code)
- 文档 (Documentation)
- 配置 (Configuration)
- 数据集 (Dataset)
- 测试结果 (Test Results)

### 3.2 Validator Driven
每个任务必须包含 Validator：
- 单元测试 (Unit Test)
- Schema 验证 (Schema Validation)
- 基准测试 (Benchmark)

### 3.3 Human Governance
关键节点必须经过 Human Gate：
- Founder 保留最终决策权

### 3.4 Incremental Execution
所有工作必须拆分为小任务，确保可验证。

### 3.5 Auditable AI
系统所有行为必须：
- 记录日志 (Log)
- 可回溯 (Traceable)
- 可解释 (Explainable)

### 3.6 Security First
系统必须：
- 隔离 secrets (Secret Isolation)
- 控制权限 (Permission Control)
- sandbox 执行 (Sandbox Execution)

---

## 4. System Overview

AI Founder OS 由以下核心模块组成：

```
┌─────────────────────────────────────────────────────────┐
│                    Idea System                          │
│              (想法捕捉、组织、优先级排序)                 │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   Project System                        │
│              (项目卡片、目标、KPI、约束)                  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    Planner System                       │
│     (任务拆分、Worker调度、进度控制、Human Gate触发)      │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Worker Pool  │ │   Skill Hub   │ │Experience LED │
│  Builder      │ │  技能安装     │ │   经验账本    │
│  Researcher   │ │  安全审核     │ │   XP积分     │
│  Documenter   │ │  权限控制     │ │   复用机制    │
│  Verifier     │ └───────────────┘ └───────────────┘
│  Evaluator    │
└───────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                   Policy Engine                          │
│     (Execution Policy / Safety Policy / Quality Policy)  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                Connection Manager                        │
│     (API Keys / OAuth / Local Models / Capability)       │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                      Dashboard                           │
│    (Project Path Graph / Review Cards / Observability)   │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Idea System

Founder 持续产生新的想法。系统必须能够：
- 记录想法 (Record)
- 分类 (Categorize)
- 评估价值 (Evaluate)
- 转化为项目 (Convert to Project)

### 5.1 Idea Card Schema

```json
{
  "schema_version": "1.0",
  "id": "idea_...",
  "title": "string",
  "description": "string",
  "tags": ["string"],
  "priority": "P0|P1|P2|P3",
  "value_hypothesis": "string",
  "risk_level": "low|medium|high",
  "status": "new|triaged|parked|converted",
  "links": {
    "related_projects": ["proj_..."],
    "references": ["url_or_doc_id"]
  },
  "created_by": "human|planner",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 5.2 行为规则

- Idea 不允许直接进入执行队列，必须先转换为 Project
- Priority 由 human 或 planner 建议，但 human 可覆盖

---

## 6. Project System

Project 是执行单位。Planner 的所有调度必须以 Project 为边界进行治理。

### 6.1 Project Card Schema

```json
{
  "schema_version": "1.0",
  "id": "proj_...",
  "name": "string",
  "one_sentence_goal": "string",
  "kpis": [
    {
      "name": "string",
      "target": "string",
      "validator": "string",
      "priority": "P0|P1|P2"
    }
  ],
  "definition_of_done": ["string"],
  "constraints": {
    "must_not": ["string"],
    "must_use": ["string"]
  },
  "operating_mode": "safe|normal|turbo",
  "execution_limits": {
    "max_concurrency": 3,
    "retry_limit": 3
  },
  "routing_policy": {
    "default_llm_connection": "conn_...",
    "fallback_llm_connection": "conn_...",
    "prefer_local_model": true
  },
  "governance": {
    "require_pr_only": true,
    "require_verifier_for": ["high_risk", "production"],
    "human_gate_required_for": [
      "skills.install",
      "connections.scope_change",
      "repo.write"
    ]
  },
  "status": "active|paused|completed|archived",
  "current_bottleneck": "string",
  "next_3_tasks": ["task_..."],
  "created_by": "human|planner",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 6.2 行为规则

- Planner 每轮循环开始必须读取该 Project Card
- 若 status=paused，planner 不得派发新任务
- operating_mode 会影响 policy

---

## 7. Planner System

Planner 是系统调度核心。

### 7.1 职责

- 拆分任务 (Task Decomposition)
- 调度 Worker (Worker Scheduling)
- 控制并发 (Concurrency Control)
- 监控进度 (Progress Monitoring)
- 触发 Human Gate (Human Gate Triggering)

### 7.2 Planner 输入

- PRD
- Project Card
- tasks.json
- roadmap.md
- Experience Ledger

### 7.3 Planner 输出

- task queue
- worker assignments
- progress reports

### 7.4 Planner Loop

```
WHILE system_running:
    1. 读取所有 Project Cards
    2. 识别当前瓶颈 (Identify Bottleneck)
    3. 生成/更新 Tasks
    4. 选择下一个 Task (按优先级 + XP + 风险)
    5. 拆分为 Subtasks
    6. 分配给合适的 Worker
    7. 监控执行状态
    8. 处理验证结果
    9. 更新 Task 状态
    10. 触发 Human Gate (如需要)
    11. 更新 Dashboard
    12. 生成 Daily Report
```

### 7.5 调度算法

**优先级计算**：
```
Priority = Base_Priority + XP_Bonus + Urgency_Factor - Risk_Penalty
```

- Base_Priority: 任务固有优先级
- XP_Bonus: 执行 Worker 的经验值
- Urgency_Factor: 依赖链紧迫度
- Risk_Penalty: 高风险任务的降权

### 7.6 失败处理 (Auto Slowdown)

当连续失败 >= 3 次：
1. 降低并发 (Concurrency - 1)
2. 强制 Verifier
3. 生成诊断任务 (Diagnostic Task)
4. 切换到 diagnose 模式

---

## 8. Task Model

Task 是 Planner 派发的最小执行单位。

### 8.1 Task Schema

```json
{
  "schema_version": "1.0",
  "id": "task_...",
  "project_id": "proj_...",
  "title": "string",
  "goal": "string",
  "inputs": {
    "documents": ["doc_id_or_path"],
    "artifacts": ["artifact_id_or_path"],
    "urls": ["string"],
    "parameters": {}
  },
  "expected_artifact": {
    "type": "code|doc|config|dataset|report|test|schema",
    "path_hint": "string",
    "acceptance_criteria": ["string"]
  },
  "validators": [
    {
      "id": "val_...",
      "type": "unit_test|schema_check|benchmark|lint|human_review|custom_script",
      "command": "string",
      "success_criteria": "string",
      "blocking": true
    }
  ],
  "risk_level": "low|medium|high",
  "required_capabilities": ["cap_..."],
  "routing_hints": {
    "worker_type": "builder|researcher|documenter|verifier|evaluator",
    "preferred_connection": "conn_...",
    "fallback_connection": "conn_..."
  },
  "state": "created|queued|assigned|running|needs_review|verifying|verified|failed|canceled|blocked",
  "retry_count": 0,
  "depends_on": ["task_..."],
  "created_by": "planner|human",
  "assigned_to": {
    "worker_id": "worker_...",
    "assigned_at": "ISO8601"
  },
  "timestamps": {
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "started_at": "ISO8601",
    "ended_at": "ISO8601"
  }
}
```

### 8.2 Task 分层

- **Epic**: 跨多天的大目标 (仅用于规划)
- **Task**: 可执行目标 (必须有 expected_artifact & validator)
- **Subtask**: Task 的拆分 (同样必须可验证)

### 8.3 Task 生命周期状态机

```
created → queued → assigned → running
                              ↓
                    needs_review | verifying | failed | blocked
                              ↓                    ↓
                        verified              queued (retry)
                              ↓                    ↓
                        completed          blocked (human)
```

### 8.4 状态转换规则

| 当前状态 | 下一状态 | 触发条件 |
|---------|---------|---------|
| created | queued | Planner 派发 |
| queued | assigned | Worker 接受 |
| assigned | running | Worker 开始执行 |
| running | verifying | 执行完成，等待验证 |
| running | needs_review | 需要 Human Gate |
| running | failed | 执行错误 |
| running | blocked | 依赖缺失 |
| verifying | verified | 所有 validators 通过 |
| verifying | failed | validators 失败 |
| failed | queued | retry_count < retry_limit |
| failed | blocked | retry_count >= retry_limit |
| needs_review | queued | Human approved |
| needs_review | canceled | Human rejected |

---

## 9. Worker System

Worker 是 AI 执行节点。

### 9.1 Worker Types

| Worker Type | 职责 | 典型任务 |
|------------|------|---------|
| Builder | 写代码、生成 API、生成脚本 | 实现功能、修复 bug |
| Researcher | 搜索信息、数据分析 | 技术调研、方案对比 |
| Documenter | 写文档、更新 PRD | 文档撰写、规范制定 |
| Verifier | 运行测试、验证 artifact | 测试执行、代码审查 |
| Evaluator | KPI 评估、性能测试 | 性能分析、指标评估 |

### 9.2 Worker Schema

```json
{
  "worker_id": "worker_...",
  "worker_type": "builder|researcher|documenter|verifier|evaluator",
  "model_source": "local_ollama:deepseek-8b|cloud_openai:gpt-4|...",
  "capability_tokens": ["cap_..."],
  "xp": {
    "total": 0,
    "success": 0,
    "failure": 0,
    "reused": 0
  },
  "status": "idle|busy|paused|error",
  "current_task_id": "task_...",
  "reputation": {
    "score": 1.0,
    "success_rate": 0.0,
    "avg_resolution_time": 0
  }
}
```

### 9.3 Worker XP Economy

**XP 规则**：
- +1 XP: 成功完成任务
- +2 XP: 经验被其他 worker 复用
- -1 XP: 重复失败

**XP 计算公式**：
```
XP = success_count + 2 * reused_count - failure_count
```

**调度优先级**：
```
Priority = XP + Availability + Success_Rate
```

### 9.4 Worker 协作协议

当 Worker 遇到问题时：

```
Worker A 失败
    ↓
搜索 Experience Ledger
    ↓
找到相关经验?
        ├ 是 → 尝试复用 → 成功?
        │           ├ 是 → 记录 XP → 完成
        │           └ 否 → 请求帮助
        │
        └ 否 → 请求其他 Worker 帮助
                    ↓
              Worker B 响应
                    ↓
              解决方案共享
                    ↓
              原始 Worker 获得 XP
```

### 9.5 Worker 执行管道

```
1. 接收 Task
2. 获取 Inputs
3. 调用 LLM
4. 生成 Artifact
5. 运行 Validator
6. 生成 EvidencePack
7. 返回 Result Packet
```

---

## 10. Experience Ledger

Experience Ledger 是系统知识库。

### 10.1 Experience Schema

```json
{
  "schema_version": "1.0",
  "id": "exp_...",
  "project_id": "proj_...",
  "problem": {
    "title": "string",
    "symptoms": ["string"],
    "error_signatures": ["string"]
  },
  "context": {
    "where": "module/path",
    "conditions": ["string"],
    "related_tasks": ["task_..."]
  },
  "solution": {
    "steps": ["string"],
    "patch_hint": "string",
    "validation": ["string"]
  },
  "reusable_pattern": {
    "when_to_apply": "string",
    "template": "string"
  },
  "contributor": {
    "worker_id": "worker_...",
    "credited_xp": 0
  },
  "reuse": {
    "count": 0,
    "reused_by_workers": ["worker_..."]
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 10.2 经验复用流程

1. Worker 遇到错误
2. 搜索 Experience Ledger (按 tags + 语义)
3. 找到匹配经验
4. 尝试复用
5. 成功则给贡献者 +XP
6. 失败则发起 Help Request

---

## 11. Skill Hub

Skill 是系统能力扩展。

### 11.1 支持的 Skill 类型

- **Search**: Brave Search, SerpAPI, Tavily
- **Code**: GitHub Automation, Deployment
- **Data**: Data Pipeline, ETL
- **Analysis**: Code Review, Metrics
- **Deployment**: Docker, K8s, Cloud

### 11.2 Skill Manifest Schema

```json
{
  "name": "string",
  "version": "string",
  "author": "string",
  "source": "openclaw_hub|private|local",
  "description": "string",
  "entrypoints": ["action_name"],
  "permissions": {
    "filesystem": {
      "read": ["paths"],
      "write": ["paths"]
    },
    "network": {
      "allow_domains": ["string"],
      "deny_domains": ["string"]
    },
    "secrets": ["cap_..."],
    "process": {
      "allow_commands": ["string"]
    }
  },
  "dependencies": ["string"],
  "runtime": "python|node|bash|docker",
  "checks": ["test_command"],
  "signature": "hash_or_signature",
  "quarantine": true,
  "security_status": "pending|approved|rejected"
}
```

### 11.3 Skill 安全审核流程

```
1. 下载 Skill
       ↓
2. Static Scan (静态扫描)
   - 检查权限声明
   - 检查依赖风险
   - 检查可疑命令
       ↓
3. LLM Security Review (语义审查)
   - 意图分析
   - 隐蔽风险检测
   - 权限过度申请检测
       ↓
4. Sandbox Execution (沙盒测试)
   - 假数据运行
   - 监控文件访问
   - 监控网络访问
       ↓
5. Human Approval (人工审批)
   - 生成 Review Card
   - Founder 决策
       ↓
6. 激活 / 隔离
   - 通过 → 加入可用池
   - 拒绝 → 移除
```

### 11.4 默认策略

- 新 Skill 默认 quarantine = true
- 必须通过 Human Gate 才能进入生产可用
- 安装后需要试运行验收

---

## 12. Policy Engine

Policy Engine 负责系统治理，包含三层策略。

### 12.1 Execution Policy

**任务执行规则**：

1. 每个 Task 必须包含：
   - goal
   - inputs
   - expected_artifact
   - validator
   - risk_level

2. 失败规则：
   ```
   连续失败 3 次
       ↓
   AUTO_SLOWDOWN
       ↓
   降低并发
       ↓
   强制 Verifier
       ↓
   生成诊断任务
   ```

3. 并发控制：
   - 默认最大并发: 3
   - Safe Mode: 1
   - Turbo Mode: 5

### 12.2 Safety Policy

**安全规则**：

1. **Secret 管理**：
   - Secrets 不允许进入 git
   - Secrets 不允许进入 logs
   - Secrets 不允许进入 prompts

2. **凭证隔离**：
   - Worker 只获得 capability tokens
   - 不直接持有长期 key

3. **网络控制**：
   - Skill 默认 deny_all_network
   - 只允许 manifest allowlist

4. **Incident 响应**：
   - 检测到泄露 → 暂停 worker
   - 生成 incident report
   - 通知 Founder

### 12.3 Quality Policy

**质量规则**：

1. **Validator 必须存在**：
   - 每个 Task 必须有至少 1 个 validator
   - 至少 1 个 blocking=true

2. **Evidence Pack 必须完整**：
   - artifact 引用
   - repro command
   - validation result

3. **Verifier 独立性**：
   - Verifier ≠ Builder
   - 关键任务必须独立验证

4. **KPI Gate**：
   - 每个项目必须定义 KPI
   - KPI 未达标不允许继续 build

---

## 13. Connection Manager

管理外部服务连接。

### 13.1 支持的 Provider 类型

| Category | Providers |
|----------|----------|
| LLM | OpenAI, Anthropic, DeepSeek, Local (Ollama, vLLM) |
| Search | Brave Search, SerpAPI, Tavily, Bing |
| Code/Repo | GitHub, GitLab |
| Cloud | AWS, GCP, Cloudflare |
| Data | Notion, Google Drive, Slack |

### 13.2 Connection Schema

```json
{
  "connection_id": "conn_...",
  "provider": "openai|brave_search|github|ollama|...",
  "name": "string",
  "auth_type": "api_key|oauth|local",
  "credentials": {
    "encrypted": true,
    "storage": "keychain|vault|file"
  },
  "scopes": ["read|write"],
  "quota": {
    "type": "monthly|usage_based",
    "limit": "string",
    "current": 0
  },
  "allowed_workers": ["worker_..."],
  "allowed_projects": ["proj_..."],
  "status": "active|expired|revoked",
  "last_used": "ISO8601",
  "health_check": {
    "last_check": "ISO8601",
    "status": "healthy|unhealthy|unknown"
  }
}
```

### 13.3 Capability Token Model

Worker 不直接获得 credentials，只获得 Capability Token：

```json
{
  "token_id": "cap_...",
  "connection_id": "conn_...",
  "permissions": ["llm.call", "search.query", "github.read"],
  "restrictions": {
    "max_rpm": 60,
    "max_daily_cost": "10usd",
    "models_allowed": ["deepseek-8b", "gpt-4"]
  },
  "issued_at": "ISO8601",
  "expires_at": "ISO8601",
  "issued_to": "worker_..."
}
```

### 13.4 本地模型支持

支持的本地模型运行时：
- Ollama
- vLLM
- LM Studio
- OpenAI Compatible APIs

**配置示例**：
```json
{
  "provider": "ollama",
  "endpoint": "http://localhost:11434",
  "models": ["deepseek-r1:8b", "qwen2.5:14b"],
  "concurrency": 2,
  "context_limit": 8192
}
```

### 13.5 路由策略

**默认路由规则**：
- Doc Worker: 本地/便宜模型
- Builder: 本地强模型
- Verifier: 云端可靠模型
- Research: 便宜模型

**自动升级条件**：
- 连续 2 次失败
- Verifier 判定低可信
- 任务标记 P0/P1

---

## 14. Evidence Pack System

EvidencePack 是系统抑制幻觉的核心机制。

### 14.1 EvidencePack Schema

```json
{
  "schema_version": "1.0",
  "id": "evp_...",
  "project_id": "proj_...",
  "task_id": "task_...",
  "artifact_ids": ["artifact_..."],
  "repro": {
    "commands": ["string"],
    "environment": {
      "os": "string",
      "runtime": "python|node|bash|docker",
      "versions": {}
    }
  },
  "validation": [
    {
      "validator_id": "val_...",
      "status": "pass|fail|skipped",
      "output_uri": "file_path_or_log_ref",
      "summary": "string"
    }
  ],
  "metrics": [
    {
      "name": "string",
      "value": "string|number",
      "threshold": "string",
      "pass": true
    }
  ],
  "logs": {
    "stdout_tail": "string",
    "stderr_tail": "string",
    "sanitized": true
  },
  "diff_summary": {
    "files_changed": ["string"],
    "lines_added": 0,
    "lines_removed": 0
  },
  "risk_note": {
    "uncertainty": "low|medium|high",
    "assumptions": ["string"],
    "known_limits": ["string"]
  },
  "created_by": "worker|verifier",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 14.2 Evidence Gate 规则

**Task 完成必要条件**：
1. Artifact 已登记
2. EvidencePack 已生成
3. 所有 blocking validators 通过
4. 提供 repro command

### 14.3 不同任务类型的证据要求

| Task Type | 最小证据要求 |
|-----------|-------------|
| Code | 单测通过 + diff summary + repro |
| Doc | 链接引用 + 结构检查 |
| Research | 引用来源 + 可复现检索步骤 |
| Data | schema validation + sample preview |
| Deploy | dry-run 结果 + 回滚方案 |

---

## 15. Human Gate System

Human Gate 是系统控制点。

### 15.1 触发条件

以下情况必须触发 Human Gate：

- Skill 安装 (Skill Installation)
- 架构变更 (Architecture Change)
- Repo 写操作 (Repository Write)
- Policy 修改 (Policy Change)
- KPI 失败 (KPI Failure)
- Connection 权限变更 (Connection Scope Change)

### 15.2 Review Card Schema

```json
{
  "schema_version": "1.0",
  "id": "gate_...",
  "project_id": "proj_...",
  "type": "task_review|skill_install|connection_scope|policy_change|kpi_failure|repo_write",
  "risk_level": "low|medium|high",
  "context": {
    "summary": "string",
    "why_now": "string",
    "affected_entities": ["task_...", "skill_...", "conn_..."]
  },
  "proposal": {
    "change": "string",
    "options": [
      {
        "id": "opt1",
        "description": "string",
        "tradeoffs": ["string"]
      }
    ],
    "recommended_option": "opt1"
  },
  "evidence_ids": ["evp_..."],
  "impact_preview": {
    "files": ["string"],
    "permissions": ["string"],
    "cost_estimate": "string",
    "time_estimate": "string"
  },
  "status": "pending|approved|rejected|modified",
  "resolution": {
    "by": "human",
    "decision": "approved|rejected|modified",
    "notes": "string",
    "constraints_added": ["string"],
    "resolved_at": "ISO8601"
  },
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 15.3 审批操作

- **Approve**: 通过
- **Reject**: 拒绝
- **Modify**: 带条件通过 (添加约束)

### 15.4 Dashboard 集成

Dashboard 显示：
- Review Inbox (待审批卡片)
- Gate Health (审批统计)
- 最近决策列表

---

## 16. Realtime Conversational Control

Founder 可以通过对话实时控制 Planner。

### 16.1 支持的控制类型

#### 状态查询
- `status` - 系统状态
- `project status` - 项目状态
- `worker status` - Worker 状态
- `next gate` - 下一个需要审批的节点
- `blockers` - 当前阻塞点

#### 任务控制
- `add task` - 新增任务
- `cancel task` - 取消任务
- `reprioritize task` - 调整优先级
- `force retry` - 强制重试

#### 执行控制
- `pause project` - 暂停项目
- `resume project` - 恢复项目
- `set concurrency N` - 设置并发数
- `safe mode` / `normal mode` / `turbo mode` - 切换模式
- `kill switch` - 紧急停止

#### 路由控制
- `reroute local` - 优先本地模型
- `reroute cloud` - 优先云端模型
- `require verifier` - 强制验证

### 16.2 命令解析

自然语言示例：
```
"暂停 story-engine 项目，并把并发改为 2。"
```

解析为结构化命令：
```json
{
  "commands": [
    {"type": "pause_project", "project": "story-engine"},
    {"type": "set_concurrency", "value": 2}
  ]
}
```

### 16.3 高风险指令确认

对于高风险操作，需要二次确认：
```
"确认要对 main 分支启用直接 push 吗？这将绕过 PR Only。"
```

必须回复 `confirm` 才执行。

### 16.4 Command Audit

每条指令记录：
```json
{
  "command_id": "cmd_...",
  "user_message": "string",
  "parsed_command": {},
  "policy_result": "pass|denied",
  "gate_required": true,
  "execution_result": "success|failed",
  "timestamp": "ISO8601"
}
```

---

## 17. Dashboard & Observability

### 17.1 Dashboard 结构

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard                                │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   Ideas     │  Projects   │   Tasks     │    Workers      │
│   想法流    │   项目空间   │   任务板    │    Worker池     │
├─────────────┴─────────────┴─────────────┴─────────────────┤
│                    Project Path Graph                       │
│              (项目路径图 + 关键节点)                         │
├─────────────────────────────────────────────────────────────┤
│               Review Inbox (Human Gate)                    │
│                    (待审批卡片)                              │
├─────────────────────────────────────────────────────────────┤
│                  Experience Ledger                          │
│                    (经验账本)                               │
├─────────────────────────────────────────────────────────────┤
│                   Observability                            │
│    (API使用 / Worker状态 / 成本 / 错误率)                   │
└─────────────────────────────────────────────────────────────┘
```

### 17.2 Project Path Graph

显示项目进展的可视化图：

```
Idea
  ↓
Task
  ↓
Subtask
  ↓
Artifact
  ↓
Validator ✓
  ↓
Verifier ✓
  ↓
[HUMAN REVIEW] ← 你在这里
  ↓
Dataset
  ↓
Training
```

### 17.3 Observability 指标

| 指标 | 描述 |
|------|------|
| Worker Success Rate | Worker 成功率 |
| Task Latency | 任务延迟 |
| API Usage | API 调用量 |
| Model Latency | 模型延迟 |
| Error Frequency | 错误频率 |
| Cost | 成本消耗 |

---

## 18. Execution Modes

系统支持三种执行模式：

| Mode | 并发数 | 行为 |
|------|--------|------|
| Safe | 1 | 只允许 doc / test |
| Normal | 3 | 标准执行 |
| Turbo | 5 | 高并发执行 |

---

## 19. Disaster Recovery

### 19.1 Kill Switch

紧急停止系统：
- 停止所有 Worker
- 撤销所有 Tokens
- 冻结执行

### 19.2 备份策略

- 自动备份 keystore/vault
- Repo 保护分支策略
- Incident 一键 revoke + rotate

---

## 20. System Philosophy

**AI Founder OS 的核心理念**：

```
AI ≠ 工具
AI = 工程组织
```

Founder 是 AI 团队的指挥官。

**系统目标**：让一个人可以通过 AI 组织完成复杂项目。

---

## 21. File Structure

```
ai_founder_os/
├── docs/
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── WORKER_SYSTEM.md
│   ├── SKILL_HUB.md
│   ├── CONNECTION_MANAGER.md
│   ├── EXECUTION_POLICY.md
│   ├── SAFETY_POLICY.md
│   └── QUALITY_POLICY.md
│
├── prompts/
│   ├── system_prompt.md
│   ├── planner_prompt.md
│   ├── builder_prompt.md
│   ├── verifier_prompt.md
│   └── skill_review_prompt.md
│
├── schemas/
│   ├── idea.schema.json
│   ├── project.schema.json
│   ├── task.schema.json
│   ├── artifact.schema.json
│   ├── evidence_pack.schema.json
│   ├── review_card.schema.json
│   └── experience.schema.json
│
├── src/
│   ├── planner/
│   ├── workers/
│   ├── skills/
│   ├── policy/
│   ├── connections/
│   ├── experience/
│   └── dashboard/
│
├── tasks.json
├── roadmap.md
└── AGENT_START_PROMPT.md
```

---

*Document Version: 1.0*
*Last Updated: 2026-03-04*
