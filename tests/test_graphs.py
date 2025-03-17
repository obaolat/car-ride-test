import math
from graphs import Graph

def test_heuristic():
    # Test the Haversine formula between two points
    graph = Graph()
    point1 = (40.7128, -74.0060)  # New York
    point2 = (34.0522, -118.2437) # Los Angeles
    distance = graph.heuristic(point1, point2)
    # Rough distance between New York and LA is ~3940 km
    assert math.isclose(distance, 3940, rel_tol=0.1)

def test_add_and_update_edge():
    graph = Graph()
    point1 = (40.7128, -74.0060)
    point2 = (40.73061, -73.935242)
    base_distance = 10  # Assume 10 minutes
    graph.add_edge(point1, point2, base_distance)
    # Check initial dynamic weight equals base_distance
    assert graph.traffic_data[(point1, point2)] == base_distance

    # Update the traffic data for the edge
    new_distance = 15
    graph.update_edge_weight(point1, point2, new_distance)
    assert graph.traffic_data[(point1, point2)] == new_distance

def test_a_star():
    # Build a small graph to test A* path finding
    graph = Graph()
    A = (0, 0)
    B = (0, 1)
    C = (1, 1)
    # Assume base distances (these could represent minutes or km)
    graph.add_edge(A, B, 5)
    graph.add_edge(B, C, 5)
    # A -> C should be 10 via A-B-C
    path, cost = graph.a_star(A, C)
    assert path == [A, B, C]
    assert cost == 10
