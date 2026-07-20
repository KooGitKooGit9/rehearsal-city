"""생활인구(행정동 단위) 수집 CLI.

실행: python -m data.collect_living_population [YYYYMMDD]
인자를 생략하면 기본값(5일 전)을 사용한다.
"""
from __future__ import annotations

import sys

from data.collectors.living_population import fetch_living_population_dong
from data.db import init_db
from data.load import upsert_living_population


def main() -> None:
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None

    print("생활인구(행정동 단위) 조회 중...")
    rows = fetch_living_population_dong(date_arg)
    print(f"성동구 필터링 후 {len(rows)}건 확보")

    init_db()
    loaded = upsert_living_population(rows)
    print(f"{loaded}건 적재 완료")


if __name__ == "__main__":
    main()
