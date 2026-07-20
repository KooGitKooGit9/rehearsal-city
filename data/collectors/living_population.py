"""생활인구(행정동 단위) 수집."""
from __future__ import annotations

from data.clients.seoul_api import fetch_all
from data.config import (
    LIVING_POPULATION_DONG_SERVICE,
    SEONGDONG_GU_CODE,
    default_living_population_date,
)


def fetch_living_population_dong(stdr_de_id: str | None = None) -> list[dict]:
    """지정한 날짜(YYYYMMDD, 기본값=5일 전)의 성동구 행정동별 생활인구를 가져온다.

    API가 ADSTRD_CODE_SE의 접두어 필터를 지원하지 않아, 서울 전체를 조회한 뒤
    성동구 자치구코드(11200)로 시작하는 행만 걸러낸다.
    """
    date_str = stdr_de_id or default_living_population_date()
    rows = fetch_all(LIVING_POPULATION_DONG_SERVICE, extra_args=(date_str,))
    return [row for row in rows if row["ADSTRD_CODE_SE"].startswith(SEONGDONG_GU_CODE)]
