"""제공사와 무관한 프롬프트 생성 로직."""
from __future__ import annotations

from engine.decision.models import DecisionRequest

INSTRUCTIONS = (
    "당신은 도시 시뮬레이션 속 시민들의 소비 전환 결정을 판단하는 모델입니다. "
    "각 시민이 새로 생긴 매장을 보고 기존 습관을 바꿔 그곳으로 옮길지 판단하세요. "
    "각 항목마다 switch_to_new_store(전환 여부), probability(전환 확률, 0~1), "
    "reason(한국어 한 문장 근거)을 반환하세요."
)


def _describe_citizen(request: DecisionRequest) -> str:
    lines = [
        f"- 시민 #{request.citizen_id}: {request.gender}, 연령대 {request.age_band}",
        f"  신규 매장: {request.new_store_name} ({request.new_store_category}), "
        f"거리 {request.distance_to_new_store_m:.0f}m",
    ]
    if request.current_store_category:
        lines.append(
            f"  기존 이용 매장 유형: {request.current_store_category}, "
            f"거리 {request.distance_to_current_store_m:.0f}m"
        )
    else:
        lines.append("  기존에 정기적으로 이용하는 매장 없음")
    return "\n".join(lines)


def build_batch_prompt(requests: list[DecisionRequest]) -> str:
    citizens = "\n".join(_describe_citizen(r) for r in requests)
    return f"{INSTRUCTIONS}\n\n대상 시민 목록 ({len(requests)}명):\n{citizens}"
