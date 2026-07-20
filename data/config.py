"""데이터 수집 계층 설정. .env에서 시크릿과 DB 접속정보를 읽는다."""
from __future__ import annotations

import os
from datetime import date, timedelta

from dotenv import load_dotenv

load_dotenv()

SEOUL_OPENDATA_API_KEY = os.environ.get("SEOUL_OPENDATA_API_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

SEOUL_API_BASE_URL = "http://openapi.seoul.go.kr:8088"

# 생활인구(행정동 단위) 서비스명 (data.seoul.go.kr OA-14991, Open API 탭에서 확인)
LIVING_POPULATION_DONG_SERVICE = "SPOP_LOCAL_RESD_DONG"

# 성동구 자치구코드. 행정동코드는 이 값으로 시작한다 (docs/DATA.md 참고).
# API가 자치구 단위 prefix 필터를 지원하지 않아 전체 조회 후 이 값으로 클라이언트에서 걸러낸다.
SEONGDONG_GU_CODE = "11200"

# 생활인구는 최신 데이터 생성까지 약 5일 지연됨 (데이터셋 페이지 공지 기준)
LIVING_POPULATION_LAG_DAYS = 5


def default_living_population_date() -> str:
    return (date.today() - timedelta(days=LIVING_POPULATION_LAG_DAYS)).strftime("%Y%m%d")
