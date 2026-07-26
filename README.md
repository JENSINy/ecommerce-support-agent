# 电商售后 Agent 工作台

一个面向电商售后场景的智能客服工作台。

用户可以通过自然语言查询订单、物流和商品 FAQ，也可以提交退货或退款申请。退款等敏感操作不会由 Agent 直接执行，而是进入人工审批流程。

项目采用 FastAPI + React + OpenAI Agents SDK + DeepSeek API，并使用 SQLite 保存业务数据、会话记录和工具调用日志。

---

## 项目功能

### Agent 能力

- 查询订单信息
- 查询订单物流
- 查询商品常见问题
- 创建退货申请
- 创建退款申请
- 支持多轮会话
- 根据上下文继续补充订单号、金额或申请原因

### 人工审核

- 退货申请由人工审核通过或拒绝
- 退款申请由人工批准或拒绝
- Agent 只能创建待审批退款申请
- Agent 无权直接执行退款
- 人工批准退款后，后端模拟执行退款并更新订单状态

### 日志与数据

- SQLite 保存订单、物流、FAQ 和售后申请
- 保存用户与 Agent 的聊天记录
- 保存 Agent 工具调用日志
- 保存人工退款和退货审核日志
- 日志包含调用原因、输入参数、执行结果、耗时和异常信息
- 支持通过 `session_id` 恢复历史会话

---

## 技术栈

| 类型 | 技术 |
| --- | --- |
| 前端 | React、Vite |
| 后端 | FastAPI |
| Agent 框架 | OpenAI Agents SDK |
| 大模型 | DeepSeek API |
| 数据库 | SQLite |
| ORM | SQLAlchemy 2.0 |
| 后端测试 | pytest、FastAPI TestClient |
| Python 代码检查 | Ruff |
| 前端代码检查 | Oxlint |

---

## 项目结构

```text
ecommerce-support-agent/
├── backend/
│   ├── agent/
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── faq.py
│   │   │   ├── logistics.py
│   │   │   ├── orders.py
│   │   │   ├── refunds.py
│   │   │   └── returns.py
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── context.py
│   │   ├── logging.py
│   │   ├── prompts.py
│   │   └── service.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── conversations.py
│   │   ├── orders.py
│   │   ├── refunds.py
│   │   ├── returns.py
│   │   └── tool_logs.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── conversation_service.py
│   │   ├── order_service.py
│   │   ├── refund_service.py
│   │   ├── return_service.py
│   │   └── tool_log_service.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_conversations.py
│   │   ├── test_orders.py
│   │   ├── test_refunds.py
│   │   └── test_returns.py
│   │
│   ├── agent_service.py
│   ├── database.py
│   ├── dependencies.py
│   ├── init_db.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── statuses.py
│   └── pyproject.toml
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── chatApi.js
│   │   │   ├── client.js
│   │   │   ├── refundApi.js
│   │   │   ├── returnApi.js
│   │   │   └── toolLogApi.js
│   │   │
│   │   ├── components/
│   │   │   ├── approvals/
│   │   │   ├── chat/
│   │   │   ├── common/
│   │   │   └── logs/
│   │   │
│   │   ├── hooks/
│   │   │   ├── useConversation.js
│   │   │   ├── useRefundRequests.js
│   │   │   └── useReturnRequests.js
│   │   │
│   │   ├── styles/
│   │   │   ├── approvals.css
│   │   │   ├── chat.css
│   │   │   ├── global.css
│   │   │   ├── layout.css
│   │   │   ├── logs.css
│   │   │   ├── responsive.css
│   │   │   └── tokens.css
│   │   │
│   │   ├── utils/
│   │   │   ├── formatters.js
│   │   │   └── status.js
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── .gitignore
└── README.md
```

## 后端结构说明

后端按照职责拆分，避免路由、业务逻辑、数据库和 Agent 代码混在一起。

### Router

`routers/` 负责：

- 接收 HTTP 请求
- 获取参数
- 调用 Service
- 返回响应

### Service

`services/` 负责：

- 查询退款、退货申请
- 修改申请和订单状态
- 创建人工审批日志
- 控制数据库事务

### Model / Schema / Status

- `models.py`：定义 SQLAlchemy 数据模型
- `schemas.py`：定义 API 请求和响应结构
- `statuses.py`：集中管理业务状态

主要状态：

```text
退款：pending_approval / approved / rejected
退货：pending_review / approved / rejected
订单：refunded
日志：success / failed / not_found
```

---

## Agent 结构

Agent 代码位于：

```text
backend/agent/
```

主要结构：

```text
agent/
├── tools/
├── client.py
├── context.py
├── logging.py
├── prompts.py
└── service.py
```

主要职责：

- `client.py`：创建 DeepSeek 客户端
- `context.py`：保存会话上下文
- `prompts.py`：保存 Agent 提示词
- `service.py`：创建客服 Agent
- `logging.py`：保存工具调用日志
- `tools/`：订单、物流、FAQ、退款、退货工具

### Agent 工具

| 工具 | 功能 |
| --- | --- |
| `get_order` | 查询订单 |
| `get_logistics` | 查询物流 |
| `search_faq` | 查询 FAQ |
| `create_return_request` | 创建退货申请 |
| `request_refund` | 创建退款申请 |

Agent 只能创建退款申请，不能直接执行退款。

---

## 核心业务流程

### 普通查询

```text
用户
 ↓
Agent
 ↓
Tool
 ↓
Database
 ↓
返回结果
```

### 退货

```text
用户申请退货
 ↓
Agent 创建 pending_review 申请
 ↓
人工批准 / 拒绝
```

### 退款

```text
用户申请退款
 ↓
Agent 创建 pending_approval 申请
 ↓
人工批准 / 拒绝
 ↓
批准后订单状态变为 refunded
```

退款申请、订单状态和审批日志在同一个数据库事务中提交，失败时统一回滚。

---

## 前端结构说明

前端按照：

```text
Component
 ↓
Hook
 ↓
API
 ↓
FastAPI
```

进行拆分。

目录：

```text
src/
├── api/
├── components/
├── hooks/
├── styles/
├── utils/
├── App.jsx
└── main.jsx
```

- `api/`：后端接口请求
- `components/`：页面组件
- `hooks/`：聊天、退款、退货状态逻辑
- `styles/`：按模块拆分 CSS
- `utils/`：时间、状态等工具函数

---

## 数据表

| 数据表 | 用途 |
| --- | --- |
| `orders` | 订单数据 |
| `logistics` | 物流信息 |
| `faqs` | FAQ 知识库 |
| `conversations` | 会话信息 |
| `messages` | 聊天消息 |
| `tool_logs` | 工具调用和审批日志 |
| `refund_requests` | 退款申请 |
| `return_requests` | 退货申请 |

---

## 本地运行

### 后端

```bash
cd backend
python -m pip install fastapi uvicorn sqlalchemy openai-agents openai python-dotenv pytest httpx ruff
python init_db.py
python -m uvicorn main:app --reload
```

配置文件：

```text
backend/.env
```

示例：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：

```text
http://localhost:5173
```

---

## 主要 API

```text
POST /chat

GET  /conversations/{session_id}/messages
GET  /orders/{order_id}
GET  /tool-logs

GET  /refund-requests
POST /refund-requests/{id}/approve
POST /refund-requests/{id}/reject

GET  /return-requests
POST /return-requests/{id}/approve
POST /return-requests/{id}/reject
```

---

## 示例

查询订单：

```text
帮我查询订单 ORD001
```

查询物流：

```text
帮我查询 ORD001 的物流
```

创建退款申请：

```text
我要申请退款，订单号 ORD002，
退款金额 129 元，
原因是商品无法正常使用。
```

创建退货申请：

```text
我要退货，订单号 ORD003，
原因是商品不合适。
```

---

## 测试与代码检查

### 后端

```bash
python -m ruff format .
python -m ruff check .
python -m pytest
```

### 前端

```bash
npm run lint
npm run build
```

---

## 数据库说明

开发数据库：

```text
backend/ecommerce.db
```

如果修改了数据库模型，`create_all()` 不会自动修改旧表。

开发阶段可以备份后重新初始化：

```powershell
Copy-Item ecommerce.db ecommerce_backup.db
Remove-Item ecommerce.db
python init_db.py
```

生产环境建议使用 Alembic 管理数据库迁移。

---

## 安全设计

- DeepSeek API Key 保存在 `.env`
- `.env` 和本地数据库不提交到 Git
- Agent 不能直接执行退款
- 退款必须经过人工审批
- 退货需要人工审核
- Agent 工具调用和人工审批都会记录日志

---

## 项目设计

后端：

```text
Router
 ↓
Service
 ↓
Model
 ↓
SQLite
```

Agent：

```text
Chat
 ↓
Agent
 ↓
Tool
 ↓
Database
```

前端：

```text
Component
 ↓
Hook
 ↓
API
 ↓
FastAPI
```

---

## 后续优化

- PostgreSQL
- Alembic
- pgvector FAQ 检索
- 用户登录和权限控制
- 接入真实订单、物流和退款平台
- Docker
- CI/CD
- 更多自动化测试
