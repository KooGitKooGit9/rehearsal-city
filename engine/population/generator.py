"""통계 분포 기반 합성 시민 생성.

개별 시민의 정확성을 주장하지 않는다 — 목표는 집단 수준 재현이다 (docs/DECISIONS.md D2).
"""
from __future__ import annotations

import random

import networkx as nx

from engine.population.models import Citizen


def generate_citizens(
    n: int,
    age_gender_weights: dict[tuple[str, str], float],
    graph: nx.MultiDiGraph,
    seed: int | None = None,
) -> list[Citizen]:
    rng = random.Random(seed)
    categories = list(age_gender_weights.keys())
    weights = list(age_gender_weights.values())
    nodes = list(graph.nodes)

    citizens = []
    for citizen_id in range(n):
        gender, age_band = rng.choices(categories, weights=weights, k=1)[0]
        home_node = rng.choice(nodes)
        lon = graph.nodes[home_node]["x"]
        lat = graph.nodes[home_node]["y"]
        citizens.append(
            Citizen(
                citizen_id=citizen_id,
                gender=gender,
                age_band=age_band,
                home_node=home_node,
                lon=lon,
                lat=lat,
            )
        )
    return citizens
