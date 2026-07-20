"""전환점 의사결정 요청/응답 모델."""
from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class DecisionRequest:
    """신규 매장 발견 시 전환 여부를 물을 시민 1명 + 매장 1곳의 맥락."""

    citizen_id: int
    gender: str
    age_band: str
    new_store_name: str
    new_store_category: str
    distance_to_new_store_m: float
    current_store_category: str | None = None
    distance_to_current_store_m: float | None = None


class DecisionResult(BaseModel):
    """LLM이 반환하는 구조화된 전환 결정."""

    switch_to_new_store: bool
    probability: float = Field(ge=0.0, le=1.0)
    reason: str
