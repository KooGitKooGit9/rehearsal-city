import networkx as nx

from engine.population.models import Citizen
from engine.simulation.clock import TICKS_PER_DAY
from engine.simulation.engine import SimulationEngine
from engine.simulation.state import ACTIVITY_HOME, ACTIVITY_WORK


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
    citizens = []
    for i in range(5):
        home_node = i % 9
        citizens.append(
            Citizen(
                citizen_id=i,
                gender="MALE",
                age_band="F20T24",
                home_node=home_node,
                lon=graph.nodes[home_node]["x"],
                lat=graph.nodes[home_node]["y"],
            )
        )
    return citizens


def _pois(graph: nx.MultiDiGraph) -> list[dict]:
    return [
        {"node": 8, "lon": graph.nodes[8]["x"], "lat": graph.nodes[8]["y"], "name": "가게1"},
        {"node": 4, "lon": graph.nodes[4]["x"], "lat": graph.nodes[4]["y"], "name": "가게2"},
    ]


def test_full_day_cycle_transitions_and_resets():
    graph = _grid_graph()
    engine = SimulationEngine(graph, _citizens(graph), _pois(graph), seed=42)

    seen_activities = set()
    for _ in range(TICKS_PER_DAY):
        engine.step()
        seen_activities.update(s.activity for s in engine.states)

    assert ACTIVITY_WORK in seen_activities
    assert all(s.activity == ACTIVITY_HOME for s in engine.states)
    assert engine.tick == 0


def test_snapshot_structure():
    graph = _grid_graph()
    engine = SimulationEngine(graph, _citizens(graph), _pois(graph), seed=1)

    engine.step()
    snapshot = engine.to_geojson_snapshot()

    assert snapshot["type"] == "FeatureCollection"
    assert len(snapshot["features"]) == 5
    assert "clock" in snapshot

    feature = snapshot["features"][0]
    assert feature["geometry"]["type"] == "Point"
    assert "activity" in feature["properties"]
