from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_rag_service
from app.models import RagRetrieveChunk, RagRetrieveRequest
from app.services.rag_service import RagService


router = APIRouter()


@router.get("/metrics", summary="RAG 指标")
async def get_rag_metrics(
    rag_service: RagService = Depends(get_rag_service),
) -> dict:
    """查看 RAG 运行指标，便于学习和排查效果。"""
    return await rag_service.get_metrics()


@router.post("/retrieve", response_model=list[RagRetrieveChunk], summary="RAG 检索调试")
async def retrieve_debug(
    req: RagRetrieveRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> list[RagRetrieveChunk]:
    """不走 LLM，只做检索，帮助你观察召回效果。"""
    chunks = await rag_service.retrieve(req.query, top_k=req.top_k)
    return [RagRetrieveChunk(**c.__dict__) for c in chunks]
