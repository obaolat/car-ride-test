import pytest
import requests
from navigation import get_route, calculate_optimal_route

# Base URL for the OSRM API
OSRM_BASE_URL = "http://router.project-osrm.org"

def test_get_route(monkeypatch):
    """
    Test the get_route function to ensure it retrieves the correct route information.
    """

    def mock_get(url, params):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        # Mocked response data
        mocked_data = {
            'routes': [{
                'distance': 1000,
                'duration': 600,
                'geometry': 'mocked_geometry'
            }]
        }
        return MockResponse(mocked_data, 200)

    # Use monkeypatch to replace 'requests.get' with our mock function
    monkeypatch.setattr(requests, 'get', mock_get)

    start = (13.388860, 52.517037)
    end = (13.397634, 52.529407)
    route = get_route(start, end)

    assert route['distance'] == 1000
    assert route['duration'] == 600
    assert route['geometry'] == 'mocked_geometry'

def test_calculate_optimal_route(monkeypatch):
    """
    Test the calculate_optimal_route function to ensure it calculates the correct combined route.
    """

    def mock_get(url, params):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        # Mocked response data
        mocked_data = {
            'routes': [{
                'distance': 1000,
                'duration': 600,
                'geometry': 'mocked_geometry'
            }]
        }
        return MockResponse(mocked_data, 200)

    # Use monkeypatch to replace 'requests.get' with our mock function
    monkeypatch.setattr(requests, 'get', mock_get)

    driver_location = (13.388860, 52.517037)
    passenger_pickup = (13.397634, 52.529407)
    passenger_dropoff = (13.428555, 52.523219)
    optimal_route = calculate_optimal_route(driver_location, passenger_pickup, passenger_dropoff)

    assert optimal_route['total_distance'] == 2000
    assert optimal_route['total_duration'] == 1200
    assert optimal_route['geometry'] == 'mocked_geometrymocked_geometry'
