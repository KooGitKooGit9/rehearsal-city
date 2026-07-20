import networkx as nx

from engine.decision.client import LLMClient
from engine.decision.models import DecisionRequest, DecisionResult
from engine.population.models import Citizen
from engine.whatif.models import NewStoreSpec, WhatIfReport
from engine.whatif.service import _build_report, run_whatif


class FakeLLMClient(LLMClient):
    def __init__(self, switch: bool) -> None:
        self.switch = switch

    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        return [
            DecisionResult(switch_to_new_store=self.switch, probability=0.8, reason="test")
            for _ in requests
        ]


class FakeEngine:
    """_build_report는 visit_log/switch_log만 읽으므로 실제 엔진 없이 스텁으로 검증한다."""

    def __init__(self, visit_log, switch_log):
        self.visit_log = visit_log
        self.switch_log = switch_log


def test_build_report_aggregates_visits_and_switches():
    engine = FakeEngine(
        visit_log=[(99, 5), (99, 150), (8, 10), (99, 300)],
        switch_log=[
            {"citizen_id": 1, "from_store": "가게1", "tick": 5},
            {"citizen_id": 2, "from_store": "가게1", "tick": 20},
        ],
    )

    report = _build_report(engine, new_store_node=99, days=7)

    assert report.daily_average_visits == 3 / 7
    assert report.switched_citizens == 2
    assert report.source_breakdown == {"가게1": 2}
    assert report.hourly_distribution == {0: 1, 1: 1, 2: 1}


def _node_id(i: int, j: int) -> int:
    return i * 3 + j


def _grid_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph(crs="EPSG:4326")
    for i in range(3):
        for j in range(3):
            g.add_node(_node_id(i, j), x=i * 0.001, y=j * 0.001)
    for i in range(3):
        for j in range(3):
            if i < 2:
                g.add_edge(_node_id(i, j), _node_id(i + 1, j), length=100.0)
                g.add_edge(_node_id(i + 1, j), _node_id(i, j), length=100.0)
            if j < 2:
                g.add_edge(_node_id(i, j), _node_id(i, j + 1), length=100.0)
                g.add_edge(_node_id(i, j + 1), _node_id(i, j), length=100.0)
    return g


def _citizens(graph: nx.MultiDiGraph) -> list[Citizen]:
    return [
        Citizen(
            citizen_id=i,
            gender="MALE",
            age_band="F20T24",
            home_node=i % 9,
            lon=graph.nodes[i % 9]["x"],
            lat=graph.nodes[i % 9]["y"],
        )
        for i in range(5)
    ]


def _pois(graph: nx.MultiDiGraph) -> list[dict]:
    return [
        {"node": 8, "lon": graph.nodes[8]["x"], "lat": graph.nodes[8]["y"], "name": "가게1", "category": "cafe"},
        {"node": 4, "lon": graph.nodes[4]["x"], "lat": graph.nodes[4]["y"], "name": "가게2", "category": "restaurant"},
    ]


def test_run_whatif_returns_well_formed_report():
    graph = _grid_graph()
    new_store = NewStoreSpec(
        lon=graph.nodes[1]["x"], lat=graph.nodes[1]["y"], name="신규 카페", category="cafe"
    )

    report = run_whatif(
        graph, _citizens(graph), _pois(graph), new_store, FakeLLMClient(switch=True), days=2, seed=3
    )

    assert isinstance(report, WhatIfReport)
    assert report.daily_average_visits >= 0
    assert report.switched_citizens >= 0
    assert isinstance(report.source_breakdown, dict)
    assert isinstance(report.hourly_distribution, dict)
