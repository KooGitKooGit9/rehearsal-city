"""도로망 경로를 따라 시민을 이동시킨다."""
from __future__ import annotations

import networkx as nx

from engine.simulation.state import CitizenState

# 도보 평균 속도 약 70m/분 가정 → 10분 틱당 이동 예산(m)
WALK_METERS_PER_TICK = 700.0


def _edge_length(graph: nx.MultiDiGraph, u: int, v: int) -> float:
    return min(data["length"] for data in graph[u][v].values())


def advance_along_path(
    state: CitizenState, graph: nx.MultiDiGraph, meters_budget: float = WALK_METERS_PER_TICK
) -> None:
    """state.path(= [현재 노드, ..., 목적지 노드])를 따라 최대 meters_budget만큼 이동시킨다."""
    while meters_budget > 0 and len(state.path) > 1:
        u, v = state.path[0], state.path[1]
        edge_length = _edge_length(graph, u, v)
        remaining_on_edge = edge_length - state.edge_progress_m

        if meters_budget < remaining_on_edge:
            state.edge_progress_m += meters_budget
            meters_budget = 0
        else:
            meters_budget -= remaining_on_edge
            state.edge_progress_m = 0.0
            state.node = v
            state.path.pop(0)

    if len(state.path) > 1:
        u, v = state.path[0], state.path[1]
        edge_length = _edge_length(graph, u, v)
        frac = state.edge_progress_m / edge_length if edge_length > 0 else 0.0
        ux, uy = graph.nodes[u]["x"], graph.nodes[u]["y"]
        vx, vy = graph.nodes[v]["x"], graph.nodes[v]["y"]
        state.lon = ux + (vx - ux) * frac
        state.lat = uy + (vy - uy) * frac
    else:
        state.lon = graph.nodes[state.node]["x"]
        state.lat = graph.nodes[state.node]["y"]
