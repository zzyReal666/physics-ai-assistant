## AI物理教学助手（Physics AI Assistant）

本仓库已按文档实现一个可本地运行的 MVP，包含：

- 后端：FastAPI（文档管理、AI答疑、AI备课、模型配置）
- 前端：React + TypeScript + Vite + Ant Design（仪表盘、文档管理、备课助手、答疑、模型配置）

## 目录结构

```text
physics-ai-assistant/
├── docs/                  # 需求/架构/详细设计文档
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   ├── teaching.py
│   │   │   └── settings.py
│   │   ├── services/
│   │   │   ├── document_store.py
│   │   │   └── model_config_store.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 一、启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：

- 健康检查：[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Swagger：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 二、启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：[http://127.0.0.1:5173](http://127.0.0.1:5173)

Vite 已配置代理：`/api -> http://127.0.0.1:8000`。

## 三、已实现接口

- `GET /health`
- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/{document_id}`
- `POST /api/chat/ask`
- `POST /api/teaching/create-plan`
- `GET /api/settings/model`
- `PUT /api/settings/model`

## 四、模型配置说明

后端支持 `DeepSeek/OpenAI/智谱` 三类配置：

- `.env` 中配置 API Key 与 Base URL
- 前端“模型配置”页面可更新当前默认模型（落盘于 `backend/data/model_config.json`）

若未配置任何 API Key，答疑与备课接口会返回内置示例结果，便于本地联调。
