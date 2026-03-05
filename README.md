## AI物理教学助手（Physics AI Assistant）

本仓库目前只有需求/设计文档（在 `docs/`），下面补充了一套**可直接运行的最小可用代码**，包含：

- **后端**：FastAPI + Python（简单版 RAG/LLM 调用接口，部分功能做成占位实现，方便后续扩展）
- **环境配置**：`backend/requirements.txt`、`.env.example`、启动命令

> 说明：为了让你尽快“跑起来”，这里实现的是 **MVP 级后端**，功能范围覆盖文档中的核心流程接口形式，但内部很多复杂逻辑（真正的向量库、Agent、多模型切换等）用简化实现或占位实现代替，你可以在此基础上按详细设计文档继续迭代。

---

### 1. 目录结构（当前代码）

```text
physics-ai-assistant/
├── docs/                    # 需求/设计文档（你已有）
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 入口，挂载路由
│   │   ├── config.py        # 配置 & 环境变量
│   │   ├── dependencies.py  # 依赖注入（配置、LLM 客户端）
│   │   └── routers/
│   │       ├── __init__.py
│   │       ├── health.py    # 健康检查
│   │       ├── chat.py      # AI 答疑（简化版）
│   │       └── teaching.py  # AI 备课（简化版）
│   ├── requirements.txt     # 后端依赖
│   └── .env.example         # 环境变量示例
└── README.md
```

---

### 2. 本地运行步骤（推荐）

在项目根目录 `physics-ai-assistant/` 下：

#### 2.1 创建并激活虚拟环境

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

#### 2.2 安装依赖

```bash
pip install -r requirements.txt
```

> 说明：`requirements.txt` 已尽量选用轻量依赖，暂不强制安装 sentence-transformers / 向量数据库 等重依赖，后续你可以根据需要自行补充。

#### 2.3 配置环境变量

```bash
cp .env.example .env
```

编辑 `backend/.env`，如果你暂时没有任何大模型 API Key，可以先 **不改**，系统会使用内置的“假回答”，方便你验证接口通路；  
如果你有 DeepSeek / OpenAI 等 Key，可以在 `.env` 中设置：

```env
DEEPSEEK_API_KEY=你的key
OPENAI_API_KEY=你的key
DEFAULT_LLM_MODEL=deepseek-chat  # 或 gpt-4.1 等
```

#### 2.4 启动后端服务

```bash
cd backend
source .venv/bin/activate  # 如未激活
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后访问：

- **交互式接口文档**：`http://127.0.0.1:8000/docs`
- **健康检查**：`GET http://127.0.0.1:8000/health`

---

### 3. 已提供的核心接口（MVP）

当前后端实现了以下简化接口，用于对应详细设计文档中的核心业务流（但内部逻辑为简化/占位实现）：

- **健康检查**
  - `GET /health`：检查服务是否正常运行。

- **AI 答疑助手（简化版）**
  - `POST /api/chat/ask`
  - 请求体示例：
    ```json
    {
      "question": "一个质量为2kg的物体在水平面上受到10N拉力，摩擦系数0.2，求加速度？",
      "student_level": "senior"
    }
    ```
  - 如未配置真实 LLM Key，会返回**规则引擎+模板**生成的“示例回答”；  
    如配置了 LLM Key，则会调用真实大模型，并附带一个简单的系统 Prompt，指导模型按“物理解题步骤”回答。

- **AI 备课助手（简化版）**
  - `POST /api/teaching/create-plan`
  - 请求体示例：
    ```json
    {
      "topic": "牛顿第二定律",
      "class_info": "高二重点班，45分钟",
      "requirements": "需要实验演示和3道典型例题"
    }
    ```
  - 未配置 LLM 时：返回硬编码的“牛顿第二定律”示例教案；  
    配置 LLM 后：通过 LLM 生成结构化教案文本。

---

### 4. 下一步建议（按详细设计继续扩展）

- 在 `backend/app/routers/documents.py` 中补充：
  - 文档上传、异步解析、入库（可以先用本地 SQLite + SQLAlchemy）。
- 在 `backend/app/services/` 下逐步实现：
  - 文档解析、文本分块、Embedding、向量检索（可用 Chroma / LanceDB / Qdrant）。
- 搭建 `frontend/`（React + TS + Ant Design），把原型文档中的页面一步步落地。

如你希望，我也可以在下一步帮你把前端 `frontend/` 的 Vite+React+TS 脚手架和基础页面也一起补齐。

