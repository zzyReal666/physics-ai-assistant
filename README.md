# Physics AI Assistant

> AI 物理教学助手（教学型 RAG 项目）

本项目用于学习和实践 **RAG + LLM 应用开发**，并已按 `docs/04-detailed-design.md` 的项目分层进行重构。

## Features

- 文档管理：上传、详情、删除、重建索引
- 多格式解析：`txt/md/pdf/pptx/docx/image`
- RAG 检索：向量召回 + 关键词重排 + 调试接口
- AI 助手：答疑、备课、出卷
- 模型配置：页面直接配置模型 / Key / Base URL

## Project Structure

```text
physics-ai-assistant/
├── docs/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── models/
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   ├── teaching.py
│   │   │   ├── exam.py
│   │   │   ├── settings.py
│   │   │   └── rag.py
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── chat.py
│   │   │   ├── teaching.py
│   │   │   ├── exam.py
│   │   │   ├── settings.py
│   │   │   ├── rag.py
│   │   │   └── tools.py
│   │   ├── services/
│   │   │   ├── database.py
│   │   │   ├── auth_service.py
│   │   │   ├── file_service.py
│   │   │   ├── exam_service.py
│   │   │   ├── document_store.py
│   │   │   ├── exam_store.py
│   │   │   ├── model_config_store.py
│   │   │   ├── rag_service.py
│   │   │   ├── rag/
│   │   │   │   ├── document_loader.py
│   │   │   │   ├── text_splitter.py
│   │   │   │   ├── embedding_service.py
│   │   │   │   ├── vector_store.py
│   │   │   │   └── retrieval_service.py
│   │   │   ├── llm/
│   │   │   │   └── client.py
│   │   │   └── agent/
│   │   │       ├── teaching_agent.py
│   │   │       ├── qa_agent.py
│   │   │       ├── exam_agent.py
│   │   │       └── tools/
│   │   │           ├── chart_tool.py
│   │   │           ├── latex_tool.py
│   │   │           ├── video_tool.py
│   │   │           └── calculator_tool.py
│   │   └── utils/
│   │       ├── helpers.py
│   │       ├── latex_utils.py
│   │       └── ocr_utils.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   ├── common/
│   │   │   ├── documents/
│   │   │   ├── teaching/
│   │   │   ├── chat/
│   │   │   └── exam/
│   │   ├── pages/
│   │   ├── services/api/
│   │   ├── stores/
│   │   ├── hooks/
│   │   └── utils/
│   └── package.json
└── README.md
```

## Quick Start

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2) Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## API Overview

- `GET /health`
- `POST /api/documents/upload`
- `POST /api/documents/{document_id}/reprocess`
- `GET /api/documents`
- `GET /api/documents/{document_id}`
- `DELETE /api/documents/{document_id}`
- `POST /api/chat/ask`
- `POST /api/teaching/create-plan`
- `POST /api/exam/generate`
- `GET /api/exam/{exam_id}/download?format=latex`
- `GET /api/settings/model`
- `PUT /api/settings/model`
- `POST /api/rag/retrieve`
- `GET /api/rag/metrics`

## RAG Learning Path

建议按下面顺序阅读代码（从“上传文档”到“回答生成”）：

1. `backend/app/routers/documents.py`
2. `backend/app/services/document_store.py`
3. `backend/app/services/rag/document_loader.py`
4. `backend/app/services/rag/text_splitter.py`
5. `backend/app/services/rag/embedding_service.py`
6. `backend/app/services/rag/vector_store.py`
7. `backend/app/services/rag/retrieval_service.py`
8. `backend/app/routers/chat.py`

### Key Concepts (速查)

- `Chunk`：文档切片，RAG 检索的最小单位。
- `Embedding`：把文本映射到向量空间，用于语义相似度检索。
- `Vector Recall`：按向量相似度找候选片段。
- `Rerank`：对候选片段再排序（本项目用关键词重排演示）。
- `Top-K`：最终返回给 LLM 的片段数量，影响准确率和成本。
- `Fallback`：当远端模型不可用时的降级策略，保证服务可用性。

## Notes

- 图片 OCR 依赖 `pytesseract`，还需要系统安装 `tesseract` 可执行程序。
- 当前 `auth/tools/agent` 部分是教学占位模块，用于结构对齐与后续扩展。
