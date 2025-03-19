import requests
from typing import List, Tuple
import polyline

OSRM_BASE_URL = "http://router.project-osrm.org"

def get_route(start: Tuple[float, float], end: Tuple[float, float]) -> dict:
    """
    Fetches the optimal route between start and end coordinates using OSRM.

    Args:
        start (Tuple[float, float]): Starting coordinates (latitude, longitude).
        end (Tuple[float, float]): Ending coordinates (latitude, longitude).

    Returns:
        dict: Route information including distance, duration, and geometry.
    """
    coords = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    url = f"{OSRM_BASE_URL}/route/v1/driving/{coords}"
    params = {
        "overview": "full",
        "geometries": "polyline",
        "steps": True
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data.get("code") == "Ok":
        route = data["routes"][0]
        return {
            "distance": route["distance"],
            "duration": route["duration"],
            "geometry": polyline.decode(route["geometry"])
        }
    else:
        raise Exception(f"OSRM error: {data.get('message')}")

def calculate_optimal_route(driver_location: Tuple[float, float], passenger_pickup: Tuple[float, float], passenger_dropoff: Tuple[float, float]) -> dict:
    """
    Determines the optimal route for a ride, including pickup and dropoff points.

    Args:
        driver_location (Tuple[float, float]): Driver's current location (latitude, longitude).
        passenger_pickup (Tuple[float, float]): Passenger's pickup location (latitude, longitude).
        passenger_dropoff (Tuple[float, float]): Passenger's dropoff location (latitude, longitude).

    Returns:
        dict: Optimal route details including total distance, total duration, and combined geometry.
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
