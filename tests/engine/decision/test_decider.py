from engine.decision.cache import DecisionCache
from engine.decision.client import LLMClient
from engine.decision.decider import decide_batch_with_cache
from engine.decision.models import DecisionRequest, DecisionResult


class FakeLLMClient(LLMClient):
    """실제 API 호출 없이 배치 크기를 기록하는 테스트용 가짜 클라이언트."""

    def __init__(self) -> None:
        self.calls: list[list[DecisionRequest]] = []

    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        self.calls.append(requests)
        return [
            DecisionResult(switch_to_new_store=True, probability=0.5, reason=f"fake-{r.citizen_id}")
            for r in requests
        ]


def _request(citizen_id: int) -> DecisionRequest:
    return DecisionRequest(
        citizen_id=citizen_id,
        gender="MALE",
        age_band="F30T34",
        new_store_name="테스트 카페",
        new_store_category="cafe",
        distance_to_new_store_m=100.0,
    )


def test_first_call_hits_llm_for_all_misses():
    client = FakeLLMClient()
    cache = DecisionCache()
    requests = [_request(1), _request(2)]

    results = decide_batch_with_cache(client, cache, requests)

    assert len(client.calls) == 1
    assert len(client.calls[0]) == 2
    assert all(isinstance(r, DecisionResult) for r in results)


def test_second_call_with_same_profile_uses_cache_not_llm():
    client = FakeLLMClient()
    cache = DecisionCache()

    decide_batch_with_cache(client, cache, [_request(1)])
    decide_batch_with_cache(client, cache, [_request(2)])  # 같은 프로파일, 다른 citizen_id

    assert len(client.calls) == 1  # 두 번째 호출은 캐시로 해결, LLM 미호출


def test_mixed_hit_and_miss_preserves_order():
    client = FakeLLMClient()
    cache = DecisionCache()

    [known_result] = decide_batch_with_cache(client, cache, [_request(1)])

    new_request = DecisionRequest(
        citizen_id=99,
        gender="FEMALE",
        age_band="F40T44",
        new_store_name="다른 매장",
        new_store_category="restaurant",
        distance_to_new_store_m=500.0,
    )
    results = decide_batch_with_cache(client, cache, [_request(2), new_request])

    assert results[0] == known_result  # 캐시 히트, 순서 유지
    assert results[1].reason == "fake-99"  # 캐시 미스 -> LLM 호출 결과
    assert len(client.calls) == 2
    assert len(client.calls[1]) == 1  # 미스 1건만 배치에 포함됨


class ShortFakeLLMClient(LLMClient):
    """실제로 겪은 문제를 재현 — 요청보다 적은 개수의 결과를 반환하는 가짜 클라이언트."""

    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        return [
            DecisionResult(switch_to_new_store=True, probability=0.5, reason=f"fake-{r.citizen_id}")
            for r in requests[:-1]
        ]


def _unique_request(citizen_id: int) -> DecisionRequest:
    # 프로파일 캐시가 재사용되지 않도록 시민마다 다른 거리 구간을 준다
    return DecisionRequest(
        citizen_id=citizen_id,
        gender="MALE",
        age_band="F30T34",
        new_store_name="테스트 카페",
        new_store_category="cafe",
        distance_to_new_store_m=100.0 * citizen_id,
    )


def test_missing_llm_response_falls_back_conservatively_instead_of_crashing():
    client = ShortFakeLLMClient()
    cache = DecisionCache()
    requests = [_unique_request(i) for i in range(3)]

    results = decide_batch_with_cache(client, cache, requests)

    assert len(results) == 3
    assert all(r is not None for r in results)
    assert results[-1].switch_to_new_store is False  # 응답 누락분은 보수적으로 미전환 처리


def test_large_batch_is_split_into_chunks():
    client = FakeLLMClient()
    cache = DecisionCache()
    requests = [_unique_request(i) for i in range(45)]  # MAX_BATCH_SIZE(20)의 배수가 아님

    results = decide_batch_with_cache(client, cache, requests)

    assert len(results) == 45
    assert [len(c) for c in client.calls] == [20, 20, 5]
