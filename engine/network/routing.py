"""좌표 기반 최단경로 탐색."""
from __future__ import annotations

import networkx as nx
import osmnx as ox


def nearest_node(graph: nx.MultiDiGraph, lon: float, lat: float) -> int:
    return ox.distance.nearest_nodes(graph, lon, lat)


def shortest_path_between(
    graph: nx.MultiDiGraph,
    orig_lon: float,
    orig_lat: float,
    dest_lon: float,
    dest_lat: float,
) -> list[int] | None:
    orig_node = nearest_node(graph, orig_lon, orig_lat)
    dest_node = nearest_node(graph, dest_lon, dest_lat)
    return ox.shortest_path(graph, orig_node, dest_node, weight="length")
