from engine.decision.models import DecisionRequest
from engine.decision.prompt import build_batch_prompt


def test_prompt_includes_all_citizens_and_key_fields():
    requests = [
        DecisionRequest(
            citizen_id=1,
            gender="FEMALE",
            age_band="F20T24",
            new_store_name="성수 카페",
            new_store_category="cafe",
            distance_to_new_store_m=120.0,
            current_store_category="restaurant",
            distance_to_current_store_m=300.0,
        ),
        DecisionRequest(
            citizen_id=2,
            gender="MALE",
            age_band="F50T54",
            new_store_name="성수 카페",
            new_store_category="cafe",
            distance_to_new_store_m=80.0,
        ),
    ]

    prompt = build_batch_prompt(requests)

    assert "시민 #1" in prompt
    assert "시민 #2" in prompt
    assert "성수 카페" in prompt
    assert "120m" in prompt
    assert "기존에 정기적으로 이용하는 매장 없음" in prompt
    assert "switch_to_new_store" in prompt
