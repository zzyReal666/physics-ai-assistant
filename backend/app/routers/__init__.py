from fastapi import APIRouter

from . import auth, chat, documents, exam, health, rag, settings, teaching, tools


api_router = APIRouter()

# 健康检查
api_router.include_router(health.router)

# 认证（占位）
api_router.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# AI 答疑
api_router.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# AI 备课
api_router.include_router(teaching.router, prefix="/api/teaching", tags=["teaching"])

# 文档管理
api_router.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# 模型配置
api_router.include_router(settings.router, prefix="/api/settings", tags=["settings"])

# AI 出卷
api_router.include_router(exam.router, prefix="/api/exam", tags=["exam"])

# RAG 调试
api_router.include_router(rag.router, prefix="/api/rag", tags=["rag"])

# 工具（占位）
api_router.include_router(tools.router, prefix="/api/tools", tags=["tools"])


__all__ = ["api_router"]
