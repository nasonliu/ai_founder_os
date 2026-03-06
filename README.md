# AI Founder OS

> AI-Native 创业操作系统 - 让一个人拥有 AI 工程团队

[![Tests](https://github.com/nasonliu/ai_founder_os/actions/workflows/test.yml/badge.svg)](https://github.com/nasonliu/ai_founder_os/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> ⚡ 350 tests passing (100%)

## 概述

AI Founder OS 是一个 AI-native 创业操作系统，目标不是提供 AI 工具，而是构建一个由 AI Worker 组成的工程组织。

创始人通过系统可以：
- 管理想法 (Idea Management)
- 创建项目 (Project Creation)
- 调度 AI Worker (Worker Orchestration)
- 自动执行任务 (Autonomous Execution)
- 在关键节点进行决策 (Human Governance)

## 核心特性

### 🧠 智能 Planner
- 任务拆分与调度
- Worker 池管理
- 失败自动降速
- 诊断任务生成

### 👥 Worker 团队
- Builder (代码实现)
- Researcher (信息搜索)
- Documenter (文档撰写)
- Verifier (质量验证)
- Evaluator (性能评估)

### 📚 经验系统
- Worker XP 积分
- 经验复用机制
- 求助协作协议
- 诊断知识库

### 🔒 安全治理
- 三层策略引擎
- Capability Token 权限控制
- Human Gate 决策节点
- Secret 隔离管理

### 🔌 连接管理
- 多 LLM 支持 (OpenAI, Anthropic, DeepSeek, 本地模型)
- Search API (Brave, SerpAPI)
- GitHub 集成
- OAuth 支持

### 🎨 Dashboard
- 项目路径图
- 任务看板
- Worker 监控
- 经验账本

### 🗣️ 对话式控制
- 实时状态查询
- 任务控制
- 执行模式切换
- 审批管理

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Dashboard UI                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     Planner System                          │
│          (任务拆分 / Worker调度 / Human Gate触发)            │
└───────────┬─────────────────────────────────┬───────────────┘
            │                                 │
    ┌───────▼───────┐               ┌────────▼────────┐
    │  Worker Pool  │               │   Policy Engine  │
    │  Builder      │               │  Execution       │
    │  Researcher   │               │  Safety          │
    │  Documenter   │               │  Quality         │
    │  Verifier      │               └──────────────────┘
    │  Evaluator    │
    └───────┬───────┘
            │
    ┌───────▼───────┐     ┌──────────────┐     ┌─────────────┐
    │  Skill Hub   │     │ Experience   │     │ Connection  │
    │  技能安装    │     │ Ledger       │     │ Manager     │
    └──────────────┘     └──────────────┘     └─────────────┘
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ai_founder_os.git
cd ai_founder_os
```

### 2. 安装依赖

```bash
# Python 3.11+
pip install -r requirements.txt
```

### 3. 配置连接

在 `connections/` 目录下配置你的 API keys。

### 4. 启动 Agent

```bash
# 使用 AGENT_START_PROMPT.md 启动
python -m src.planner.planner
```

## 项目结构

```
ai_founder_os/
├── docs/                     # 项目文档
│   ├── PRD.md               # 产品需求文档
│   ├── ARCHITECTURE.md      # 系统架构
│   ├── WORKER_SYSTEM.md     # Worker 系统
│   ├── CONNECTION_MANAGER.md # 连接管理
│   └── *.md
│
├── prompts/                  # Agent 提示词
│   ├── system_prompt.md
│   ├── planner_prompt.md
│   ├── builder_prompt.md
│   ├── verifier_prompt.md
│   └── skill_review_prompt.md
│
├── schemas/                  # JSON Schema 定义
│   ├── idea.schema.json
│   ├── project.schema.json
│   ├── task.schema.json
│   ├── evidence_pack.schema.json
│   ├── review_card.schema.json
│   └── experience.schema.json
│
├── src/                      # 源代码
│   ├── planner/            # Planner 系统
│   ├── workers/            # Worker 实现
│   ├── skills/             # Skill Hub
│   ├── policy/             # 策略引擎
│   ├── connections/        # 连接管理
│   ├── experience/         # 经验账本
│   └── dashboard/          # Dashboard
│
├── tasks.json               # 任务列表
├── roadmap.md               # 项目路线图
└── AGENT_START_PROMPT.md   # Agent 启动提示词
```

## 文档

- [PRD 完整文档](docs/PRD.md)
- [架构设计](docs/ARCHITECTURE.md)
- [Worker 系统](docs/WORKER_SYSTEM.md)
- [连接管理](docs/CONNECTION_MANAGER.md)

## 核心原则

1. **Artifact First** - 所有任务必须产生可验证的产物
2. **Validator Driven** - 每个任务必须有验证器
3. **Human Governance** - 关键节点必须人工审批
4. **Incremental Execution** - 小步迭代，持续验证
5. **Auditable AI** - 所有行为可追溯
6. **Security First** - 安全优先

## 参与贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
