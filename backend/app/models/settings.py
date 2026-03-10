from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderStatus(BaseModel):
    deepseek: bool
    openai: bool
    zhipu: bool


class ModelConfigResponse(BaseModel):
    default_llm_model: str
    configured_providers: ProviderStatus
    candidate_models: list[str]
    deepseek_api_key: str
    deepseek_base_url: str
    openai_api_key: str
    openai_base_url: str
    zhipu_api_key: str
    zhipu_base_url: str


class ModelConfigUpdateRequest(BaseModel):
    default_llm_model: str = Field(..., min_length=1)
    deepseek_api_key: str = ''
    deepseek_base_url: str = ''
    openai_api_key: str = ''
    openai_base_url: str = ''
    zhipu_api_key: str = ''
    zhipu_base_url: str = ''
