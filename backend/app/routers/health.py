from fastapi import APIRouter

router = APIRouter()


@router.get("/health", summary="健康检查")
async def health_check() -> dict:
    return {"status": "ok"}


