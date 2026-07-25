# 电商售后 Agent 工作台

一个面向电商售后场景的智能客服工作台。用户可通过自然语言查询订单、物流、商品 FAQ，并提交退货或退款申请；退款等敏感操作必须经过人工审批后才会执行。

## 项目功能

### Agent 能力

- 查询订单信息
- 查询订单物流
- 查询商品常见问题
- 创建退货申请
- 创建退款申请
- 支持多轮会话：用户先说明需求，后续补充订单号、金额或原因后可继续处理

### 人工审核

- 退货申请由人工审核通过或拒绝
- 退款申请由人工批准或拒绝
- Agent 只能创建待审批退款申请，不能直接执行退款
- 人工批准退款后，系统模拟执行退款并更新订单状态

### 日志与数据

- SQLite 持久化保存订单、物流、FAQ、聊天消息和售后申请
- 保存 Agent 工具调用日志
- 日志包含工具名称、调用原因、输入参数、执行结果、耗时和失败信息
- 通过 `session_id` 恢复历史会话记录
- 保存人工审批操作日志，便于审计与排查问题

## 技术栈

| 类型 | 技术 |
| --- | --- |
| 前端 | React、Vite |
| 后端 | FastAPI |
| Agent 框架 | OpenAI Agents SDK |
| 大模型 | DeepSeek API |
| 数据库 | SQLite |
| ORM | SQLAlchemy 2.0 |
| 测试 | pytest、FastAPI TestClient |

## 项目结构

```text
ecommerce-support-agent/
├── backend/
│   ├── agent_service.py
│   ├── database.py
│   ├── init_db.py
│   ├── main.py
│   ├── migrate_return_requests.py
│   ├── models.py
│   ├── test_api.py
│   ├── ecommerce.db
│   ├── .env
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── .env
│   └── package.json
└── README.md


核心工具
工具	功能
get_order(order_id)	查询订单商品、金额和订单状态
get_logistics(order_id)	查询快递公司、运单号和物流进度
search_faq(question)	查询商品参数、兼容性、保修与退换货规则
create_return_request(order_id, reason)	创建待人工审核的退货申请
request_refund(order_id, amount, reason)	创建待人工审批的退款申请
issue_refund(order_id, amount)	仅在人工批准后由后端模拟执行退款


核心业务流程
订单、物流与 FAQ 查询
用户输入自然语言
-> Agent 识别用户意图
-> 调用订单、物流或 FAQ 工具
-> 查询 SQLite 数据库
-> 整理为自然语言回复
-> 保存工具调用日志

退货审核
用户申请退货
-> Agent 收集订单号和退货原因
-> 创建 pending_review 状态的退货申请
-> 前端退货审核中心展示申请
-> 人工批准或拒绝
-> 保存人工审核日志

退款人工审批
用户申请退款
-> Agent 收集订单号、退款金额和退款原因
-> Agent 创建 pending_approval 状态的退款申请
-> 前端退款审批中心展示申请
-> 人工点击“批准退款”
-> 后端模拟执行 issue_refund
-> 订单状态更新为 refunded
-> 保存人工审批操作日志

数据表
数据表	用途
orders	模拟订单数据
logistics	模拟物流数据
faqs	商品常见问题知识库
conversations	会话记录
messages	用户与 Agent 的聊天消息
tool_logs	Agent 工具调用和人工审核日志
return_requests	退货申请记录
refund_requests	退款申请记录

本地运行
1. 后端配置

进入后端目录：

cd backend


安装 Python 依赖：

python -m pip install fastapi uvicorn sqlalchemy openai-agents openai python-dotenv pytest httpx


创建 backend/.env 文件：

DEEPSEEK_API_KEY=你的DeepSeek_API_Key


初始化数据库和模拟数据：

python init_db.py


如果已创建过 return_requests 表，运行迁移脚本：

python migrate_return_requests.py


启动后端：

python -m uvicorn main:app --reload


打开后端 API 文档：

http://127.0.0.1:8000/docs

2. 前端配置

打开新的终端，进入前端目录：

cd frontend


安装依赖：

npm.cmd install


创建 frontend/.env 文件：

VITE_API_BASE_URL=http://127.0.0.1:8000


启动前端：

npm.cmd run dev


浏览器打开：

http://localhost:5173

演示测试用例
查询订单
查询订单 ORD004


预期：Agent 调用 get_order，返回订单状态 paid。

查询物流
查询 ORD002 的物流


预期：Agent 调用 get_logistics，返回中通快递和“已揽收”状态。

查询 FAQ
蓝牙静音鼠标怎么充电？


预期：Agent 调用 search_faq，回答 Type-C 充电和续航信息。

创建退货申请
我要退货，订单号 ORD003，原因是不想要了。


预期：Agent 调用 create_return_request，前端退货审核中心出现待审核记录。

创建退款申请
我要申请退款，不是退货。订单号 ORD002，退款金额 129 元，原因是鼠标无法使用。


预期：Agent 调用 request_refund，前端退款审批中心出现待审批记录。

自动化测试

在 backend 目录运行：

python -m pytest -q


测试使用独立的 ecommerce_test.db，不会影响演示数据库 ecommerce.db。

当前测试覆盖：

存在订单查询

不存在订单查询

工具日志接口

人工批准退款后订单状态更新

人工批准退货后申请状态更新

拒绝退货时审核原因必填校验

安全设计

DEEPSEEK_API_KEY 仅保存于后端 .env 文件，不提交到 Git。

Agent 不具备直接退款权限。

Agent 只能创建 pending_approval 状态的退款申请。

只有人工在审批中心点击“批准退款”后，后端才执行模拟退款。

Agent 工具调用和人工审批操作均保存到 tool_logs，支持审计和问题追踪。

后续优化

使用 PostgreSQL 替换 SQLite

使用 pgvector 实现 FAQ 向量检索

增加用户登录、身份认证和管理员权限控制

增加订单取消等敏感操作的审批机制

接入真实订单、物流与支付平台

使用 Docker 完成容器化部署

增加更多自动化测试与接口异常场景测试