"""프로파일 단위 응답 캐시 (CLAUDE.md 원칙 2)."""
from __future__ import annotations

from engine.decision.models import DecisionRequest, DecisionResult

DISTANCE_BUCKET_M = 100


def profile_key(request: DecisionRequest) -> tuple:
    """비슷한 시민(성별·연령대·거리 구간·매장 유형이 같음)은 같은 캐시 키를 공유한다."""
    distance_bucket = round(request.distance_to_new_store_m / DISTANCE_BUCKET_M)
    return (
        request.gender,
        request.age_band,
        request.new_store_category,
        distance_bucket,
        request.current_store_category,
    )


class DecisionCache:
    def __init__(self) -> None:
        self._store: dict[tuple, DecisionResult] = {}

    def get(self, request: DecisionRequest) -> DecisionResult | None:
        return self._store.get(profile_key(request))

    def set(self, request: DecisionRequest, result: DecisionResult) -> None:
        self._store[profile_key(request)] = result
