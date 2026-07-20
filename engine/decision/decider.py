"""캐시 재사용 + 배칭을 결합한 의사결정 오케스트레이션 (CLAUDE.md 원칙 2)."""
from __future__ import annotations

from engine.decision.cache import DecisionCache
from engine.decision.client import LLMClient
from engine.decision.models import DecisionRequest, DecisionResult

# 배치 하나에 너무 많은 항목을 넣으면 LLM이 요청한 개수보다 적게 반환할 위험이
# 커진다(실제로 겪음 — 큰 배치에서 응답 배열 길이가 모자란 경우 발생). 배치를
# 이 크기로 잘라서 여러 번 호출한다(그래도 틱마다 부르는 것보다는 훨씬 적은 호출 수).
MAX_BATCH_SIZE = 20

_FALLBACK_RESULT = DecisionResult(
    switch_to_new_store=False, probability=0.0, reason="LLM 응답 누락 — 보수적으로 미전환 처리"
)


def decide_batch_with_cache(
    client: LLMClient, cache: DecisionCache, requests: list[DecisionRequest]
) -> list[DecisionResult]:
    """캐시에 없는 요청만 모아 배치 호출(들)로 처리하고, 입력 순서대로 반환한다."""
    results: list[DecisionResult | None] = [None] * len(requests)
    misses: list[tuple[int, DecisionRequest]] = []

    for i, request in enumerate(requests):
        cached = cache.get(request)
        if cached is not None:
            results[i] = cached
        else:
            misses.append((i, request))

    for start in range(0, len(misses), MAX_BATCH_SIZE):
        chunk = misses[start : start + MAX_BATCH_SIZE]
        chunk_results = client.decide_batch([request for _, request in chunk])

        for (i, request), result in zip(chunk, chunk_results):
            cache.set(request, result)
            results[i] = result

        # 모델이 요청 수보다 적게 반환한 자리는 죽지 않고 보수적으로 채운다
        for i, request in chunk[len(chunk_results) :]:
            cache.set(request, _FALLBACK_RESULT)
            results[i] = _FALLBACK_RESULT

    return results
