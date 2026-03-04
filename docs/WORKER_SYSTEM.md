# Worker System Specification

## 1. Worker Overview

Worker 是 AI Founder OS 的执行单元，是构成"AI 工程团队"的基础。

### 1.1 Worker 核心职责

- 接收 Planner 分配的 Task
- 执行任务并生成 Artifact
- 运行 Validator
- 生成 EvidencePack
- 记录 Experience（失败时）

### 1.2 Worker 类型

| Type | 角色 | 核心能力 |
|------|------|---------|
| Builder | 工程师 | 代码实现、脚本生成、API 创建 |
| Researcher | 研究员 | 信息搜索、数据分析、方案调研 |
| Documenter | 文档工程师 | PRD 撰写、规范制定、技术文档 |
| Verifier | 质量工程师 | 测试执行、代码审查、结果验证 |
| Evaluator | 评估师 | KPI 评估、性能测试、数据分析 |

---

## 2. Worker Lifecycle

### 2.1 完整状态机

```
IDLE ──▶ ASSIGNED ──▶ RUNNING ──▶ VERIFYING ──▶ COMPLETED
  ▲                              │              │
  │                              │              │
  └──◀──── FAILED ◀──────────────┘              │
                                               │
                    BLOCKED ◀───────────────────┘
```

### 2.2 状态定义

| 状态 | 描述 | 可转换到 |
|------|------|---------|
| IDLE | 空闲，可接受任务 | ASSIGNED |
| ASSIGNED | 已分配任务，未开始 | RUNNING, IDLE (取消) |
| RUNNING | 执行中 | VERIFYING, FAILED, BLOCKED |
| VERIFYING | 等待验证 | COMPLETED, FAILED |
| COMPLETED | 任务完成 | IDLE |
| FAILED | 执行失败 | IDLE, RUNNING (重试) |
| BLOCKED | 被阻塞 | RUNNING (解决后) |

---

## 3. Worker XP Economy

### 3.1 XP 获取规则

```json
{
  "xp_rules": {
    "success_task": 1,
    "experience_reused": 2,
    "repeated_failure": -1,
    "blocker_resolved": 1
  }
}
```

### 3.2 XP 计算公式

```
XP_Total = Success_Count × 1 + Reused_Count × 2 - Failure_Count × 1
```

### 3.3 调度优先级

```python
def calculate_worker_priority(worker, task):
    # 基础分数
    priority = worker.xp_total
    
    # 成功率加权
    success_rate = worker.success_count / worker.total_tasks
    priority += success_rate * 10
    
    # 类型匹配
    if worker.type == task.routing_hints.worker_type:
        priority += 5
    
    # 当前负载
    if worker.status == 'idle':
        priority += 3
    
    return priority
```

### 3.4 Reputation System

```json
{
  "reputation_factors": {
    "success_rate": "完成率",
    "avg_resolution_time": "平均解决时间",
    "verifier_pass_rate": "验证通过率",
    "code_quality_score": "代码质量分"
  }
}
```

---

## 4. Worker Collaboration Protocol

### 4.1 Help Request Flow

```
Worker A 失败
    │
    ▼
搜索 Experience Ledger
    │
    ├─ 找到匹配经验 → 尝试复用
    │
    └─ 未找到 → 发起 Help Request
                    │
                    ▼
              Planner 路由到合适 Worker B
                    │
                    ▼
              Worker B 提供解决方案
                    │
                    ▼
              Worker A 应用并反馈
                    │
                    ▼
              记录 Experience + XP
```

### 4.2 Help Request Schema

```json
{
  "help_id": "help_...",
  "requester_worker_id": "worker_a",
  "project_id": "proj_...",
  "task_id": "task_...",
  "error_summary": "string",
  "attempts": ["tried_method_1", "tried_method_2"],
  "constraints": ["timebox_30min", "no_arch_change"],
  "desired_output": ["root_cause", "fix_steps", "verification"],
  "tags": ["importerror", "python", "deps"],
  "status": "pending|accepted|resolved|expired"
}
```

### 4.3 Experience Entry Schema

```json
{
  "exp_id": "exp_...",
  "timestamp": "ISO8601",
  "project": "string",
  "worker_id": "worker_...",
  "category": ["build", "dependency", "runtime", "logic", "test", "env"],
  "symptoms": ["exact_error"],
  "root_cause": "version_mismatch_package_X",
  "fix": ["pin_B==1.9", "update_import_path"],
  "reproduction": {
    "command": "pytest -q",
    "env": ["python_3.11", "ubuntu_22.04"]
  },
  "verification": {
    "command": "pytest -q",
    "result": "pass"
  },
  "reusability_tags": ["importerror", "version-pin", "python"],
  "confidence": 0.8,
  "status": "solved"
}
```

---

## 5. Worker 执行管道

### 5.1 标准执行流程

```
1. 接收 Subtask
        │
        ▼
2. 获取 Inputs
   - 读取任务描述
   - 下载相关 Artifacts
   - 获取 Context Pack
        │
        ▼
3. 准备 Environment
   - 设置工作目录
   - 配置环境变量
   - 加载 Capability Token
        │
        ▼
4. 调用 LLM
   - 选择模型
   - 构建 Prompt
   - 设置参数
        │
        ▼
5. 生成 Artifact
   - 写入文件
   - 生成配置
   - 创建测试
        │
        ▼
6. 运行 Validators
   - 执行测试
   - 检查 Schema
   - 生成报告
        │
        ▼
7. 生成 EvidencePack
   - 收集日志
   - 整理指标
   - 准备复现命令
        │
        ▼
8. 返回 Result Packet
```

### 5.2 Result Packet Schema

```json
{
  "subtask_id": "task_...",
  "status": "done|blocked|failed",
  "artifacts": [
    {"type": "file", "path": "string"},
    {"type": "command", "value": "string"}
  ],
  "summary": {
    "changes": ["string"],
    "decisions": ["string"]
  },
  "verification": {
    "tests_run": ["string"],
    "result": "pass|fail"
  },
  "open_issues": ["string"],
  "risks": ["string"]
}
```

---

## 6. Worker Registry

### 6.1 Registry Schema

```json
{
  "workers": [
    {
      "worker_id": "worker_builder_01",
      "worker_type": "builder",
      "model_source": "local_ollama:deepseek-8b",
      "fallback_model": "cloud_openai:gpt-4",
      "capabilities": ["cap_code", "cap_test"],
      "xp": {
        "total": 50,
        "success": 45,
        "failure": 5,
        "reused": 10
      },
      "status": "idle|busy|paused|error",
      "reputation": {
        "score": 0.9,
        "success_rate": 0.9,
        "avg_resolution_time_minutes": 30
      }
    }
  ]
}
```

### 6.2 Worker 初始化

```python
def initialize_worker(worker_type, model_source):
    worker = {
        "worker_id": generate_id(),
        "worker_type": worker_type,
        "model_source": model_source,
        "capabilities": get_capabilities(worker_type),
        "xp": {"total": 0, "success": 0, "failure": 0, "reused": 0},
        "status": "idle",
        "reputation": {"score": 1.0, "success_rate": 0.0}
    }
    return worker
```

---

## 7. Error Recovery

### 7.1 错误分类

| Error Type | 描述 | 处理方式 |
|------------|------|---------|
| validation_fail | 测试/指标未过 | 修复后重试 |
| runtime_error | 执行报错 | 诊断后重试 |
| missing_dependency | 缺文件/权限 | 阻塞 + 通知 |
| hallucination_detected | 输出不符合预期 | 触发验证 + 人工审查 |
| policy_denied | 权限/网络被拒 | 修改 task/capability |

### 7.2 自恢复流程

```
错误发生
    │
    ▼
判断错误类型
    │
    ├─ validation_fail → 尝试修复 → 重试 (最多2次)
    │
    ├─ runtime_error → 搜索经验 → 尝试方案
    │
    ├─ missing_dependency → 标记 blocked → 通知 Planner
    │
    └─ 其他 → 记录 Experience → 请求帮助
```

### 7.3 升级策略

```
连续失败 3 次
    │
    ▼
触发 Auto Slowdown
    │
    ├─ 并发 -1
    │
    ├─ 强制 Verifier
    │
    ├─ 切换到 diagnose 模式
    │
    └─ 生成诊断任务
```

---

## 8. Worker Context Pack

### 8.1 Context Pack 内容

每个任务分配时，Worker 收到一个 Context Pack：

```json
{
  "task": {
    "id": "task_...",
    "goal": "string",
    "inputs": {},
    "expected_artifact": {},
    "validators": [],
    "risk_level": "low|medium|high"
  },
  "project": {
    "id": "proj_...",
    "name": "string",
    "kpis": [],
    "constraints": {},
    "operating_mode": "safe|normal|turbo"
  },
  "context": {
    "related_files": ["file1", "file2"],
    "key_constraints": ["constraint1"],
    "relevant_experiences": ["exp_1", "exp_2"]
  },
  "capabilities": {
    "tokens": ["cap_..."],
    "connections": ["conn_..."]
  }
}
```

### 8.2 Context 限制

- 相关文件摘要：最多 2 页
- 关键约束：最多 5 条
- 相关经验：最多 3 条

---

*Document Version: 1.0*
