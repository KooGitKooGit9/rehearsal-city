from engine.decision.cache import DecisionCache
from engine.decision.models import DecisionRequest, DecisionResult


def _request(citizen_id: int, distance: float) -> DecisionRequest:
    return DecisionRequest(
        citizen_id=citizen_id,
        gender="FEMALE",
        age_band="F20T24",
        new_store_name="테스트 카페",
        new_store_category="cafe",
        distance_to_new_store_m=distance,
        current_store_category="restaurant",
        distance_to_current_store_m=200.0,
    )


def test_cache_miss_returns_none():
    cache = DecisionCache()
    assert cache.get(_request(1, 50.0)) is None


def test_similar_profiles_share_cache_entry():
    cache = DecisionCache()
    result = DecisionResult(switch_to_new_store=True, probability=0.7, reason="가까움")

    cache.set(_request(1, 55.0), result)

    # 다른 시민(citizen_id 다름)이라도 성별·연령대·거리 구간·매장 유형이 같으면 캐시 재사용
    assert cache.get(_request(2, 61.0)) == result


def test_different_distance_bucket_is_cache_miss():
    cache = DecisionCache()
    result = DecisionResult(switch_to_new_store=True, probability=0.7, reason="가까움")

    cache.set(_request(1, 55.0), result)

    assert cache.get(_request(2, 900.0)) is None
