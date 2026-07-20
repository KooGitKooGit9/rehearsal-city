import random

import networkx as nx

from engine.population.models import Citizen
from engine.simulation.clock import TICKS_PER_DAY
from engine.simulation.scheduler import DailySchedule, decide_activity, generate_schedule
from engine.simulation.state import (
    ACTIVITY_COMMUTING,
    ACTIVITY_HOME,
    ACTIVITY_LEISURE,
    ACTIVITY_RETURNING,
    ACTIVITY_WORK,
    CitizenState,
)


def _cycle_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    coords = {1: (0.0, 0.0), 2: (1.0, 0.0), 3: (1.0, 1.0), 4: (0.0, 1.0)}
    for node, (x, y) in coords.items():
        g.add_node(node, x=x, y=y)
    ring = [1, 2, 3, 4, 1]
    for u, v in zip(ring, ring[1:]):
        g.add_edge(u, v, length=100.0)
        g.add_edge(v, u, length=100.0)
    return g


def _state(activity: str, path: list[int], node: int = 1) -> CitizenState:
    citizen = Citizen(citizen_id=0, gender="MALE", age_band="F20T24", home_node=1, lon=0.0, lat=0.0)
    state = CitizenState.at_home(citizen)
    state.activity = activity
    state.path = path
    state.node = node
    return state


def _stub_pick_store(lon, lat, rng):
    return 3, 1.0, 1.0


def test_generate_schedule_valid_ranges():
    graph = _cycle_graph()
    schedule = generate_schedule(home_node=1, graph=graph, rng=random.Random(1))

    assert 0 <= schedule.leave_home_tick < schedule.leave_work_tick < TICKS_PER_DAY
    assert schedule.workplace_node != 1
    assert schedule.workplace_node in graph.nodes


def test_generate_schedule_deterministic_with_seed():
    graph = _cycle_graph()
    a = generate_schedule(home_node=1, graph=graph, rng=random.Random(5))
    b = generate_schedule(home_node=1, graph=graph, rng=random.Random(5))
    assert a == b


def test_home_to_commuting_at_scheduled_tick():
    graph = _cycle_graph()
    schedule = DailySchedule(leave_home_tick=48, leave_work_tick=108, workplace_node=3, has_leisure_stop=False)
    state = _state(ACTIVITY_HOME, path=[])

    decide_activity(state, schedule, tick=48, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))

    assert state.activity == ACTIVITY_COMMUTING
    assert state.path[0] == 1
    assert state.path[-1] == 3


def test_commuting_to_work_on_arrival():
    graph = _cycle_graph()
    schedule = DailySchedule(leave_home_tick=48, leave_work_tick=108, workplace_node=3, has_leisure_stop=False)
    state = _state(ACTIVITY_COMMUTING, path=[3], node=3)

    decide_activity(state, schedule, tick=50, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))

    assert state.activity == ACTIVITY_WORK


def test_work_to_returning_without_leisure():
    graph = _cycle_graph()
    schedule = DailySchedule(leave_home_tick=48, leave_work_tick=108, workplace_node=3, has_leisure_stop=False)
    state = _state(ACTIVITY_WORK, path=[3], node=3)

    decide_activity(state, schedule, tick=108, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))

    assert state.activity == ACTIVITY_RETURNING
    assert state.path[-1] == state.citizen.home_node


def test_work_to_leisure_with_stop():
    graph = _cycle_graph()
    schedule = DailySchedule(leave_home_tick=48, leave_work_tick=108, workplace_node=3, has_leisure_stop=True)
    state = _state(ACTIVITY_WORK, path=[3], node=3)

    decide_activity(state, schedule, tick=108, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))

    assert state.activity == ACTIVITY_LEISURE
    assert state.dwell_remaining > 0
    assert state.path[-1] == 3


def test_leisure_dwell_then_returning():
    graph = _cycle_graph()
    schedule = DailySchedule(leave_home_tick=48, leave_work_tick=108, workplace_node=3, has_leisure_stop=True)
    state = _state(ACTIVITY_LEISURE, path=[3], node=3)
    state.dwell_remaining = 1

    decide_activity(state, schedule, tick=110, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))
    assert state.activity == ACTIVITY_LEISURE
    assert state.dwell_remaining == 0

    decide_activity(state, schedule, tick=111, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))
    assert state.activity == ACTIVITY_RETURNING


def test_returning_to_home():
    graph = _cycle_graph()
    schedule = DailySchedule(leave_home_tick=48, leave_work_tick=108, workplace_node=3, has_leisure_stop=False)
    state = _state(ACTIVITY_RETURNING, path=[1], node=1)

    decide_activity(state, schedule, tick=120, graph=graph, pick_store=_stub_pick_store, rng=random.Random(0))

    assert state.activity == ACTIVITY_HOME
