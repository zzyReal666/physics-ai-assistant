from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import Depends
from openai import AsyncOpenAI

from .config import Settings, get_settings
from .services.document_store import DocumentStore
from .services.model_config_store import ModelConfigStore


class LLMClient:
    """统一封装的大模型客户端。

    - 如果未配置任何 API Key，则不会真正调用外部服务，
      上层可根据 `enabled` 字段决定返回“示例回答”。
    """

    def __init__(self, settings: Settings, model_override: str | None = None):
        self.settings = settings
        self.active_model = model_override or settings.default_llm_model

        self._deepseek_client: Optional[AsyncOpenAI] = None
        self._openai_client: Optional[AsyncOpenAI] = None
        self._zhipu_client: Optional[AsyncOpenAI] = None

        if settings.deepseek_api_key:
            self._deepseek_client = AsyncOpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
            )

        if settings.openai_api_key:
            self._openai_client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
            )
        if settings.zhipu_api_key:
            self._zhipu_client = AsyncOpenAI(
                api_key=settings.zhipu_api_key,
                base_url=settings.zhipu_base_url,
            )

    @property
    def enabled(self) -> bool:
        return bool(self._deepseek_client or self._openai_client or self._zhipu_client)

    def _select_client(self) -> AsyncOpenAI:
        """根据模型名称选择底层客户端。"""
        model = self.active_model.lower()
        if "deepseek" in model:
            if not self._deepseek_client:
                raise RuntimeError("未配置 DeepSeek API Key")
            return self._deepseek_client  # type: ignore[return-value]
        if "glm" in model or "zhipu" in model:
            if not self._zhipu_client:
                raise RuntimeError("未配置 智谱 API Key")
            return self._zhipu_client  # type: ignore[return-value]

        # 默认走 openai 兼容接口
        if not self._openai_client:
            raise RuntimeError("未配置 OpenAI API Key")
        return self._openai_client  # type: ignore[return-value]

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        """最小封装：给定 system + user prompt，返回文本回复。"""
        client = self._select_client()
        resp = await client.chat.completions.create(
            model=self.active_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""


def get_settings_dep() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def _get_model_config_store_cached(data_dir: str) -> ModelConfigStore:
    return ModelConfigStore(data_dir=data_dir)


def get_model_config_store(
    settings: Settings = Depends(get_settings_dep),
) -> ModelConfigStore:
    return _get_model_config_store_cached(settings.data_dir)


def get_llm_client(
    settings: Settings = Depends(get_settings_dep),
    model_store: ModelConfigStore = Depends(get_model_config_store),
) -> LLMClient:
    return LLMClient(settings, model_override=model_store.get_model_override())


@lru_cache(maxsize=1)
def _get_document_store_cached(data_dir: str) -> DocumentStore:
    return DocumentStore(data_dir=data_dir)


def get_document_store(settings: Settings = Depends(get_settings_dep)) -> DocumentStore:
    return _get_document_store_cached(settings.data_dir)


__all__ = [
    "LLMClient",
    "get_llm_client",
    "get_settings_dep",
    "get_document_store",
    "get_model_config_store",
]
