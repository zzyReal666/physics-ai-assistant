from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


class ExamStore:
    def __init__(self, data_dir: str):
        self._file = Path(data_dir) / "exams.json"
        self._file.parent.mkdir(parents=True, exist_ok=True)
        if not self._file.exists():
            self._file.write_text("[]", encoding="utf-8")

    def save_exam(self, exam: dict[str, Any]) -> dict[str, Any]:
        all_exams = self._read()
        exam_id = str(uuid.uuid4())
        record = {
            "id": exam_id,
            "created_at": datetime.utcnow().isoformat() + "Z",
            **exam,
        }
        all_exams.append(record)
        self._write(all_exams)
        return record

    def get_exam(self, exam_id: str) -> dict[str, Any] | None:
        for exam in self._read():
            if exam["id"] == exam_id:
                return exam
        return None

    def _read(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self._file.read_text(encoding="utf-8") or "[]")
        except json.JSONDecodeError:
            data = []
        return data if isinstance(data, list) else []

    def _write(self, data: list[dict[str, Any]]) -> None:
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

