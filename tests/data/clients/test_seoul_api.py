"""서울 열린데이터광장 공통 클라이언트 테스트 (실제 네트워크 호출 없음)."""
import json
from pathlib import Path

import pytest

from data.clients import seoul_api

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures" / "spop_local_resd_dong_sample.json").read_text()
)


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_fetch_all_single_page(monkeypatch):
    monkeypatch.setattr(seoul_api.requests, "get", lambda url, timeout: FakeResponse(FIXTURE))

    rows = seoul_api.fetch_all("SPOP_LOCAL_RESD_DONG", extra_args=("20260716",))

    assert len(rows) == 3


def test_fetch_all_paginates_until_total_reached(monkeypatch):
    page1 = {
        "SPOP_LOCAL_RESD_DONG": {
            "list_total_count": 2,
            "RESULT": {"CODE": "INFO-000", "MESSAGE": "정상 처리되었습니다"},
            "row": [{"ADSTRD_CODE_SE": "11200610"}],
        }
    }
    page2 = {
        "SPOP_LOCAL_RESD_DONG": {
            "list_total_count": 2,
            "RESULT": {"CODE": "INFO-000", "MESSAGE": "정상 처리되었습니다"},
            "row": [{"ADSTRD_CODE_SE": "11200620"}],
        }
    }
    responses = iter([page1, page2])
    monkeypatch.setattr(seoul_api, "PAGE_SIZE", 1)
    monkeypatch.setattr(seoul_api.requests, "get", lambda url, timeout: FakeResponse(next(responses)))

    rows = seoul_api.fetch_all("SPOP_LOCAL_RESD_DONG")

    assert len(rows) == 2


def test_fetch_all_raises_on_error_code(monkeypatch):
    error_payload = {
        "SPOP_LOCAL_RESD_DONG": {
            "RESULT": {"CODE": "ERROR-336", "MESSAGE": "일별 트래픽 제한을 초과하였습니다."},
        }
    }
    monkeypatch.setattr(seoul_api.requests, "get", lambda url, timeout: FakeResponse(error_payload))

    with pytest.raises(seoul_api.SeoulApiError):
        seoul_api.fetch_all("SPOP_LOCAL_RESD_DONG")
