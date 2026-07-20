import networkx as nx

from engine.simulation.poi import attach_nearest_nodes


def _sample_graph() -> nx.MultiDiGraph:
    g = nx.MultiDiGraph(crs="EPSG:4326")
    g.add_node(1, x=0.0, y=0.0)
    g.add_node(2, x=1.0, y=0.0)
    return g


def test_attach_nearest_nodes_maps_to_closest_graph_node():
    raw = [
        {"lon": 0.01, "lat": 0.01, "name": "카페 A", "category": "cafe"},
        {"lon": 0.99, "lat": 0.0, "name": None, "category": "unknown"},
    ]

    result = attach_nearest_nodes(raw, _sample_graph())

    assert result[0]["node"] == 1
    assert result[1]["node"] == 2
    assert result[0]["name"] == "카페 A"
    assert result[0]["category"] == "cafe"
