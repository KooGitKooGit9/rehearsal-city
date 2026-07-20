"""캐시 재사용 + 배칭을 결합한 의사결정 오케스트레이션 (CLAUDE.md 원칙 2)."""
from __future__ import annotations

from engine.decision.cache import DecisionCache
from engine.decision.client import LLMClient
from engine.decision.models import DecisionRequest, DecisionResult


def decide_batch_with_cache(
    client: LLMClient, cache: DecisionCache, requests: list[DecisionRequest]
) -> list[DecisionResult]:
    """캐시에 없는 요청만 모아 한 번의 배치 호출로 처리하고, 입력 순서대로 반환한다."""
    results: list[DecisionResult | None] = [None] * len(requests)
    misses: list[tuple[int, DecisionRequest]] = []

    for i, request in enumerate(requests):
        cached = cache.get(request)
        if cached is not None:
            results[i] = cached
        else:
            misses.append((i, request))

    if misses:
        miss_results = client.decide_batch([request for _, request in misses])
        for (i, request), result in zip(misses, miss_results):
            cache.set(request, result)
            results[i] = result

    return results
