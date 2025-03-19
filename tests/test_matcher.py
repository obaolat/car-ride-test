from models import User, Driver
from matcher import RideMatcher
from graphs import Graph

class DummyUser:
    def __init__(self, latitude, longitude, smoking, music, pets):
        self.latitude = latitude
        self.longitude = longitude
        self.smoking = smoking
        self.music = music
        self.pets = pets

class DummyDriver:
    def __init__(self, id, latitude, longitude, smoking, music, pets, rating=5.0, is_available=True):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.smoking = smoking
        self.music = music
        self.pets = pets
        self.rating = rating
        self.is_available = is_available

# Override Driver.query.filter_by to return a list of dummy drivers for testing.
class DummyDriverQuery:
    def __init__(self, drivers):
        self.drivers = drivers

    def filter_by(self, **kwargs):
        available = [d for d in self.drivers if d.is_available]
        return available

def test_find_best_driver(monkeypatch):
    # Create a dummy user and two dummy drivers.
    user = DummyUser(40.7128, -74.0060, smoking=False, music=True, pets=True)
    driver1 = DummyDriver(1, 40.7138, -74.0050, smoking=False, music=True, pets=True, rating=4.5)
    driver2 = DummyDriver(2, 40.7328, -73.9350, smoking=False, music=True, pets=False, rating=5.0)
    dummy_drivers = [driver1, driver2]

    # Monkey-patch Driver.query.filter_by to return our dummy drivers
    from models import Driver
    Driver.query = DummyDriverQuery(dummy_drivers)

    # Also, override the traffic function to return a fixed ETA.
    monkeypatch.setattr("matcher.get_live_travel_time", lambda start, end: 10)

    matcher = RideMatcher()
    best = matcher.find_best_driver(user)
    # In this dummy scenario, driver1 matches all preferences, so it should be selected.
    assert best.id == 1
