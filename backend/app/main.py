from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import api_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Physics AI Assistant Backend",
        description="AI 物理教学助手 - 后端服务（MVP 简化版）",
        version="0.1.0",
    )

    # CORS（方便前端本地调试）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 挂载统一路由
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        return {
            "message": "Physics AI Assistant Backend is running.",
            "env": settings.app_env,
        }

    return app


app = create_app()


