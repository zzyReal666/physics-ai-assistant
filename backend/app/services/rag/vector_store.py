from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonVectorStore:
    """基于 JSON 的简化向量存储。

    教学目的：
    - 让你先理解“向量库接口”该长什么样；
    - 后续可以无缝替换为 Chroma/Qdrant/LanceDB。
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text('[]', encoding='utf-8')

    def read_all(self) -> list[dict[str, Any]]:
        """读取全部向量记录。"""
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def write_all(self, rows: list[dict[str, Any]]) -> None:
        """全量写回记录。"""
        self.path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')

    def upsert_document_chunks(self, document_id: str, rows: list[dict[str, Any]]) -> int:
        """按 document_id 做“覆盖式 upsert”。"""
        cur = self.read_all()
        cur = [x for x in cur if x.get('document_id') != document_id]
        cur.extend(rows)
        self.write_all(cur)
        return len(rows)

    def remove_document(self, document_id: str) -> None:
        """删除指定文档的全部 chunks。"""
        cur = self.read_all()
        cur = [x for x in cur if x.get('document_id') != document_id]
        self.write_all(cur)
