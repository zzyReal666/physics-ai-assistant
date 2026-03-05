from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.config import Settings
from app.dependencies import get_model_config_store, get_settings_dep
from app.services.model_config_store import ModelConfigStore


router = APIRouter()


class ProviderStatus(BaseModel):
    deepseek: bool
    openai: bool
    zhipu: bool


class ModelConfigResponse(BaseModel):
    default_llm_model: str
    configured_providers: ProviderStatus
    candidate_models: list[str]


class ModelConfigUpdateRequest(BaseModel):
    default_llm_model: str = Field(..., min_length=1)


def _provider_status(settings: Settings) -> ProviderStatus:
    return ProviderStatus(
        deepseek=bool(settings.deepseek_api_key),
        openai=bool(settings.openai_api_key),
        zhipu=bool(settings.zhipu_api_key),
    )


@router.get("/model", response_model=ModelConfigResponse, summary="获取模型配置")
async def get_model_config(
    settings: Settings = Depends(get_settings_dep),
    store: ModelConfigStore = Depends(get_model_config_store),
) -> ModelConfigResponse:
    model = store.get_model_override() or settings.default_llm_model
    return ModelConfigResponse(
        default_llm_model=model,
        configured_providers=_provider_status(settings),
        candidate_models=[
            "deepseek-chat",
            "gpt-4.1",
            "gpt-4.1-mini",
            "glm-4-flash",
            "glm-4-plus",
        ],
    )


@router.put("/model", response_model=ModelConfigResponse, summary="更新模型配置")
async def update_model_config(
    req: ModelConfigUpdateRequest,
    settings: Settings = Depends(get_settings_dep),
    store: ModelConfigStore = Depends(get_model_config_store),
) -> ModelConfigResponse:
    model = req.default_llm_model.strip()
    if not model:
        raise HTTPException(status_code=400, detail="模型名不能为空")
    store.write_model_override(model)
    return await get_model_config(settings=settings, store=store)

