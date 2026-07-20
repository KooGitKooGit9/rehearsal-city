import networkx as nx

from engine.population.models import Citizen
from engine.simulation.movement import advance_along_path
from engine.simulation.state import CitizenState


def _line_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    g.add_node(1, x=0.0, y=0.0)
    g.add_node(2, x=1.0, y=0.0)
    g.add_node(3, x=2.0, y=0.0)
    g.add_edge(1, 2, length=500.0)
    g.add_edge(2, 3, length=500.0)
    return g


def _citizen_state(path: list[int]) -> CitizenState:
    citizen = Citizen(citizen_id=0, gender="MALE", age_band="F20T24", home_node=1, lon=0.0, lat=0.0)
    state = CitizenState.at_home(citizen)
    state.path = path
    return state


def test_partial_move_stays_on_first_edge():
    state = _citizen_state([1, 2, 3])

    advance_along_path(state, _line_graph(), meters_budget=300.0)

    assert state.node == 1
    assert state.path == [1, 2, 3]
    assert state.edge_progress_m == 300.0
    assert 0.0 < state.lon < 1.0


def test_full_move_reaches_destination():
    state = _citizen_state([1, 2, 3])

    advance_along_path(state, _line_graph(), meters_budget=1000.0)

    assert state.node == 3
    assert state.path == [3]
    assert state.lon == 2.0


def test_arrived_state_does_not_move_further():
    state = _citizen_state([3])
    state.node = 3

    advance_along_path(state, _line_graph(), meters_budget=700.0)

    assert state.node == 3
    assert state.lon == 2.0
