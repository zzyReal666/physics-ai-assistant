from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """聊天问答请求。"""

    question: str = Field(..., description='教师输入的物理问题，可包含文字描述')
    student_level: Literal['junior', 'senior'] = Field(
        'senior', description='学生水平（用于控制讲解难度）'
    )


class ChatAnswer(BaseModel):
    """聊天回答输出。

    retrieval_debug 用于教学与调试：展示检索分数拆解。
    """

    model_config = ConfigDict(protected_namespaces=())
    content: str
    model_used: Optional[str] = None
    from_llm: bool = False
    references: list[dict[str, str]] = Field(default_factory=list)
    retrieval_debug: list[dict[str, float]] = Field(default_factory=list)
