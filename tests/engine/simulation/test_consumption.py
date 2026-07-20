import random

from engine.simulation.consumption import pick_store

POIS = [
    {"node": 1, "lon": 0.001, "lat": 0.0, "name": "가장 가까움"},
    {"node": 2, "lon": 0.002, "lat": 0.0, "name": "두번째"},
    {"node": 3, "lon": 0.003, "lat": 0.0, "name": "세번째"},
    {"node": 4, "lon": 0.004, "lat": 0.0, "name": "네번째"},
    {"node": 5, "lon": 0.005, "lat": 0.0, "name": "다섯번째"},
    {"node": 6, "lon": 10.0, "lat": 10.0, "name": "아주 멀리"},
]


def test_pick_store_only_chooses_among_nearest_candidates():
    rng = random.Random(0)

    for _ in range(50):
        node, lon, lat = pick_store(0.0, 0.0, POIS, rng)
        assert node != 6


def test_pick_store_deterministic_with_seed():
    a = pick_store(0.0, 0.0, POIS, random.Random(3))
    b = pick_store(0.0, 0.0, POIS, random.Random(3))
    assert a == b
