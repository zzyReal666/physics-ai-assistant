from __future__ import annotations

from app.services.llm.client import LLMClient


class TeachingAgent:
    """备课 Agent（教学占位实现）。"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
