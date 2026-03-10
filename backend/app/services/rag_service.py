from __future__ import annotations

"""兼容层：对外保持 RagService 名称，同时内部使用 services/rag 子模块实现。

这样做的目的：
1) 对齐详细设计目录结构；
2) 兼容现有依赖注入与路由，不一次性破坏大量调用点。
"""

from pathlib import Path
from typing import Any

from app.config import Settings
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.retrieval_service import RetrievalChunk, RetrievalService
from app.services.rag.vector_store import JsonVectorStore


class RagService:
    def __init__(self, settings: Settings):
        self.settings = settings
        root = Path(settings.data_dir)
        root.mkdir(parents=True, exist_ok=True)

        store = JsonVectorStore(root / 'rag_chunks.json')
        embedding = EmbeddingService(settings, root / 'model_config.json')
        self._retrieval = RetrievalService(
            settings=settings,
            store=store,
            embedding_service=embedding,
            metrics_path=root / 'rag_metrics.json',
        )

    async def index_document(
        self,
        document_id: str,
        filename: str,
        chunks: list[dict[str, str]],
    ) -> int:
        return await self._retrieval.index_document(document_id, filename, chunks)

    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievalChunk]:
        return await self._retrieval.retrieve(query, top_k)

    async def remove_document(self, document_id: str) -> None:
        self._retrieval.remove_document(document_id)

    async def mark_document_failed(self) -> None:
        self._retrieval.mark_document_failed()

    async def get_metrics(self) -> dict[str, Any]:
        return self._retrieval.metrics()
