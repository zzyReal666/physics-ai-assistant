from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from .config import Settings, get_settings
from .services.document_store import DocumentStore
from .services.exam_store import ExamStore
from .services.llm.client import LLMClient
from .services.model_config_store import ModelConfigStore
from .services.rag_service import RagService


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
    return LLMClient(settings, runtime_config=model_store.get_runtime_config())


@lru_cache(maxsize=1)
def _get_document_store_cached(data_dir: str) -> DocumentStore:
    return DocumentStore(data_dir=data_dir)


def get_document_store(settings: Settings = Depends(get_settings_dep)) -> DocumentStore:
    return _get_document_store_cached(settings.data_dir)


@lru_cache(maxsize=1)
def _get_exam_store_cached(data_dir: str) -> ExamStore:
    return ExamStore(data_dir=data_dir)


def get_exam_store(settings: Settings = Depends(get_settings_dep)) -> ExamStore:
    return _get_exam_store_cached(settings.data_dir)


@lru_cache(maxsize=1)
def _get_rag_service_cached(data_dir: str, embedding_model: str, rag_top_k: int) -> RagService:
    settings = get_settings()
    return RagService(settings=settings)


def get_rag_service(settings: Settings = Depends(get_settings_dep)) -> RagService:
    return _get_rag_service_cached(
        settings.data_dir, settings.embedding_model, settings.rag_top_k
    )


__all__ = [
    'LLMClient',
    'get_llm_client',
    'get_settings_dep',
    'get_document_store',
    'get_model_config_store',
    'get_exam_store',
    'get_rag_service',
]
