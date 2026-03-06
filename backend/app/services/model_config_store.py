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

    def get_runtime_config(self) -> dict[str, Any]:
        data = self.read()
        return {
            "default_llm_model": self._as_str(data.get("default_llm_model")),
            "deepseek_api_key": self._as_str(data.get("deepseek_api_key")),
            "deepseek_base_url": self._as_str(data.get("deepseek_base_url")),
            "openai_api_key": self._as_str(data.get("openai_api_key")),
            "openai_base_url": self._as_str(data.get("openai_base_url")),
            "zhipu_api_key": self._as_str(data.get("zhipu_api_key")),
            "zhipu_base_url": self._as_str(data.get("zhipu_base_url")),
        }

    def write_runtime_config(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = self.read()
        fields = [
            "default_llm_model",
            "deepseek_api_key",
            "deepseek_base_url",
            "openai_api_key",
            "openai_base_url",
            "zhipu_api_key",
            "zhipu_base_url",
        ]
        for key in fields:
            if key in payload:
                value = payload.get(key)
                data[key] = value.strip() if isinstance(value, str) else ""
        self._file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return data

    def _as_str(self, value: Any) -> str:
        return value.strip() if isinstance(value, str) else ""
