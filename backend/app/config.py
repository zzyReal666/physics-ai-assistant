from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，支持从 .env / 环境变量加载。"""

    # 基础
    app_env: str = Field("dev", alias="APP_ENV")

    # LLM 相关（可选）
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL"
    )

    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_BASE_URL"
    )

    default_llm_model: str = Field(
        default="deepseek-chat",
        alias="DEFAULT_LLM_MODEL",
        description="默认使用的大模型名称，例如 deepseek-chat / gpt-4.1",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取全局配置（带缓存）。"""
    return Settings()


__all__ = ["Settings", "get_settings"]

