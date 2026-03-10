from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import Settings
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.vector_store import JsonVectorStore


@dataclass
class RetrievalChunk:
    """检索结果对象。

    教学意义：
    - 拆出 vector_score / lexical_score，能直观看到“语义召回”和“关键词重排”的贡献。
    """

    chunk_id: str
    document_id: str
    filename: str
    content: str
    score: float
    vector_score: float
    lexical_score: float


class RetrievalService:
    """向量召回 + 关键词重排。

    一个简化但完整的 RAG retrieval pipeline：
    1) 查询向量化；
    2) 与所有 chunk 向量做相似度；
    3) 叠加关键词重叠度做 rerank；
    4) 更新检索指标。
    """

    def __init__(
        self,
        settings: Settings,
        store: JsonVectorStore,
        embedding_service: EmbeddingService,
        metrics_path: Path,
    ):
        self.settings = settings
        self.store = store
        self.embedding_service = embedding_service
        self.metrics_path = metrics_path
        if not self.metrics_path.exists():
            self.metrics_path.write_text(
                json.dumps(
                    {
                        'documents_processed': 0,
                        'documents_failed': 0,
                        'chunks_indexed_total': 0,
                        'queries_total': 0,
                        'queries_with_hits': 0,
                        'average_top_score': 0.0,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding='utf-8',
            )

    async def index_document(self, document_id: str, filename: str, chunks: list[dict[str, str]]) -> int:
        """写入一个文档的全部 chunks 到向量存储。"""
        vectors = await self.embedding_service.embed_batch([c['content'] for c in chunks])
        rows: list[dict[str, Any]] = []
        for i, c in enumerate(chunks):
            rows.append(
                {
                    'chunk_id': f"{document_id}:{c['index']}",
                    'document_id': document_id,
                    'filename': filename,
                    'chunk_index': c['index'],
                    'content': c['content'],
                    'vector': vectors[i],
                }
            )
        n = self.store.upsert_document_chunks(document_id, rows)
        metrics = self._read_metrics()
        metrics['documents_processed'] = int(metrics.get('documents_processed', 0)) + 1
        metrics['chunks_indexed_total'] = int(metrics.get('chunks_indexed_total', 0)) + n
        self._write_metrics(metrics)
        return n

    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievalChunk]:
        """执行检索并返回 top-k。

        评分公式（可调）：
        score = 0.75 * vector_score + 0.25 * lexical_score
        """
        rows = self.store.read_all()
        if not rows:
            self._update_query_metrics(False, 0.0)
            return []
        q_vec = (await self.embedding_service.embed_batch([query]))[0]
        q_tokens = set(self._tokenize(query))
        scored: list[RetrievalChunk] = []
        for r in rows:
            v = r.get('vector', [])
            v_score = self._cosine(q_vec, v)
            if v_score <= 0:
                continue
            c_tokens = set(self._tokenize(r.get('content', '')))
            l_score = len(q_tokens & c_tokens) / max(1, len(q_tokens | c_tokens))
            score = 0.75 * v_score + 0.25 * l_score
            scored.append(
                RetrievalChunk(
                    chunk_id=r.get('chunk_id', ''),
                    document_id=r.get('document_id', ''),
                    filename=r.get('filename', 'unknown'),
                    content=r.get('content', ''),
                    score=score,
                    vector_score=v_score,
                    lexical_score=l_score,
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        out = scored[: (top_k or self.settings.rag_top_k)]
        self._update_query_metrics(bool(out), out[0].score if out else 0.0)
        return out

    def remove_document(self, document_id: str) -> None:
        self.store.remove_document(document_id)

    def mark_document_failed(self) -> None:
        m = self._read_metrics()
        m['documents_failed'] = int(m.get('documents_failed', 0)) + 1
        self._write_metrics(m)

    def metrics(self) -> dict[str, Any]:
        m = self._read_metrics()
        rows = self.store.read_all()
        return {
            **m,
            'indexed_chunks_current': len(rows),
            'indexed_documents_current': len({r.get('document_id') for r in rows}),
            'retrieval_top_k_default': self.settings.rag_top_k,
        }

    def _update_query_metrics(self, has_hit: bool, top_score: float) -> None:
        """在线更新平均 top 分，避免每次扫描历史查询。"""
        m = self._read_metrics()
        total = int(m.get('queries_total', 0)) + 1
        hits = int(m.get('queries_with_hits', 0)) + (1 if has_hit else 0)
        avg = float(m.get('average_top_score', 0.0))
        m['queries_total'] = total
        m['queries_with_hits'] = hits
        m['average_top_score'] = round(((avg * (total - 1)) + top_score) / total, 4)
        self._write_metrics(m)

    def _read_metrics(self) -> dict[str, Any]:
        try:
            data = json.loads(self.metrics_path.read_text(encoding='utf-8'))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _write_metrics(self, data: dict[str, Any]) -> None:
        self.metrics_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def _tokenize(self, text: str) -> list[str]:
        import re

        # 轻量分词：英文词 + 中文单字。准确度一般，但足够做教学演示。
        return re.findall(r'[a-z0-9_]+', text.lower()) + re.findall(r'[\u4e00-\u9fff]', text)

    def _cosine(self, a: list[float], b: list[float]) -> float:
        """余弦相似度（前提：向量已归一化时可退化为点积）。"""
        if not a or not b or len(a) != len(b):
            return 0.0
        return sum(x * y for x, y in zip(a, b))
