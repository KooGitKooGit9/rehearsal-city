import networkx as nx

from engine.population.generator import generate_citizens


def _sample_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph()
    g.add_node(1, x=127.03, y=37.54)
    g.add_node(2, x=127.04, y=37.545)
    g.add_node(3, x=127.05, y=37.55)
    return g


def test_generate_citizens_count_and_fields():
    weights = {("MALE", "F20T24"): 3.0, ("FEMALE", "F20T24"): 1.0}
    graph = _sample_graph()

    citizens = generate_citizens(100, weights, graph, seed=1)

    assert len(citizens) == 100
    assert all(c.home_node in graph.nodes for c in citizens)
    assert all((c.gender, c.age_band) in weights for c in citizens)


def test_generate_citizens_deterministic_with_seed():
    weights = {("MALE", "F20T24"): 1.0, ("FEMALE", "F30T34"): 1.0}
    graph = _sample_graph()

    a = generate_citizens(20, weights, graph, seed=7)
    b = generate_citizens(20, weights, graph, seed=7)

    assert a == b
