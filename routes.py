import hashlib
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from models import db, User, Driver, Admin, Rating
from matcher import RideMatcher  
from dotenv import load_dotenv
from functools import wraps
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

routes = Blueprint('routes', __name__)

# ------------------- ADMIN AUTH & CRUD ------------------- #

@routes.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login with JWT authentication."""
    data = request.json
    admin = Admin.query.filter_by(username=data["username"]).first()

    if admin and hashlib.sha256(data["password"].encode()).hexdigest() == admin.password:
        token = jwt.encode(
            {"admin_id": admin.id, "exp": datetime.utcnow() + timedelta(hours=2)},
            SECRET_KEY,
            algorithm="HS256"
        )
        return jsonify({"token": token}), 200

    return jsonify({"error": "Invalid credentials"}), 401


def admin_required(func):
    """Decorator to ensure only admins can access certain routes."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 403
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            admin = Admin.query.get(decoded_token["admin_id"])
            if not admin:
                return jsonify({"error": "Unauthorized"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 403

        return func(*args, **kwargs)
    return wrapper


@routes.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Allows admin to delete a user."""
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 200
    return jsonify({"error": "User not found"}), 404


@routes.route('/admin/delete_driver/<int:driver_id>', methods=['DELETE'])
@admin_required
def delete_driver(driver_id):
    """Allows admin to delete a driver."""
    driver = Driver.query.get(driver_id)
    if driver:
        db.session.delete(driver)
        db.session.commit()
        return jsonify({"message": "Driver deleted"}), 200
    return jsonify({"error": "Driver not found"}), 404


# ------------------- USER & DRIVER CREATION ------------------- #

@routes.route('/user', methods=['POST'])
def create_user():
    """Registers a new user."""
    data = request.json
    new_user = User(**data)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


@routes.route('/driver', methods=['POST'])
def create_driver():
    """Registers a new driver."""
    data = request.json
    new_driver = Driver(**data)
    db.session.add(new_driver)
    db.session.commit()
    return jsonify({"message": "Driver created"}), 201


# ------------------- USER-DRIVER MATCHING ------------------- #

@routes.route('/match/<int:user_id>', methods=['GET'])
def match_user(user_id):
    """Matches a user to the best available driver based on location and preferences."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    matcher = RideMatcher()
    best_driver = matcher.find_best_driver(user)

    if best_driver:
        return jsonify({
            "driver_id": best_driver.id,
            "rating": best_driver.rating
        })
    return jsonify({"message": "No suitable driver found"}), 404


# ------------------- DRIVER RATING SYSTEM ------------------- #

@routes.route('/rate_driver/<int:driver_id>', methods=['POST'])
def rate_driver(driver_id):
    """Allows users to rate drivers dynamically, recalculating their average rating."""
    data = request.json
    user_id = data.get("user_id")
    rating_score = data.get("rating")

    if rating_score is None or not (1 <= rating_score <= 5):
        return jsonify({"error": "Invalid rating. Must be between 1 and 5"}), 400

    user = User.query.get(user_id)
    driver = Driver.query.get(driver_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    # Store the new rating
    new_rating = Rating(user_id=user_id, driver_id=driver_id, score=rating_score)
    db.session.add(new_rating)
    db.session.commit()

    # Recalculate the driver's average rating
    avg_rating = db.session.query(db.func.avg(Rating.score)).filter(Rating.driver_id == driver_id).scalar()
    driver.rating = round(avg_rating, 2) if avg_rating else 5.0
    db.session.commit()

    return jsonify({
        "message": "Rating submitted successfully",
        "driver_id": driver.id,
        "new_average_rating": driver.rating
    }), 200


# ------------------- FETCH USERS & DRIVERS ------------------- #

@routes.route('/users', methods=['GET'])
def get_users():
    """Retrieves a list of all users."""
    users = User.query.all()
    return jsonify([{
        "id": user.id,
        "name": user.name,
        "latitude": user.latitude,
        "longitude": user.longitude,
        "smoking": user.smoking,
        "music": user.music
    } for user in users]), 200


@routes.route('/drivers', methods=['GET'])
def get_drivers():
    """Retrieves a list of all drivers."""
    drivers = Driver.query.all()
    return jsonify([{
        "id": driver.id,
        "name": driver.name,
        "latitude": driver.latitude,
        "longitude": driver.longitude,
        "rating": driver.rating,
        "is_available": driver.is_available,
        "smoking": driver.smoking,
        "music": driver.music
    } for driver in drivers]), 200


# ------------------- FETCH DRIVER RATINGS ------------------- #

@routes.route('/driver/<int:driver_id>/ratings', methods=['GET'])
def get_driver_ratings(driver_id):
    """Fetch all ratings for a specific driver."""
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    ratings = Rating.query.filter_by(driver_id=driver_id).all()
    return jsonify([{
        "user_id": rating.user_id,
        "score": rating.score,
        "timestamp": rating.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for rating in ratings]), 200
