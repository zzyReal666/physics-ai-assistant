from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExamGenerateRequest(BaseModel):
    knowledge_points: str = Field(..., description='知识点范围')
    difficulty: Literal['easy', 'medium', 'hard'] = 'medium'
    question_types: str = Field(default='选择题4道 + 计算题2道', description='题型组合描述')
    total_score: int = Field(default=100, ge=20, le=200)
    paper_type: str = Field(default='阶段测试')


class ExamQuestion(BaseModel):
    type: str
    title: str
    score: int
    answer_outline: str


class ExamGenerateResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    exam_id: str
    title: str
    questions: list[ExamQuestion]
    latex_content: str
    download_url: str
    from_llm: bool = False
    model_used: Optional[str] = None


class ExamListItem(BaseModel):
    id: str
    title: str
    knowledge_points: str
    difficulty: str
    total_score: int
    paper_type: str
    created_at: str
