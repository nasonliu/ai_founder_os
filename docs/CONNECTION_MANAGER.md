# Connection Manager Specification

## 1. Overview

Connection Manager 统一管理系统所有外部服务连接，包括 LLM API、Search API、GitHub、OAuth 服务和本地模型。

### 1.1 核心目标

- 统一凭证管理 (Unified Credential Management)
- 能力令牌化 (Capability Tokenization)
- 预算控制 (Budget Control)
- 审计追踪 (Audit Trail)

---

## 2. Supported Providers

### 2.1 LLM Providers

| Provider | Auth Type | Models |
|----------|-----------|--------|
| OpenAI | API Key / OAuth | gpt-4, gpt-3.5-turbo |
| Anthropic | API Key | claude-3-opus, claude-3-sonnet |
| DeepSeek | API Key | deepseek-chat, deepseek-reasoner |
| Ollama | Local | deepseek-r1, qwen2.5, llama3 |
| vLLM | Local (OpenAI Compatible) | Various |

### 2.2 Search Providers

| Provider | Auth Type | Features |
|----------|-----------|----------|
| Brave Search | API Key | Web search, News |
| SerpAPI | API Key | Google search |
| Tavily | API Key | AI-optimized search |
| Bing | API Key | Web search |

### 2.3 Repository Providers

| Provider | Auth Type | Capabilities |
|----------|-----------|-------------|
| GitHub | OAuth / PAT | repo read/write, PR, issues |
| GitLab | OAuth / PAT | repo read/write, MR |

### 2.4 OAuth Services

| Service | Capabilities |
|---------|-------------|
| Google Drive | file read/write |
| Notion | page read/write |
| Slack | message send |

---

## 3. Connection Schema

### 3.1 Base Connection Schema

```json
{
  "connection_id": "conn_...",
  "provider": "openai|brave_search|github|ollama|...",
  "name": "My OpenAI Key",
  "auth_type": "api_key|oauth|local",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### 3.2 API Key Type Schema

```json
{
  "connection_id": "conn_...",
  "provider": "openai",
  "name": "Work Account",
  "auth_type": "api_key",
  "credentials": {
    "encrypted": true,
    "storage": "keychain",
    "key_ref": "openai_work_key"
  },
  "scopes": ["chat_completions", "embeddings"],
  "quota": {
    "type": "monthly",
    "limit": "100usd",
    "current": "25usd",
    "reset_at": "ISO8601"
  },
  "allowed_workers": ["worker_builder_01", "worker_builder_02"],
  "allowed_projects": ["proj_story_engine", "proj_ppc_agent"],
  "status": "active|expired|revoked",
  "health_check": {
    "enabled": true,
    "interval_minutes": 60,
    "last_check": "ISO8601",
    "status": "healthy|unhealthy|unknown"
  }
}
```

### 3.3 OAuth Type Schema

```json
{
  "connection_id": "conn_...",
  "provider": "github",
  "name": "Personal Account",
  "auth_type": "oauth",
  "credentials": {
    "encrypted": true,
    "storage": "vault",
    "refresh_token_ref": "github_refresh_token"
  },
  "oauth_config": {
    "client_id": "xxx",
    "scopes": ["repo", "user"],
    "token_type": "installation"
  },
  "scopes": ["repo_read", "repo_write", "pr_create"],
  "quota": {
    "type": "rate_limit",
    "limit": "5000/hour",
    "current": 4500
  },
  "allowed_workers": ["worker_builder_01"],
  "allowed_projects": ["proj_ai_founder_os"],
  "status": "active|expired|revoked",
  "expires_at": "ISO8601"
}
```

### 3.4 Local Model Schema

```json
{
  "connection_id": "conn_...",
  "provider": "ollama",
  "name": "Local DeepSeek",
  "auth_type": "local",
  "local_config": {
    "endpoint": "http://localhost:11434",
    "models": [
      {
        "name": "deepseek-r1:8b",
        "context_limit": 32768,
        "recommended_for": ["builder", "reasoning"]
      },
      {
        "name": "qwen2.5:14b",
        "context_limit": 32768,
        "recommended_for": ["documenter"]
      }
    ],
    "concurrency_limit": 2
  },
  "allowed_workers": ["worker_builder_01", "worker_doc_01"],
  "allowed_projects": ["proj_story_engine"],
  "status": "active",
  "health_check": {
    "enabled": true,
    "interval_minutes": 5,
    "last_check": "ISO8601",
    "status": "healthy"
  }
}
```

---

## 4. Capability Token System

### 4.1 Capability Token Schema

```json
{
  "token_id": "cap_...",
  "connection_id": "conn_...",
  "issued_to": {
    "worker_id": "worker_...",
    "task_id": "task_..."
  },
  "permissions": [
    "llm.call",
    "search.query"
  ],
  "restrictions": {
    "max_requests_per_minute": 30,
    "max_daily_cost": "5usd",
    "models_allowed": ["deepseek-r1:8b", "gpt-4"],
    "rate_limit": {
      "rpm": 30,
      "tpm": 100000
    }
  },
  "issued_at": "ISO8601",
  "expires_at": "ISO8601",
  "status": "active|revoked|expired"
}
```

### 4.2 Token Generation Flow

```
Worker 请求 (Task 需要 capabilities)
        │
        ▼
验证 Worker 权限
        │
        ▼
检查 Connection 配额
        │
        ├─ 配额充足 → 生成 Token
        │
        └─ 配额不足 → 拒绝 + 通知
              │
              ▼
        设置 Token 权限
              │
              ▼
        设置过期时间 (默认 15 分钟)
              │
              ▼
        签发 Token
```

### 4.3 权限类型定义

```json
{
  "permission_types": {
    "llm": [
      "llm.call",
      "llm.embeddings",
      "llm.batch"
    ],
    "search": [
      "search.query",
      "search.fetch"
    ],
    "github": [
      "github.repo.read",
      "github.repo.write",
      "github.pr.create",
      "github.issue.write"
    ],
    "filesystem": [
      "fs.read",
      "fs.write"
    ]
  }
}
```

---

## 5. Routing Rules

### 5.1 默认路由策略

```json
{
  "routing_rules": {
    "builder": {
      "primary": "local_ollama:deepseek-8b",
      "fallback": "cloud_openai:gpt-4",
      "retry_on_failure": true
    },
    "researcher": {
      "primary": "local_ollama:qwen2.5",
      "fallback": "brave_search",
      "retry_on_failure": true
    },
    "documenter": {
      "primary": "local_ollama:qwen2.5",
      "fallback": "cloud_openai:gpt-3.5-turbo",
      "retry_on_failure": false
    },
    "verifier": {
      "primary": "cloud_openai:gpt-4",
      "fallback": "cloud_anthropic:claude-3",
      "retry_on_failure": false
    },
    "evaluator": {
      "primary": "local_ollama:deepseek-8b",
      "fallback": "cloud_openai:gpt-4",
      "retry_on_failure": true
    }
  }
}
```

### 5.2 自动升级条件

```json
{
  "auto_upgrade_conditions": [
    "consecutive_failures >= 2",
    "verifier_confidence < 0.5",
    "task_priority == P0",
    "task_risk_level == high"
  ]
}
```

---

## 6. Budget Control

### 6.1 预算规则

```json
{
  "budget_rules": {
    "default_daily_limit": "10usd",
    "warning_threshold": 0.8,
    "hard_limit_action": "pause_all_tasks",
    "per_project_limit": {
      "proj_story_engine": "5usd/day",
      "proj_ppc_agent": "3usd/day"
    }
  }
}
```

### 6.2 成本追踪

| Metric | Description |
|--------|-------------|
| daily_spend | 今日消费 |
| weekly_spend | 本周消费 |
| project_spend | 项目累计消费 |
| model_spend | 按模型分类的消费 |

---

## 7. Health Check

### 7.1 检查项

- API 连通性
- 认证有效性
- 配额剩余
- 响应时间

### 7.2 故障处理

```
Health Check 失败
        │
        ▼
标记 Connection 状态为 unhealthy
        │
        ▼
通知 Planner
        │
        ▼
切换到备用 Connection
        │
        ▼
生成 Review Card (如果关键)
```

---

## 8. Security Requirements

### 8.1 凭证存储

- **必须**: 加密存储 (Keychain, Vault, Encrypted File)
- **禁止**: 明文存储在配置文件
- **禁止**: 提交到 Git

### 8.2 日志脱敏

```
日志中禁止出现:
✗ API Keys
✗ Access Tokens
✗ Refresh Tokens
✗ OAuth Tokens

日志中可以出现:
✓ Connection ID
✓ Provider Name (不含凭证)
✓ Usage Metrics
✓ Error Codes
```

### 8.3 轮换策略

```json
{
  "rotation_policy": {
    "api_keys": {
      "auto_rotate": true,
      "rotation_days": 90
    },
    "oauth_tokens": {
      "auto_refresh": true,
      "refresh_before_expiry_hours": 24
    }
  }
}
```

---

*Document Version: 1.0*
