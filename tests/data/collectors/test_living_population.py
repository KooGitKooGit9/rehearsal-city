"""생활인구(행정동 단위) 수집기 테스트."""
import json
from pathlib import Path

from data.collectors import living_population

FIXTURE_ROWS = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "spop_local_resd_dong_sample.json").read_text()
)["SPOP_LOCAL_RESD_DONG"]["row"]


def test_filters_to_seongdong_gu_only(monkeypatch):
    monkeypatch.setattr(living_population, "fetch_all", lambda service, extra_args=(): FIXTURE_ROWS)

    rows = living_population.fetch_living_population_dong("20260716")

    assert len(rows) == 2
    assert all(row["ADSTRD_CODE_SE"].startswith("11200") for row in rows)
