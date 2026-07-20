"""OSM POI(카페·음식점 등) 수집 — 소비 모델의 매장 후보.

상권분석·상가정보 API는 docs/DATA.md에서 백테스트 단계로 이연했다. 여기서는
"방문할 매장이 실제로 존재한다" 정도의 근사치로 OSMnx POI를 그대로 사용한다.
"""
from __future__ import annotations

import json

import networkx as nx
import osmnx as ox

from engine.config import RegionConfig
from engine.network.routing import nearest_node

POI_TAGS = {
    "amenity": ["cafe", "restaurant", "fast_food"],
    "shop": ["convenience", "supermarket"],
}


def attach_nearest_nodes(raw_pois: list[dict], graph: nx.MultiDiGraph) -> list[dict]:
    """[{"lon","lat","name"}, ...] 원자료에 최근접 그래프 노드를 붙인다 (순수 함수, 테스트 용이)."""
    return [
        {
            "node": nearest_node(graph, item["lon"], item["lat"]),
            "lon": item["lon"],
            "lat": item["lat"],
            "name": item["name"],
        }
        for item in raw_pois
    ]


def _raw_pois_from_cache_or_fetch(region: RegionConfig) -> list[dict]:
    cache_path = region.pois_path
    if cache_path.exists():
        return json.loads(cache_path.read_text())

    gdf = ox.features_from_place(region.place_query, tags=POI_TAGS)
    raw = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom.geom_type != "Point":
            continue
        name = row.get("name")
        raw.append({"lon": geom.x, "lat": geom.y, "name": name if isinstance(name, str) else None})

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(raw, ensure_ascii=False))
    return raw


def load_or_build_pois(region: RegionConfig, graph: nx.MultiDiGraph) -> list[dict]:
    return attach_nearest_nodes(_raw_pois_from_cache_or_fetch(region), graph)
