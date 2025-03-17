# matcher.py

from models import db, Driver, Rating
from graphs import Graph
from traffic import get_live_travel_time
from sqlalchemy.sql import func

class RideMatcher:
    """
    Finds the best available driver for a user based on:
      - Real-time ETA (via OSRM API)
      - Straight-line distance (Haversine estimate)
      - Driver rating (dynamic, based on user ratings)
      - Passenger preferences (smoking, music, pets; at least 2/3 must match)
    
    The composite score is calculated such that lower scores represent better matches.
    """

    def __init__(self):
        # Create an instance of Graph for calculating straight-line distances.
        self.graph = Graph()

    def calculate_driver_rating(self, driver_id):
        """
        Dynamically calculates the average rating of a driver.
        Returns a value between 1 and 5 (defaults to 5.0 if no ratings exist).
        """
        avg_rating = db.session.query(func.avg(Rating.score)).filter(Rating.driver_id == driver_id).scalar()
        return round(avg_rating, 2) if avg_rating else 5.0

    def find_best_driver(self, user):
        """
        This function finds and then returns the best available driver for the given user.
        It onnly really considers drivers that match at least 2 out of 3 preferences (smoking, music, pets).
        Combines both dynamic ETA and the Haversine distance, then adjusts for driver rating.
        """
        available_drivers = Driver.query.filter_by(is_available=True).all()
        if not available_drivers:
            return None  # No available drivers

        best_driver = None
        best_score = float('inf')
        user_location = (user.latitude, user.longitude)

        # Define weight factors (adjustable)
        weight_eta = 0.5         # Weight for real-time ETA (in minutes)
        weight_distance = 0.3    # Weight for straight-line distance (in km)
        # Higher driver rating is better, so we divide by rating to lower the score
        # (Assuming ratings are between 1 and 5)

        for driver in available_drivers:
            driver_location = (driver.latitude, driver.longitude)

            # Check if at least 2 of 3 preferences match:
            preference_match = sum([
                user.smoking == driver.smoking,
                user.music == driver.music,
                getattr(user, 'pets', False) == getattr(driver, 'pets', False)
            ])
            if preference_match < 2:
                continue

            # Calculate straight-line distance using the Haversine formula from our Graph class.
            distance_km = self.graph.heuristic(user_location, driver_location)

            # Get dynamic ETA (in minutes) from OSRM API using our traffic module.
            eta = get_live_travel_time(user_location, driver_location)
            if eta is None:
                continue  # Skip this driver if we couldn't retrieve an ETA

            # Calculate driver's average rating dynamically.
            driver_rating = self.calculate_driver_rating(driver.id)

            # Compute a composite score:
            # Lower ETA and lower distance are better.
            # A higher rating reduces the score.
            composite_score = (weight_eta * eta + weight_distance * distance_km) / driver_rating

            # Select the driver with the lowest composite score.
            if composite_score < best_score:
                best_score = composite_score
                best_driver = driver

        return best_driver
