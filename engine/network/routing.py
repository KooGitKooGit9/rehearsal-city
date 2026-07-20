"""좌표 기반 최단경로 탐색."""
from __future__ import annotations

import networkx as nx
import osmnx as ox


def nearest_node(graph: nx.MultiDiGraph, lon: float, lat: float) -> int:
    return ox.distance.nearest_nodes(graph, lon, lat)


def shortest_path_between_nodes(graph: nx.MultiDiGraph, orig_node: int, dest_node: int) -> list[int] | None:
    return ox.shortest_path(graph, orig_node, dest_node, weight="length")


def path_length_m(graph: nx.MultiDiGraph, orig_node: int, dest_node: int) -> float | None:
    """두 노드 사이의 실제 도보 거리(m). 경로가 없으면 None."""
    try:
        return nx.shortest_path_length(graph, orig_node, dest_node, weight="length")
    except nx.NetworkXNoPath:
        return None


def shortest_path_between(
    graph: nx.MultiDiGraph,
    orig_lon: float,
    orig_lat: float,
    dest_lon: float,
    dest_lat: float,
) -> list[int] | None:
    orig_node = nearest_node(graph, orig_lon, orig_lat)
    dest_node = nearest_node(graph, dest_lon, dest_lat)
    return shortest_path_between_nodes(graph, orig_node, dest_node)
