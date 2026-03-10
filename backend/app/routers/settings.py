from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings
from app.dependencies import get_model_config_store, get_settings_dep
from app.models import ModelConfigResponse, ModelConfigUpdateRequest, ProviderStatus
from app.services.model_config_store import ModelConfigStore


router = APIRouter()


def _provider_status(settings: Settings, runtime: dict[str, str]) -> ProviderStatus:
    deepseek_key = runtime.get("deepseek_api_key") or settings.deepseek_api_key or ""
    openai_key = runtime.get("openai_api_key") or settings.openai_api_key or ""
    zhipu_key = runtime.get("zhipu_api_key") or settings.zhipu_api_key or ""
    return ProviderStatus(
        deepseek=bool(deepseek_key),
        openai=bool(openai_key),
        zhipu=bool(zhipu_key),
    )


@router.get("/model", response_model=ModelConfigResponse, summary="获取模型配置")
async def get_model_config(
    settings: Settings = Depends(get_settings_dep),
    store: ModelConfigStore = Depends(get_model_config_store),
) -> ModelConfigResponse:
    runtime = store.get_runtime_config()
    model = runtime.get("default_llm_model") or settings.default_llm_model
    return ModelConfigResponse(
        default_llm_model=model,
        configured_providers=_provider_status(settings, runtime),
        candidate_models=[
            "deepseek-chat",
            "gpt-4.1",
            "gpt-4.1-mini",
            "glm-4-flash",
            "glm-4-plus",
        ],
        deepseek_api_key=runtime.get("deepseek_api_key") or settings.deepseek_api_key or "",
        deepseek_base_url=runtime.get("deepseek_base_url") or settings.deepseek_base_url,
        openai_api_key=runtime.get("openai_api_key") or settings.openai_api_key or "",
        openai_base_url=runtime.get("openai_base_url") or settings.openai_base_url,
        zhipu_api_key=runtime.get("zhipu_api_key") or settings.zhipu_api_key or "",
        zhipu_base_url=runtime.get("zhipu_base_url") or settings.zhipu_base_url,
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
    store.write_runtime_config(req.model_dump())
    return await get_model_config(settings=settings, store=store)
