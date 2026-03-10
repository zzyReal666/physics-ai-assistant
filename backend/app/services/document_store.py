from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

import aiofiles
from app.services.rag.document_loader import DocumentLoader
from app.services.rag.text_splitter import PhysicsTextSplitter

if TYPE_CHECKING:
    from .rag_service import RagService


ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "png", "jpg", "jpeg", "txt", "md"}


@dataclass
class UploadResult:
    """上传接口的返回结构。"""

    document_id: str
    filename: str
    status: str
    message: str


class DocumentStore:
    """文档存储与解析服务。

    学习重点：
    1) 这里负责“文件和元数据”生命周期；
    2) RAG 向量索引交给 RagService；
    3) 两者分离后，更容易替换实现（比如换 PostgreSQL、换对象存储）。
    """

    def __init__(self, data_dir: str):
        # 统一把所有“文档原始文件 + 元数据”放到 data_dir 下，
        # 便于后续迁移到数据库/对象存储时做适配层替换。
        root = Path(data_dir)
        self._uploads_dir = root / "uploads"
        self._metadata_file = root / "metadata.json"
        self._uploads_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self._loader = DocumentLoader()
        self._splitter = PhysicsTextSplitter(max_chars=350)
        if not self._metadata_file.exists():
            self._metadata_file.write_text("[]", encoding="utf-8")

    async def upload(self, filename: str, content: bytes) -> UploadResult:
        """保存原始文件并写入初始元数据。

        关键点：
        1) 只做“快路径”工作（落盘 + 记录），确保上传接口响应快；
        2) 真正耗时的解析/建索引放在后台任务 process_document 中。
        """
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("不支持的文件类型")

        document_id = str(uuid.uuid4())
        safe_name = self._safe_filename(filename)
        final_name = f"{document_id}_{safe_name}"
        file_path = self._uploads_dir / final_name

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        doc = {
            "id": document_id,
            "filename": filename,
            "stored_filename": final_name,
            "file_type": ext,
            "file_size": len(content),
            # 初始状态为 uploaded，后续由后台任务做真正解析和建索引。
            "status": "uploaded",
            "retry_count": 0,
            "last_error": None,
            "chunk_count": 0,
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        await self._append_metadata(doc)
        return UploadResult(
            document_id=document_id,
            filename=filename,
            status="uploaded",
            message="文件上传成功，已进入后台解析队列",
        )

    async def list_documents(self) -> list[dict[str, Any]]:
        """返回文档列表（按时间倒序）。"""
        docs = await self._read_metadata()
        return sorted(docs, key=lambda d: d.get("created_at", ""), reverse=True)

    async def get_document(self, document_id: str) -> dict[str, Any] | None:
        doc = await self.get_document_meta(document_id)
        if not doc:
            return None
        # 这里直接实时读取分块，便于你观察解析结果（教学友好）。
        chunks = await self._build_chunks(doc)
        return {**doc, "chunks": chunks, "chunk_count": len(chunks)}

    async def get_document_meta(self, document_id: str) -> dict[str, Any] | None:
        docs = await self._read_metadata()
        for doc in docs:
            if doc["id"] == document_id:
                return doc
        return None

    async def process_document(
        self, document_id: str, rag_service: "RagService", max_retries: int = 2
    ) -> None:
        """后台任务入口：解析文档 -> 分块 -> 建索引，并带重试机制。"""
        for attempt in range(max_retries + 1):
            try:
                await self._update_document_fields(
                    document_id,
                    status="processing",
                    retry_count=attempt,
                    last_error=None,
                )
                doc = await self.get_document_meta(document_id)
                if not doc:
                    return
                chunks = await self._build_chunks(doc, max_chunks=200)
                # 这里将“可解释的文本分块”交给 RAG 服务建索引。
                await rag_service.index_document(
                    document_id=document_id,
                    filename=doc["filename"],
                    chunks=chunks,
                )
                await self._update_document_fields(
                    document_id,
                    status="processed",
                    chunk_count=len(chunks),
                    processed_at=datetime.utcnow().isoformat() + "Z",
                    last_error=None,
                )
                return
            except Exception as err:
                # 解析类任务常见临时失败（如依赖加载、瞬时 IO），
                # 这里采用指数前缀的简化回退等待做重试。
                if attempt >= max_retries:
                    await self._update_document_fields(
                        document_id,
                        status="failed",
                        last_error=str(err),
                    )
                    await rag_service.mark_document_failed()
                    return
                await asyncio.sleep(0.2 * (attempt + 1))

    async def delete_document(self, document_id: str) -> bool:
        """删除文档元数据和原始文件。"""
        docs = await self._read_metadata()
        target: dict[str, Any] | None = None
        kept: list[dict[str, Any]] = []
        for doc in docs:
            if doc.get("id") == document_id and target is None:
                target = doc
            else:
                kept.append(doc)

        if not target:
            return False

        file_path = self._uploads_dir / target["stored_filename"]
        if file_path.exists():
            file_path.unlink()

        async with aiofiles.open(self._metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(kept, ensure_ascii=False, indent=2))
        return True

    async def _update_document_fields(self, document_id: str, **fields: Any) -> None:
        """局部更新单条文档元数据字段。"""
        docs = await self._read_metadata()
        changed = False
        for doc in docs:
            if doc.get("id") == document_id:
                doc.update(fields)
                changed = True
                break
        if changed:
            async with aiofiles.open(self._metadata_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(docs, ensure_ascii=False, indent=2))

    async def retrieve_chunks(self, query: str, top_k: int = 3) -> list[dict[str, str]]:
        """遗留关键词检索方法（兼容老调用）。

        新链路建议直接走 RagService.retrieve（向量+重排）。
        """
        words = [w for w in re.split(r"\W+", query.lower()) if len(w) >= 2]
        docs = await self.list_documents()
        ranked: list[tuple[int, dict[str, str]]] = []

        for doc in docs[:10]:
            chunks = await self._build_chunks(doc, max_chunks=4)
            for chunk in chunks:
                content = chunk["content"].lower()
                score = sum(1 for w in words if w in content)
                if score > 0:
                    ranked.append(
                        (
                            score,
                            {
                                "document_id": doc["id"],
                                "filename": doc["filename"],
                                "content": chunk["content"],
                            },
                        )
                    )
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in ranked[:top_k]]

    async def _build_chunks(
        self, doc: dict[str, Any], max_chunks: int = 8
    ) -> list[dict[str, str]]:
        """从单个文档构建切片。

        说明：
        - 这里把“文档解析”和“分块策略”拆到独立服务里（loader/splitter），
          便于你分别替换和测试。
        - max_chunks 是安全阈值，避免极端大文档一次构建太多分块。
        """
        file_path = self._uploads_dir / doc["stored_filename"]
        ext = doc.get("file_type", "")
        if ext in {"txt", "md", "pdf", "pptx", "docx", "png", "jpg", "jpeg"} and file_path.exists():
            content = await self._extract_text(file_path, ext)
            if not content.strip():
                return [
                    {
                        "index": "1",
                        "content": (
                            f"文件《{doc['filename']}》已上传，但当前未提取到有效文本。"
                            "请确认文档是否为扫描版图片，后续可接入 OCR。"
                        ),
                    }
                ]
            parts = self._splitter.split(content, max_chunks=max_chunks)
            return [
                {"index": p["index"], "content": p["content"]}
                for p in parts
                if p["content"].strip()
            ]

        return [
            {
                "index": "1",
                "content": (
                    f"文件《{doc['filename']}》已上传。当前仅支持 txt/md/pdf/pptx/docx/image 文本切片；"
                    "其他格式已记录元数据，可在后续迭代中接入OCR和结构化解析。"
                ),
            }
        ]

    async def _read_metadata(self) -> list[dict[str, Any]]:
        """读取 metadata.json，损坏时返回空列表。"""
        async with aiofiles.open(self._metadata_file, "r", encoding="utf-8") as f:
            raw = await f.read()
        try:
            data = json.loads(raw or "[]")
        except json.JSONDecodeError:
            data = []
        return data if isinstance(data, list) else []

    async def _append_metadata(self, doc: dict[str, Any]) -> None:
        """追加一条文档元数据记录。"""
        docs = await self._read_metadata()
        docs.append(doc)
        async with aiofiles.open(self._metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(docs, ensure_ascii=False, indent=2))

    async def _read_text_file(self, path: Path) -> str:
        """读取纯文本文件（目前仅保留给教学演示）。"""
        async with aiofiles.open(path, "r", encoding="utf-8", errors="ignore") as f:
            return await f.read()

    async def _extract_text(self, path: Path, ext: str) -> str:
        # 统一委托给 DocumentLoader，DocumentStore 不关心具体格式解析细节。
        return await self._loader.load_text(path, ext)

    def _safe_filename(self, filename: str) -> str:
        """文件名清洗：防止路径穿越与非法字符。"""
        name = os.path.basename(filename)
        return re.sub(r"[^0-9A-Za-z.\-_]+", "_", name)
