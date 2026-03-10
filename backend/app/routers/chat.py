from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import LLMClient, get_llm_client, get_rag_service
from app.models import ChatAnswer, ChatRequest
from app.services.rag_service import RagService


router = APIRouter()


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
        return ChatAnswer(
            content=content, from_llm=False, references=references, retrieval_debug=[]
        )

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
    return ChatAnswer(content=content, from_llm=False, references=references, retrieval_debug=[])


@router.post("/ask", response_model=ChatAnswer, summary="AI 物理解题答疑（简化版）")
async def ask_question(
    req: ChatRequest,
    llm_client: LLMClient = Depends(get_llm_client),
    rag_service: RagService = Depends(get_rag_service),
) -> ChatAnswer:
    """AI 答疑入口。

    RAG + 生成整体流程：
    1) 先检索：rag_service.retrieve 获取相关 chunks；
    2) 再生成：把检索上下文拼到 prompt，交给 LLM；
    3) 失败兜底：LLM 调用失败时返回本地模板回答。
    """
    chunks = await rag_service.retrieve(req.question, top_k=5)
    references = [
        {"source": chunk.filename, "content": chunk.content[:180]}
        for chunk in chunks
    ]
    retrieval_debug = [
        {
            "score": round(c.score, 4),
            "vector_score": round(c.vector_score, 4),
            "lexical_score": round(c.lexical_score, 4),
        }
        for c in chunks
    ]

    if not llm_client.enabled:
        # 无模型配置时仍返回“可读 + 可教学”的稳定输出。
        ans = _fallback_answer(req, references)
        ans.retrieval_debug = retrieval_debug
        return ans

    context = "\n\n".join([f"[{c.filename}] {c.content}" for c in chunks]) or "无检索上下文"
    user_prompt = (
        f"学生水平：{'高一' if req.student_level == 'junior' else '高二/高三'}。\n"
        f"检索上下文：\n{context}\n\n"
        f"请用适合该水平学生的方式，详细解答以下问题：\n\n{req.question}"
    )

    try:
        # 真实模型调用路径。
        content = await llm_client.chat(SYSTEM_PROMPT_QA, user_prompt)
        return ChatAnswer(
            content=content,
            model_used=llm_client.active_model,
            from_llm=True,
            references=references,
            retrieval_debug=retrieval_debug,
        )
    except Exception:
        # 网络抖动、Key 失效、供应商异常都走这里，避免接口报 500。
        ans = _fallback_answer(req, references)
        ans.content = (
            "【提示】当前大模型调用失败，已自动切换本地教学模板回答。\n\n" + ans.content
        )
        ans.retrieval_debug = retrieval_debug
        return ans
