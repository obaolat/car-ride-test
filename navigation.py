# navigation.py
import osrm
from typing import List, Tuple

def get_route(start: Tuple[float, float], end: Tuple[float, float]) -> dict:
    """
    Fetches the optimal route between start and end coordinates using OSRM.

    Args:
        start (Tuple[float, float]): Starting coordinates (longitude, latitude).
        end (Tuple[float, float]): Ending coordinates (longitude, latitude).

    Returns:
        dict: Route information including distance and duration.
    """
    coords = [start, end]
    response = osrm.route(coordinates=coords, overview='full', steps=True)
    route = response.get('routes', [])[0]
    return route

def calculate_optimal_route(driver_location: Tuple[float, float], passenger_pickup: Tuple[float, float], passenger_dropoff: Tuple[float, float]) -> dict:
    """
    Determines the optimal route for a ride, including pickup and dropoff points.

    Args:
        driver_location (Tuple[float, float]): Driver's current location (longitude, latitude).
        passenger_pickup (Tuple[float, float]): Passenger's pickup location (longitude, latitude).
        passenger_dropoff (Tuple[float, float]): Passenger's dropoff location (longitude, latitude).

    Returns:
        dict: Optimal route details including distance and duration.
    """
    # Route from driver to passenger pickup
    to_pickup_route = get_route(driver_location, passenger_pickup)
    # Route from pickup to dropoff
    to_dropoff_route = get_route(passenger_pickup, passenger_dropoff)

    # Combine routes
    total_distance = to_pickup_route['distance'] + to_dropoff_route['distance']
    total_duration = to_pickup_route['duration'] + to_dropoff_route['duration']
    geometry = to_pickup_route['geometry'] + to_dropoff_route['geometry']

    return {
        'total_distance': total_distance,
        'total_duration': total_duration,
        'geometry': geometry
    }
