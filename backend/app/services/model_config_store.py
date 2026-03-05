from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ModelConfigStore:
    def __init__(self, data_dir: str):
        self._file = Path(data_dir) / "model_config.json"
        self._file.parent.mkdir(parents=True, exist_ok=True)
        if not self._file.exists():
            self._file.write_text("{}", encoding="utf-8")

    def read(self) -> dict[str, Any]:
        try:
            return json.loads(self._file.read_text(encoding="utf-8") or "{}")
        except json.JSONDecodeError:
            return {}

    def get_model_override(self) -> str | None:
        data = self.read()
        model = data.get("default_llm_model")
        return model if isinstance(model, str) and model.strip() else None

    def write_model_override(self, model: str) -> dict[str, Any]:
        data = self.read()
        data["default_llm_model"] = model.strip()
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

