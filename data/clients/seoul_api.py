"""서울 열린데이터광장 Open API 공통 클라이언트.

URL 패턴: {BASE_URL}/{인증키}/{TYPE}/{서비스명}/{시작위치}/{종료위치}/[추가인자...]
"""
from __future__ import annotations

import requests

from data.config import SEOUL_API_BASE_URL, SEOUL_OPENDATA_API_KEY

PAGE_SIZE = 1000


class SeoulApiError(RuntimeError):
    pass


def _fetch_page(service: str, start_index: int, end_index: int, extra_args: tuple[str, ...]) -> dict:
    path_parts = [
        SEOUL_API_BASE_URL,
        SEOUL_OPENDATA_API_KEY,
        "json",
        service,
        str(start_index),
        str(end_index),
        *extra_args,
    ]
    url = "/".join(path_parts)

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()[service]

    result = payload["RESULT"]
    if not result["CODE"].startswith("INFO"):
        raise SeoulApiError(f"{service} 요청 실패: {result['CODE']} {result['MESSAGE']}")

    return payload


def fetch_all(service: str, extra_args: tuple[str, ...] = ()) -> list[dict]:
    """페이징을 순회하며 전체 행을 수집한다."""
    rows: list[dict] = []
    start_index = 1
    total_count: int | None = None

    while total_count is None or start_index <= total_count:
        end_index = start_index + PAGE_SIZE - 1
        payload = _fetch_page(service, start_index, end_index, extra_args)
        total_count = int(payload["list_total_count"])
        rows.extend(payload.get("row", []))
        start_index += PAGE_SIZE

    return rows
