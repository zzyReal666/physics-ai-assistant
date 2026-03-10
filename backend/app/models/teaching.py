from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TeachingPlanRequest(BaseModel):
    topic: str = Field(..., description='备课主题/知识点，如“牛顿第二定律”')
    class_info: str = Field(..., description='班级情况和课时信息，如“高二重点班，45分钟”')
    requirements: Optional[str] = Field(default=None, description='特殊要求')


class TeachingPlanResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    topic: str
    plan_markdown: str
    model_used: Optional[str] = None
    from_llm: bool = False
