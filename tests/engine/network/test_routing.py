from engine.network.routing import nearest_node, shortest_path_between


def test_nearest_node_returns_queried_node(graph):
    node_id = next(iter(graph.nodes))
    x, y = graph.nodes[node_id]["x"], graph.nodes[node_id]["y"]

    assert nearest_node(graph, x, y) == node_id


def test_shortest_path_between_two_points(graph):
    nodes = list(graph.nodes)
    orig, dest = nodes[0], nodes[-1]
    orig_x, orig_y = graph.nodes[orig]["x"], graph.nodes[orig]["y"]
    dest_x, dest_y = graph.nodes[dest]["x"], graph.nodes[dest]["y"]

    path = shortest_path_between(graph, orig_x, orig_y, dest_x, dest_y)

    assert path is not None
    assert len(path) > 0
