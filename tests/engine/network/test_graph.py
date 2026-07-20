import networkx as nx

from engine.config import DEMO_REGION


def test_graph_has_nodes_and_edges(graph):
    assert isinstance(graph, nx.MultiDiGraph)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0


def test_cache_file_created(graph):
    assert DEMO_REGION.cache_path.exists()
