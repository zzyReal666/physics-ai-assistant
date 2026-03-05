from __future__ import annotations

from typing import Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import LLMClient, get_document_store, get_llm_client
from app.services.document_store import DocumentStore


router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., description="教师输入的物理问题，可包含文字描述")
    student_level: Literal["junior", "senior"] = Field(
        "senior", description="学生水平（用于控制讲解难度）"
    )


class ChatAnswer(BaseModel):
    content: str
    model_used: Optional[str] = None
    from_llm: bool = False
    references: list[dict[str, str]] = []


SYSTEM_PROMPT_QA = """
你是一名优秀的高中物理教师，请用中文回答问题。
- 严谨使用物理概念，适当渲染 LaTeX 公式（例如 F=ma 用 $F=ma$）。
- 按“分析受力/列式/求解/检验”的结构给出分步解答。
- 如果题目信息不足，请明确指出并做合理假设。
""".strip()


def _fallback_answer(req: ChatRequest, references: list[dict[str, str]]) -> ChatAnswer:
    """在未配置 LLM 时的简易规则回答，方便本地快速验证链路。"""
    if "牛顿第二定律" in req.question or "F=ma" in req.question:
        content = (
            "【示例回答（本地规则引擎，未调用真实大模型）】\n\n"
            "题目涉及牛顿第二定律，可以按以下步骤讲解：\n"
            "1. 明确研究对象，画受力分析图，找出合外力 $F_\\text{合}$。\n"
            "2. 应用牛顿第二定律：$F_\\text{合} = ma$，列出分量方程。\n"
            "3. 代入已知量求出加速度 $a$，注意方向和正负号。\n"
            "4. 可提醒学生：质量 $m$ 一般为常量，加速度与合外力成正比，与质量成反比。"
        )
        return ChatAnswer(content=content, from_llm=False, references=references)

    content = (
        "【示例回答（本地规则引擎，未调用真实大模型）】\n\n"
        "目前未配置任何大模型 API Key，所以返回的是一个示例模板回答。\n"
        "你可以在 `backend/.env` 中配置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY，"
        "然后重新启动服务，就会自动切换为真实大模型推理结果。\n\n"
        "针对你的问题，建议按照以下物理解题思路进行：\n"
        "1. 明确研究对象和受力情况，必要时画受力分析图。\n"
        "2. 找出相关物理定律（如牛顿定律、能量守恒等），用数学形式写出方程。\n"
        "3. 结合已知条件化简求解，注意单位与方向。\n"
        "4. 最后进行合理性检查（数量级、方向、极端情况）。"
    )
    return ChatAnswer(content=content, from_llm=False, references=references)


@router.post("/ask", response_model=ChatAnswer, summary="AI 物理解题答疑（简化版）")
async def ask_question(
    req: ChatRequest,
    llm_client: LLMClient = Depends(get_llm_client),
    store: DocumentStore = Depends(get_document_store),
) -> ChatAnswer:
    """AI 答疑入口。

    - 若已配置 LLM Key：调用真实大模型给出分步解答；
    - 若未配置：返回内置的“示例解题模板”，方便本地验证。
    """
    chunks = await store.retrieve_chunks(req.question, top_k=3)
    references = [
        {"source": chunk["filename"], "content": chunk["content"][:180]}
        for chunk in chunks
    ]

    if not llm_client.enabled:
        return _fallback_answer(req, references)

    context = "\n\n".join([f"[{c['filename']}] {c['content']}" for c in chunks]) or "无检索上下文"
    user_prompt = (
        f"学生水平：{'高一' if req.student_level == 'junior' else '高二/高三'}。\n"
        f"检索上下文：\n{context}\n\n"
        f"请用适合该水平学生的方式，详细解答以下问题：\n\n{req.question}"
    )

    content = await llm_client.chat(SYSTEM_PROMPT_QA, user_prompt)
    return ChatAnswer(
        content=content,
        model_used=llm_client.settings.default_llm_model,
        from_llm=True,
        references=references,
    )

