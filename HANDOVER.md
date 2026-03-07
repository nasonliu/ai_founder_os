# AI Founder OS - 项目交接文档

## 📋 项目概述

**AI Founder OS** 是一个面向创始人的 AI 原生操作系统，旨在通过 AI 自动化完成创业过程中的各种任务。

---

## ✅ 已完成功能

### 1. 核心系统
- [x] Planner Loop - 任务规划和决策系统
- [x] Worker Registry - AI Worker 注册和管理
- [x] Policy Engine - 策略引擎和规则系统
- [x] Connection Manager - 连接管理
- [x] Experience Ledger - 经验记录
- [x] Skill Hub Loader - 技能加载器
- [x] Human Gate System - 人工审核系统

### 2. Dashboard (11个面板)
- [x] Overview - 系统概览
- [x] Projects - 项目管理
- [x] Workers - Worker 状态
- [x] Tasks - 任务管理
- [x] Reviews - 审批工作流
- [x] Ideas - 想法收集
- [x] APIs - API 连接管理
- [x] Routes - API 路由列表
- [x] Console - Planner 命令行
- [x] Souls - 角色人格配置
- [x] Settings - 系统设置

### 3. 向量化记忆系统
- [x] Per-Agent 记忆隔离 (planner, builder, researcher, verifier, documenter, evaluator)
- [x] 向量嵌入和语义搜索
- [x] 跨 Agent 搜索
- [x] API 端点:
  - `GET /api/memory/agents` - 列出所有 Agent
  - `GET /api/memory/{agent_id}` - 获取 Agent 记忆
  - `POST /api/memory/{agent_id}` - 添加记忆
  - `GET /api/memory/{agent_id}/search?q=...` - Agent 内搜索
  - `GET /api/memory/search?q=...` - 跨 Agent 搜索

### 4. AI Provider 集成
- [x] 9 个 AI Provider 支持
- [x] 实时模型列表获取 (需配置 API Key)
- [x] API Key 管理
- [x] 后端模型获取逻辑

**Providers:**
| Provider | 状态 |
|----------|------|
| OpenAI | ✅ 已配置 |
| Anthropic | ✅ 已配置 |
| DeepSeek | ✅ 已配置 |
| MiniMax | ✅ 已配置 |
| 阿里云 (Qwen) | ✅ 已配置 |
| 智谱AI | ✅ 已配置 |
| OpenRouter | ✅ 已配置 |
| GitHub Copilot | ✅ 已配置 |
| Brave Search | ✅ 已配置 |

### 5. 持久化存储
- [x] 文件-based 存储 (JSON)
- [x] Souls 配置持久化
- [x] Daily Memory 日志

---

## 🌐 部署状态

### 前端
- **URL**: https://sweuxhxuk356.space.minimaxi.com
- **状态**: ✅ 已部署 (CDN)
- **框架**: React + TypeScript + Vite
- **UI**: 莫兰蒂色系 (Morandi)

### 后端
- **URL**: http://localhost:8000
- **状态**: ❌ 本地运行，需部署到公网
- **框架**: FastAPI (Python)

---

## 🔧 本地开发

### 启动后端
```bash
cd /workspace/ai_founder_os
pip install fastapi uvicorn pydantic python-multipart
uvicorn src.api.server:app --host 0.0.0.0 --port 8000
```

### 启动前端
```bash
cd /workspace/ai_founder_os/frontend
npm install
npm run dev
```

### 构建前端
```bash
cd /workspace/ai_founder_os/frontend
npm run build
```

---

## 🚀 待完成工作

### 1. 后端部署 (高优先级)
需要将后端部署到公网，有以下选项：

**方案A: Railway (推荐)**
```bash
# 安装 Railway CLI
npm install -g @railway/cli
railway login
cd /workspace/ai_founder_os
railway init
railway deploy
```

**方案B: Render**
- 推送代码到 GitHub
- 在 render.com 创建 Python 服务

**方案C: 本地 + ngrok**
```bash
# 本地运行后端
uvicorn src.api.server:app --host 0.0.0.0 --port 8000

# 另一个终端运行 ngrok
ngrok http 8000

# 获取公网 URL 后更新前端 API_BASE
```

### 2. 前端配置 (部署后)
部署后端后，需要更新前端 API 配置：

文件: `/workspace/ai_founder_os/frontend/src/App.tsx`

将:
```typescript
const API_BASE = '';
```

改为:
```typescript
const API_BASE = 'https://你的后端URL';
```

### 3. 测试覆盖
- [ ] 添加更多单元测试
- [ ] 添加集成测试
- [ ] 添加 E2E 测试

### 4. 功能增强
- [ ] 添加更多 Worker 类型
- [ ] 完善 Planner 决策逻辑
- [ ] 添加更多 API Provider
- [ ] 实现完整的 Agent 协作工作流

---

## 📁 项目结构

```
ai_founder_os/
├── src/
│   ├── api/
│   │   ├── server.py      # FastAPI 主服务
│   │   └── ...
│   ├── planner/           # Planner 系统
│   ├── workers/          # Worker 系统
│   ├── policy/           # 策略引擎
│   ├── connections/       # 连接管理
│   ├── experience/       # 经验记录
│   ├── skills/           # 技能系统
│   ├── memory.py         # 向量记忆系统
│   ├── storage.py        # 持久化存储
│   └── api_keys.py       # API Key 管理
├── frontend/
│   ├── src/
│   │   ├── App.tsx      # Dashboard 主组件
│   │   └── ...
│   └── ...
├── docs/                 # 项目文档
├── memory/               # 记忆数据
│   └── vectors/          # 向量数据
│       ├── planner/
│       └── builder/
├── souls/                # 角色配置
├── data/                 # 运行时数据
├── tasks.json            # 任务列表
├── railway.json          # 部署配置
└── requirements.txt      # Python 依赖
```

---

## 🔑 API Key 配置

### 已保存的 Key (后端)
- DeepSeek: sk-cffc51be682c4f8f859610b9528d7d48
- 阿里云: sk-69db541c911f4219a05ecafa545f3048

### 保存新 Key
```bash
# 通过 API
curl -X POST "http://localhost:8000/api/keys/{provider}?key=YOUR_KEY"
```

支持的 provider: openai, anthropic, deepseek, minimax, alibaba, zhipu, github

---

## 📊 测试结果

- **单元测试**: 357+ tests passed
- **API 端点**: 20+ endpoints
- **Workers**: 6 个预配置 Worker

---

## 📝 注意事项

1. **前端无法连接后端**: 由于后端在本地，前端部署在 CDN，目前无法实时获取最新模型列表。需要部署后端到公网解决。

2. **API Key 安全**: 不要将 API Key 提交到 GitHub。已配置 `.gitignore`。

3. **记忆隔离**: 每个 Agent (planner, builder, researcher, verifier, documenter, evaluator) 有独立的记忆空间，互不干扰。

---

## 🔗 链接

- **GitHub**: https://github.com/nasonliu/ai_founder_os
- **前端**: https://sweuxhxuk356.space.minimaxi.com (CDN)
- **后端**: 本地运行中 (localhost:8000)

---

*最后更新: 2026-03-07*
