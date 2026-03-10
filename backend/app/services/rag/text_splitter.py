from __future__ import annotations


class PhysicsTextSplitter:
    """物理文本分块器（教学版）。

    为什么要分块：
    - 向量检索通常以 chunk 为最小检索单位；
    - chunk 太大：召回噪声高，token 成本高；
    - chunk 太小：上下文碎片化，答案连贯性变差。
    """

    def __init__(self, max_chars: int = 350):
        self.max_chars = max_chars

    def split(self, text: str, max_chunks: int = 200) -> list[dict[str, str]]:
        """按字符窗口切分文本并附带顺序索引。"""
        clean = ' '.join(text.split())
        if not clean:
            return []
        parts: list[dict[str, str]] = []
        for i in range(0, len(clean), self.max_chars):
            parts.append({'index': str(len(parts) + 1), 'content': clean[i : i + self.max_chars]})
            if len(parts) >= max_chunks:
                break
        return parts
