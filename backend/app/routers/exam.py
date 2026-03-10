from __future__ import annotations

import json
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.dependencies import LLMClient, get_exam_store, get_llm_client
from app.models import (
    ExamGenerateRequest,
    ExamGenerateResponse,
    ExamListItem,
    ExamQuestion,
)
from app.services.exam_store import ExamStore


router = APIRouter()


SYSTEM_PROMPT_EXAM = """
你是一名高中物理命题老师。请根据给定参数生成试卷题目。
要求：
1) 覆盖指定知识点；
2) 难度符合要求；
3) 输出 JSON 数组，每个元素包含字段：type,title,score,answer_outline；
4) 只输出 JSON，不要解释文字。
""".strip()


def _parse_question_type_counts(text: str) -> list[tuple[str, int]]:
    found = re.findall(r"(选择题|填空题|实验题|计算题|简答题)\s*(\d+)\s*道", text)
    if found:
        return [(t, int(c)) for t, c in found if int(c) > 0]
    return [("选择题", 4), ("计算题", 2)]


def _build_latex(title: str, req: ExamGenerateRequest, questions: list[ExamQuestion]) -> str:
    lines = [
        r"\documentclass[12pt]{article}",
        r"\usepackage{ctex}",
        r"\usepackage{amsmath}",
        r"\begin{document}",
        rf"\section*{{{title}}}",
        rf"\textbf{{范围：}}{req.knowledge_points} \\",
        rf"\textbf{{难度：}}{req.difficulty} \\",
        rf"\textbf{{总分：}}{req.total_score} \\",
        r"\begin{enumerate}",
    ]
    for q in questions:
        lines.append(rf"\item ({q.type}, {q.score}分) {q.title}")
    lines.extend([r"\end{enumerate}", r"\end{document}"])
    return "\n".join(lines)


def _build_rule_questions(req: ExamGenerateRequest) -> list[ExamQuestion]:
    type_counts = _parse_question_type_counts(req.question_types)
    total = sum(c for _, c in type_counts)
    total = max(total, 1)
    base = req.total_score // total
    rest = req.total_score % total
    diff_hint = {
        "easy": "注重基础概念与直接应用",
        "medium": "包含多步推导与综合分析",
        "hard": "强调综合建模与变式推理",
    }[req.difficulty]
    questions: list[ExamQuestion] = []
    idx = 0
    for q_type, count in type_counts:
        for i in range(1, count + 1):
            idx += 1
            score = base + (1 if idx <= rest else 0)
            questions.append(
                ExamQuestion(
                    type=q_type,
                    title=f"{req.knowledge_points}（{q_type}{i}）：请根据题设完成物理分析并给出结论。",
                    score=score,
                    answer_outline=f"{diff_hint}；先列已知与未知，再用对应定律列式求解并检验量纲。",
                )
            )
    return questions


def _try_parse_llm_questions(raw: str) -> list[ExamQuestion]:
    text = raw.strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("llm输出不是json数组")
    arr = json.loads(text[start : end + 1])
    if not isinstance(arr, list):
        raise ValueError("llm输出格式错误")
    out: list[ExamQuestion] = []
    for item in arr:
        if not isinstance(item, dict):
            continue
        out.append(
            ExamQuestion(
                type=str(item.get("type", "综合题")),
                title=str(item.get("title", "")).strip() or "请完成本题作答。",
                score=int(item.get("score", 10)),
                answer_outline=str(item.get("answer_outline", "结合相关定律分步作答。")),
            )
        )
    if not out:
        raise ValueError("llm未返回有效题目")
    return out


def _build_exam(req: ExamGenerateRequest, questions: list[ExamQuestion]) -> tuple[str, str]:
    title = f"{req.knowledge_points}-{req.difficulty}难度-{req.paper_type}"
    latex = _build_latex(title, req, questions)
    return title, latex


@router.post("/generate", response_model=ExamGenerateResponse, summary="生成试卷")
async def generate_exam(
    req: ExamGenerateRequest,
    store: ExamStore = Depends(get_exam_store),
    llm_client: LLMClient = Depends(get_llm_client),
) -> ExamGenerateResponse:
    from_llm = False
    model_used: str | None = None
    questions: list[ExamQuestion]
    if llm_client.enabled:
        try:
            prompt = (
                f"知识点：{req.knowledge_points}\n"
                f"难度：{req.difficulty}\n"
                f"题型组合：{req.question_types}\n"
                f"总分：{req.total_score}\n"
                f"试卷类型：{req.paper_type}\n"
                "请返回题目JSON数组。"
            )
            llm_text = await llm_client.chat(SYSTEM_PROMPT_EXAM, prompt)
            questions = _try_parse_llm_questions(llm_text)
            from_llm = True
            model_used = llm_client.active_model
        except Exception:
            questions = _build_rule_questions(req)
    else:
        questions = _build_rule_questions(req)

    title, latex = _build_exam(req, questions)
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
            "from_llm": from_llm,
            "model_used": model_used,
        }
    )
    return ExamGenerateResponse(
        exam_id=exam["id"],
        title=title,
        questions=questions,
        latex_content=latex,
        download_url=f"/api/exam/{exam['id']}/download?format=latex",
        from_llm=from_llm,
        model_used=model_used,
    )


@router.get("/", response_model=list[ExamListItem], summary="试卷列表")
async def list_exams(store: ExamStore = Depends(get_exam_store)) -> list[ExamListItem]:
    exams = store.list_exams()
    return [ExamListItem(**exam) for exam in exams]


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
