import networkx as nx

from engine.decision.cache import DecisionCache
from engine.decision.client import LLMClient
from engine.decision.models import DecisionRequest, DecisionResult
from engine.population.models import Citizen
from engine.simulation.clock import TICKS_PER_DAY
from engine.simulation.engine import SimulationEngine
from engine.simulation.scheduler import DailySchedule
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
        {"node": 8, "lon": graph.nodes[8]["x"], "lat": graph.nodes[8]["y"], "name": "가게1", "category": "cafe"},
        {"node": 4, "lon": graph.nodes[4]["x"], "lat": graph.nodes[4]["y"], "name": "가게2", "category": "restaurant"},
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


class FakeLLMClient(LLMClient):
    def __init__(self, switch: bool) -> None:
        self.switch = switch
        self.calls: list[list[DecisionRequest]] = []

    def decide_batch(self, requests: list[DecisionRequest]) -> list[DecisionResult]:
        self.calls.append(requests)
        return [
            DecisionResult(switch_to_new_store=self.switch, probability=0.9, reason="test")
            for _ in requests
        ]


def _new_store_at_node(graph: nx.MultiDiGraph, node: int) -> dict:
    return {
        "node": node,
        "lon": graph.nodes[node]["x"],
        "lat": graph.nodes[node]["y"],
        "name": "신규 카페",
        "category": "cafe",
    }


def test_turning_point_switches_habitual_store_when_llm_approves():
    graph = _grid_graph()
    citizens = _citizens(graph)
    llm_client = FakeLLMClient(switch=True)
    new_store = _new_store_at_node(graph, 1)  # 기존 POI(노드 8, 4)와 겹치지 않는 노드
    engine = SimulationEngine(graph, citizens, _pois(graph), seed=1, new_store=new_store, llm_client=llm_client)
    # 생성 시점엔 아무도 단골이 없어 위 생성자 호출은 실질적으로 아무 일도 하지 않았다(0건 판단).

    state = engine.states[0]
    state.habitual_store_node = 8  # 이미 단골이 있는 상태
    engine.schedules[0] = DailySchedule(
        leave_home_tick=0, leave_work_tick=0, workplace_node=1, has_leisure_stop=True
    )

    # 하루 시작 시점에 그날 여가 방문 예정자를 한 번에 배치 판단한다(틱마다가 아니라)
    engine._process_daily_turning_points()

    assert len(llm_client.calls) == 1
    assert len(llm_client.calls[0]) == 1
    assert state.habitual_store_node == 1
    assert 1 in state.decided_new_stores
    assert engine.switch_log == [{"citizen_id": state.citizen.citizen_id, "from_store": "가게1", "tick": 0}]


def test_turning_point_keeps_habitual_store_when_llm_declines():
    graph = _grid_graph()
    citizens = _citizens(graph)
    llm_client = FakeLLMClient(switch=False)
    new_store = _new_store_at_node(graph, 1)
    engine = SimulationEngine(graph, citizens, _pois(graph), seed=1, new_store=new_store, llm_client=llm_client)

    state = engine.states[0]
    state.habitual_store_node = 8
    engine.schedules[0] = DailySchedule(
        leave_home_tick=0, leave_work_tick=0, workplace_node=1, has_leisure_stop=True
    )

    engine._process_daily_turning_points()

    assert state.habitual_store_node == 8  # 전환 안 함
    assert 1 in state.decided_new_stores  # 그래도 "판단은 했다"는 기록은 남음
    assert engine.switch_log == []


def test_turning_point_llm_called_only_once_per_citizen_per_new_store():
    graph = _grid_graph()
    citizens = _citizens(graph)
    llm_client = FakeLLMClient(switch=False)
    new_store = _new_store_at_node(graph, 1)
    engine = SimulationEngine(graph, citizens, _pois(graph), seed=1, new_store=new_store, llm_client=llm_client)

    state = engine.states[0]
    state.habitual_store_node = 8
    engine.schedules[0] = DailySchedule(
        leave_home_tick=0, leave_work_tick=0, workplace_node=1, has_leisure_stop=True
    )

    engine._process_daily_turning_points()
    # 다음 날이 되어(스케줄이 다시 여가 방문 예정으로) 다시 검사 대상이 되어도
    # 이미 판단을 마쳤으므로 LLM을 다시 호출하지 않아야 한다
    engine.schedules[0] = DailySchedule(
        leave_home_tick=0, leave_work_tick=0, workplace_node=1, has_leisure_stop=True
    )
    engine._process_daily_turning_points()

    assert len(llm_client.calls) == 1
