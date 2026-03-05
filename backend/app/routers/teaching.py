from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import LLMClient, get_llm_client


router = APIRouter()


class TeachingPlanRequest(BaseModel):
    topic: str = Field(..., description="备课主题/知识点，如“牛顿第二定律”")
    class_info: str = Field(
        ..., description="班级情况和课时信息，如“高二重点班，45分钟”"
    )
    requirements: Optional[str] = Field(
        default=None, description="特殊要求，如“包含实验演示和3道典型例题”"
    )


class TeachingPlanResponse(BaseModel):
    topic: str
    plan_markdown: str
    model_used: Optional[str] = None
    from_llm: bool = False


SYSTEM_PROMPT_TEACHING = """
你是一名资深高中物理教师，擅长按中国高中教学大纲设计教案。
请根据给定的“教学主题”“班级情况”和“特殊要求”，输出一份 Markdown 格式的教案，
结构建议为：

1. 教学目标（知识与技能、过程与方法、情感态度价值观）
2. 教学重难点
3. 教学流程（含时间分配：导入、讲授、新授、例题、练习、小结、作业）
4. 教学资源（教材章节、实验、视频、示意图说明等）
5. 板书设计或课后反思要点

答题要求：
- 使用中文；
- 适当使用 LaTeX 公式表示物理量（例如 $F=ma$）；
- 结合主题给出 2~3 道典型例题（只需题目与简要思路，无需完整解答）。
""".strip()


def _fallback_plan(req: TeachingPlanRequest) -> TeachingPlanResponse:
    """未配置 LLM 时的固定示例教案（以牛顿第二定律为例）。"""
    md = f"""# 教案示例：{req.topic}

> 本教案为示例内容（未调用真实大模型），主要用于本地联调和界面展示。

## 一、教学目标

1. 知识与技能
   - 理解牛顿第二定律的物理意义，掌握公式 $F=ma$ 的矢量性质。
   - 会在简单情景中根据受力情况求加速度。
2. 过程与方法
   - 通过实验观察“力对物体运动状态的影响”，培养实验探究能力。
3. 情感态度与价值观
   - 体会牛顿运动定律在现代科技中的重要作用，激发学习兴趣。

## 二、教学重难点

- 重点：$F=ma$ 中“合外力”与“加速度”的对应关系。
- 难点：区分“受力大小变化”和“物体运动状态变化”之间的关系。

## 三、教学流程（45min，示例）

1. 导入（5min）
   - 通过生活实例（地铁启动、突然刹车）引出“力与加速度”的关系。
2. 新课讲授（20min）
   - 受力分析示例：水平拉小车、斜面运动等。
   - 归纳得出牛顿第二定律：$F_\\text{{合}} = ma$。
3. 典型例题（10min）
   - 例1：水平面上受拉力和摩擦力的加速度计算。
   - 例2：斜面上物体滑动的受力与加速度分析。
4. 课堂练习（5min）
   - 2~3 道基础计算题，教师巡视辅导。
5. 课堂小结（3min）
6. 布置作业（2min）

## 四、教学资源

- 教材：人教版高中物理必修一，相应章节。
- 实验：力与加速度关系的小车实验（可用演示视频代替）。
- 示意图：受力分析图、$v$-$t$ 图等。

## 五、备注

- 班级信息：{req.class_info}
- 特殊要求：{req.requirements or "无特殊要求"}
"""
    return TeachingPlanResponse(
        topic=req.topic, plan_markdown=md, from_llm=False, model_used=None
    )


@router.post(
    "/create-plan",
    response_model=TeachingPlanResponse,
    summary="AI 备课助手（简化版）",
)
async def create_teaching_plan(
    req: TeachingPlanRequest,
    llm_client: LLMClient = Depends(get_llm_client),
) -> TeachingPlanResponse:
    """根据主题和班级情况生成教案。

    - 已配置 LLM 时：调用真实模型生成 Markdown 教案；
    - 未配置时：返回固定示例教案（便于本地验证）。
    """
    if not llm_client.enabled:
        return _fallback_plan(req)

    user_prompt = (
        f"教学主题：{req.topic}\n"
        f"班级情况：{req.class_info}\n"
        f"特殊要求：{req.requirements or '无'}\n\n"
        "请按照系统提示的结构给出完整教案。"
    )
    md = await llm_client.chat(SYSTEM_PROMPT_TEACHING, user_prompt)
    return TeachingPlanResponse(
        topic=req.topic,
        plan_markdown=md,
        from_llm=True,
        model_used=llm_client.active_model,
    )


