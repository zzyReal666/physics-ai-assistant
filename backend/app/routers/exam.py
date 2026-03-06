from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field

from app.dependencies import get_exam_store
from app.services.exam_store import ExamStore


router = APIRouter()


class ExamGenerateRequest(BaseModel):
    knowledge_points: str = Field(..., description="知识点范围")
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    question_types: str = Field(
        default="选择题4道 + 计算题2道", description="题型组合描述"
    )
    total_score: int = Field(default=100, ge=20, le=200)
    paper_type: str = Field(default="阶段测试")


class ExamQuestion(BaseModel):
    type: str
    title: str
    score: int
    answer_outline: str


class ExamGenerateResponse(BaseModel):
    exam_id: str
    title: str
    questions: list[ExamQuestion]
    latex_content: str
    download_url: str


def _build_exam(req: ExamGenerateRequest) -> tuple[str, list[ExamQuestion], str]:
    title = f"{req.knowledge_points}-{req.difficulty}难度-{req.paper_type}"
    questions = [
        ExamQuestion(
            type="选择题",
            title="下列关于牛顿第二定律的说法正确的是（ ）",
            score=10,
            answer_outline="强调合外力与加速度方向一致，m 恒定时 a 与 F 成正比。",
        ),
        ExamQuestion(
            type="选择题",
            title="质量2kg物体受水平拉力和摩擦力作用，求加速度表达式。",
            score=10,
            answer_outline="先受力分析，再列 $F_\\text{合}=ma$。",
        ),
        ExamQuestion(
            type="计算题",
            title="斜面上物体下滑，已知倾角和摩擦系数，求加速度。",
            score=20,
            answer_outline="沿斜面方向列方程，分解重力并考虑摩擦力方向。",
        ),
    ]
    latex = r"""
\documentclass[12pt]{article}
\usepackage{ctex}
\usepackage{amsmath}
\begin{document}
\section*{物理试卷（示例）}
\textbf{范围：}""" + req.knowledge_points + r""" \\
\textbf{难度：}""" + req.difficulty + r""" \\
\textbf{总分：}""" + str(req.total_score) + r""" \\
\begin{enumerate}
\item 下列关于牛顿第二定律的说法正确的是（ ）。
\item 质量$2kg$物体受水平拉力和摩擦力作用，求加速度表达式。
\item 斜面上物体下滑，已知倾角和摩擦系数，求加速度。
\end{enumerate}
\end{document}
""".strip()
    return title, questions, latex


@router.post("/generate", response_model=ExamGenerateResponse, summary="生成试卷")
async def generate_exam(
    req: ExamGenerateRequest,
    store: ExamStore = Depends(get_exam_store),
) -> ExamGenerateResponse:
    title, questions, latex = _build_exam(req)
    exam = store.save_exam(
        {
            "title": title,
            "knowledge_points": req.knowledge_points,
            "difficulty": req.difficulty,
            "question_types": req.question_types,
            "total_score": req.total_score,
            "paper_type": req.paper_type,
            "questions": [q.model_dump() for q in questions],
            "latex_content": latex,
        }
    )
    return ExamGenerateResponse(
        exam_id=exam["id"],
        title=title,
        questions=questions,
        latex_content=latex,
        download_url=f"/api/exam/{exam['id']}/download?format=latex",
    )


@router.get("/{exam_id}/download", summary="下载试卷")
async def download_exam(
    exam_id: str,
    format: str = Query(default="latex"),
    store: ExamStore = Depends(get_exam_store),
) -> Response:
    exam = store.get_exam(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="试卷不存在")
    if format != "latex":
        raise HTTPException(status_code=400, detail="当前仅支持 latex 格式")
    content = exam.get("latex_content", "")
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=exam-{exam_id}.tex",
        },
    )
