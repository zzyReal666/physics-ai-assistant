from __future__ import annotations

from datetime import datetime


def utc_now_iso() -> str:
    """返回 UTC ISO 时间字符串。"""

    return datetime.utcnow().isoformat() + 'Z'
