from __future__ import annotations

from typing import Optional

from openai import AsyncOpenAI

from app.config import Settings


class LLMClient:
    """统一封装多提供商 LLM 客户端。"""

    def __init__(self, settings: Settings, runtime_config: dict[str, str] | None = None):
        self.settings = settings
        cfg = runtime_config or {}
        self.active_model = cfg.get('default_llm_model') or settings.default_llm_model

        self._deepseek_client: Optional[AsyncOpenAI] = None
        self._openai_client: Optional[AsyncOpenAI] = None
        self._zhipu_client: Optional[AsyncOpenAI] = None

        deepseek_key = cfg.get('deepseek_api_key') or settings.deepseek_api_key
        deepseek_base_url = cfg.get('deepseek_base_url') or settings.deepseek_base_url
        openai_key = cfg.get('openai_api_key') or settings.openai_api_key
        openai_base_url = cfg.get('openai_base_url') or settings.openai_base_url
        zhipu_key = cfg.get('zhipu_api_key') or settings.zhipu_api_key
        zhipu_base_url = cfg.get('zhipu_base_url') or settings.zhipu_base_url

        if deepseek_key:
            self._deepseek_client = AsyncOpenAI(api_key=deepseek_key, base_url=deepseek_base_url)
        if openai_key:
            self._openai_client = AsyncOpenAI(api_key=openai_key, base_url=openai_base_url)
        if zhipu_key:
            self._zhipu_client = AsyncOpenAI(api_key=zhipu_key, base_url=zhipu_base_url)

    @property
    def enabled(self) -> bool:
        return bool(self._deepseek_client or self._openai_client or self._zhipu_client)

    def _select_client(self) -> AsyncOpenAI:
        model = self.active_model.lower()
        if 'deepseek' in model:
            if not self._deepseek_client:
                raise RuntimeError('未配置 DeepSeek API Key')
            return self._deepseek_client
        if 'glm' in model or 'zhipu' in model:
            if not self._zhipu_client:
                raise RuntimeError('未配置 智谱 API Key')
            return self._zhipu_client
        if not self._openai_client:
            raise RuntimeError('未配置 OpenAI API Key')
        return self._openai_client

    async def chat(self, system_prompt: str, user_prompt: str) -> str:
        client = self._select_client()
        resp = await client.chat.completions.create(
            model=self.active_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
        )
        return resp.choices[0].message.content or ''
