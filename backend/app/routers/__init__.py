from fastapi import APIRouter

from . import health, chat, teaching, documents, settings


api_router = APIRouter()

# 健康检查
api_router.include_router(health.router)

# AI 答疑
api_router.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# AI 备课
api_router.include_router(teaching.router, prefix="/api/teaching", tags=["teaching"])

# 文档管理
api_router.include_router(documents.router, prefix="/api/documents", tags=["documents"])

# 模型配置
api_router.include_router(settings.router, prefix="/api/settings", tags=["settings"])


__all__ = ["api_router"]
