from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Optional

from openai import AsyncOpenAI

from app.config import Settings


class EmbeddingService:
    """Embedding 服务：远端优先，本地兜底。

    设计取舍：
    - 生产环境通常直接用高质量 embedding 模型；
    - 教学/离线场景经常没有网络或 key，所以保留本地 hash embedding 兜底，
      让整个 RAG 流程始终可跑通。
    """

    def __init__(self, settings: Settings, runtime_cfg_path: Path):
        self.settings = settings
        self.runtime_cfg_path = runtime_cfg_path
        self._client: Optional[AsyncOpenAI] = None

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量向量化。

        注意：异常不外抛到上层，而是回退到本地 embedding。
        这样做可以保证“系统可用性优先”，适合教学项目。
        """
        if not texts:
            return []
        try:
            client = self._get_client()
            if client:
                resp = await client.embeddings.create(model=self.settings.embedding_model, input=texts)
                return [item.embedding for item in resp.data]
        except Exception:
            pass
        return [self._local_hash_embedding(t) for t in texts]

    def _get_client(self) -> Optional[AsyncOpenAI]:
        """按“运行时配置 > 环境变量”优先级创建 embedding 客户端。"""
        if self._client:
            return self._client
        cfg = self._read_json(self.runtime_cfg_path)
        api_key = cfg.get('openai_api_key') or self.settings.openai_api_key
        base_url = cfg.get('openai_base_url') or self.settings.openai_base_url
        if not api_key:
            return None
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        return self._client

    def _local_hash_embedding(self, text: str, dim: int = 256) -> list[float]:
        """本地 hash embedding（示意版）。

        逻辑：token -> hash 到固定桶 -> 计数 -> 归一化。
        优点：零依赖可运行；缺点：语义质量明显弱于真实模型。
        """
        vec = [0.0] * dim
        for tok in self._tokenize(text):
            vec[hash(tok) % dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def _tokenize(self, text: str) -> list[str]:
        """轻量分词：英文单词 + 中文单字。"""
        words = re.findall(r'[a-z0-9_]+', text.lower())
        cjk = re.findall(r'[\u4e00-\u9fff]', text)
        return words + cjk

    def _read_json(self, path: Path) -> dict:
        """容错读取 JSON 配置文件。"""
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
