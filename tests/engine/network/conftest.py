import pytest

from engine.network.graph import load_or_build_graph


@pytest.fixture(scope="session")
def graph():
    """세션당 1회만 로드. 캐시가 없으면 최초 실행 시 Overpass API를 호출한다."""
    return load_or_build_graph()
