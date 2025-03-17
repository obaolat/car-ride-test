import json
from traffic import get_live_travel_time

class DummyResponse:
    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

def dummy_get(url):
    # Return a dummy OSRM response with a duration of 600 seconds (10 minutes)
    dummy_data = {
        "code": "Ok",
        "routes": [{
            "duration": 600
        }]
    }
    return DummyResponse(dummy_data, 200)

def test_get_live_travel_time(monkeypatch):
    monkeypatch.setattr("traffic.requests.get", dummy_get)
    start = (40.7128, -74.0060)
    end = (40.73061, -73.935242)
    travel_time = get_live_travel_time(start, end)
    # 600 seconds should convert to 10 minutes
    assert travel_time == 10
