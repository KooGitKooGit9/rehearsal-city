"""OSMnx 도로망 그래프 로드와 로컬 캐싱."""
from __future__ import annotations

import networkx as nx
import osmnx as ox

from engine.config import DEMO_REGION, RegionConfig


def load_or_build_graph(region: RegionConfig = DEMO_REGION) -> nx.MultiDiGraph:
    """캐시가 있으면 로드하고, 없으면 Overpass API로 받아온 뒤 캐시에 저장한다.

    최초 fetch는 지역 규모에 따라 수십 초~수 분 걸릴 수 있다 (성수동 기준 약 195초 확인됨).
    """
    cache_path = region.cache_path
    if cache_path.exists():
        return ox.load_graphml(cache_path)

    graph = ox.graph_from_place(region.place_query, network_type=region.network_type)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, cache_path)
    return graph
