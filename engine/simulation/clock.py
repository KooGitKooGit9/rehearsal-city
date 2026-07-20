"""시뮬레이션 시간: 10분 단위 틱 (CLAUDE.md 원칙 3)."""
from __future__ import annotations

TICK_MINUTES = 10
TICKS_PER_DAY = 24 * 60 // TICK_MINUTES  # 144


def tick_to_clock_str(tick: int) -> str:
    total_minutes = (tick % TICKS_PER_DAY) * TICK_MINUTES
    hour, minute = divmod(total_minutes, 60)
    return f"{hour:02d}:{minute:02d}"


def tick_to_hour(tick: int) -> int:
    return (tick % TICKS_PER_DAY) * TICK_MINUTES // 60
