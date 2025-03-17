from collections import defaultdict
import heapq
import math

class Graph:
    """Graph to store locations and find shortest routes efficiently using dynamic travel times."""
    
    def __init__(self):
        self.graph = defaultdict(list)
        self.traffic_data = {}  # Stores dynamic travel times (in minutes or km) for each edge

    def add_edge(self, point1, point2, distance, bidirectional=True):
        """
        Adds an edge between two locations.
        :param point1: Tuple (lat, lon)
        :param point2: Tuple (lat, lon)
        :param distance: Base travel time/distance for the edge (default weight)
        :param bidirectional: If True, adds edge in both directions.
        """
        self.graph[point1].append((point2, distance))
        if bidirectional:
            self.graph[point2].append((point1, distance))
        # Initialize dynamic travel time with the base distance.
        self.traffic_data[(point1, point2)] = distance
        if bidirectional:
            self.traffic_data[(point2, point1)] = distance

    def update_edge_weight(self, point1, point2, new_distance, bidirectional=True):
        """
        Updates the travel time for the edge between point1 and point2 based on real-time traffic data.
        :param new_distance: The updated travel time/distance.
        """
        self.traffic_data[(point1, point2)] = new_distance
        if bidirectional:
            self.traffic_data[(point2, point1)] = new_distance

    def get_edge_weight(self, point1, point2, default_weight):
        """
        Retrieves the dynamic travel time for the edge, if available.
        :param default_weight: Base weight in case no dynamic data exists.
        """
        return self.traffic_data.get((point1, point2), default_weight)

    def heuristic(self, point1, point2):
        """Estimates the distance between two points using the Haversine formula (great-circle distance)."""
        lat1, lon1 = point1
        lat2, lon2 = point2

        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c  # Estimated distance in km

    def a_star(self, start, end):
        """
        Finds the shortest path from start to end using the A* search algorithm.
        Returns a tuple of (path, total_dynamic_cost).
        """
        pq = [(0, start)]  # Priority queue: (estimated total cost, current node)
        g_cost = {node: float('inf') for node in self.graph}  # Cost to reach each node from start
        g_cost[start] = 0
        came_from = {}  # To reconstruct the path

        while pq:
            curr_cost, node = heapq.heappop(pq)
            
            if node == end:
                return self.reconstruct_path(came_from, end), g_cost[end]
            
            for neighbor, base_weight in self.graph[node]:
                # Use updated dynamic weight if available, otherwise fall back to the base weight
                dynamic_weight = self.get_edge_weight(node, neighbor, base_weight)
                new_cost = g_cost[node] + dynamic_weight

                if new_cost < g_cost[neighbor]:
                    g_cost[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, end)
                    heapq.heappush(pq, (priority, neighbor))
                    came_from[neighbor] = node

        return None, float('inf')  # No path found

    def reconstruct_path(self, came_from, current):
        """Reconstructs the path from start to end using the came_from mapping."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
