from __future__ import annotations

import json
import os
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles


ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "png", "jpg", "jpeg", "txt", "md"}


@dataclass
class UploadResult:
    document_id: str
    filename: str
    status: str
    message: str


class DocumentStore:
    def __init__(self, data_dir: str):
        root = Path(data_dir)
        self._uploads_dir = root / "uploads"
        self._metadata_file = root / "metadata.json"
        self._uploads_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_file.parent.mkdir(parents=True, exist_ok=True)
        if not self._metadata_file.exists():
            self._metadata_file.write_text("[]", encoding="utf-8")

    async def upload(self, filename: str, content: bytes) -> UploadResult:
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
            "status": "processed",
            "created_at": datetime.utcnow().isoformat() + "Z",
        }
        await self._append_metadata(doc)
        return UploadResult(
            document_id=document_id,
            filename=filename,
            status="processed",
            message="文件上传成功并已完成简化解析",
        )

    async def list_documents(self) -> list[dict[str, Any]]:
        docs = await self._read_metadata()
        return sorted(docs, key=lambda d: d.get("created_at", ""), reverse=True)

    async def get_document(self, document_id: str) -> dict[str, Any] | None:
        docs = await self._read_metadata()
        for doc in docs:
            if doc["id"] == document_id:
                chunks = await self._build_chunks(doc)
                return {**doc, "chunks": chunks, "chunk_count": len(chunks)}
        return None

    async def retrieve_chunks(self, query: str, top_k: int = 3) -> list[dict[str, str]]:
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
        file_path = self._uploads_dir / doc["stored_filename"]
        ext = doc.get("file_type", "")
        if ext in {"txt", "md"} and file_path.exists():
            content = await self._read_text_file(file_path)
            parts = self._split_text(content, max_chars=350)[:max_chunks]
            return [
                {"index": str(i + 1), "content": part}
                for i, part in enumerate(parts)
                if part.strip()
            ]

        return [
            {
                "index": "1",
                "content": (
                    f"文件《{doc['filename']}》已上传。当前MVP版本仅对 txt/md 进行文本切片；"
                    "其他格式已记录元数据，可在后续迭代中接入OCR和结构化解析。"
                ),
            }
        ]

    async def _read_metadata(self) -> list[dict[str, Any]]:
        async with aiofiles.open(self._metadata_file, "r", encoding="utf-8") as f:
            raw = await f.read()
        try:
            data = json.loads(raw or "[]")
        except json.JSONDecodeError:
            data = []
        return data if isinstance(data, list) else []

    async def _append_metadata(self, doc: dict[str, Any]) -> None:
        docs = await self._read_metadata()
        docs.append(doc)
        async with aiofiles.open(self._metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(docs, ensure_ascii=False, indent=2))

    async def _read_text_file(self, path: Path) -> str:
        async with aiofiles.open(path, "r", encoding="utf-8", errors="ignore") as f:
            return await f.read()

    def _split_text(self, text: str, max_chars: int) -> list[str]:
        clean = " ".join(text.split())
        if not clean:
            return []
        out: list[str] = []
        for i in range(0, len(clean), max_chars):
            out.append(clean[i : i + max_chars])
        return out

    def _safe_filename(self, filename: str) -> str:
        name = os.path.basename(filename)
        return re.sub(r"[^0-9A-Za-z.\-_]+", "_", name)
