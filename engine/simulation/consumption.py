"""규칙 기반 소비 선택 — 가까운 매장 후보 중 확률적으로 하나를 고른다."""
from __future__ import annotations

import math
import random

NEAREST_CANDIDATE_COUNT = 5


def _distance(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    return math.hypot(lon2 - lon1, lat2 - lat1)


def pick_store(
    current_lon: float, current_lat: float, pois: list[dict], rng: random.Random
) -> tuple[int, float, float]:
    """현재 위치에서 가까운 후보 상위 N곳 중 무작위로 하나를 선택한다."""
    ranked = sorted(pois, key=lambda p: _distance(current_lon, current_lat, p["lon"], p["lat"]))
    candidates = ranked[:NEAREST_CANDIDATE_COUNT]
    chosen = rng.choice(candidates)
    return chosen["node"], chosen["lon"], chosen["lat"]
