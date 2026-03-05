from __future__ import annotations

from typing import Optional

from fastapi import Depends
from openai import AsyncOpenAI

from .config import Settings, get_settings


class LLMClient:
    """统一封装的大模型客户端。

    - 如果未配置任何 API Key，则不会真正调用外部服务，
      上层可根据 `enabled` 字段决定返回“示例回答”。
    """

    def __init__(self, settings: Settings):
        self.settings = settings

        self._deepseek_client: Optional[AsyncOpenAI] = None
        self._openai_client: Optional[AsyncOpenAI] = None

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

    @property
    def enabled(self) -> bool:
        return bool(self._deepseek_client or self._openai_client)

    def _select_client(self) -> AsyncOpenAI:
        """根据模型名称选择底层客户端。"""
        model = self.settings.default_llm_model.lower()
        if "deepseek" in model:
            if not self._deepseek_client:
                raise RuntimeError("未配置 DeepSeek API Key")
            return self._deepseek_client  # type: ignore[return-value]

        # 默认走 openai 兼容接口
        if not self._openai_client:
            raise RuntimeError("未配置 OpenAI API Key")
        return self._openai_client  # type: ignore[return-value]

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        """最小封装：给定 system + user prompt，返回文本回复。"""
        client = self._select_client()
        resp = await client.chat.completions.create(
            model=self.settings.default_llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return resp.choices[0].message.content or ""


def get_settings_dep() -> Settings:
    return get_settings()


def get_llm_client(settings: Settings = Depends(get_settings_dep)) -> LLMClient:
    return LLMClient(settings)


__all__ = ["LLMClient", "get_llm_client", "get_settings_dep"]

