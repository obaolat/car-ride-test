import pytest
from models import db, User, Driver, Admin, Rating
from flask import Flask
from database import init_db

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user(app):
    with app.app_context():
        user = User(name="Test User", latitude=40.7128, longitude=-74.0060, smoking=False, music=True, pets=True)
        db.session.add(user)
        db.session.commit()
        assert user.id is not None

def test_create_driver(app):
    with app.app_context():
        driver = Driver(name="Test Driver", latitude=40.73061, longitude=-73.935242, smoking=False, music=True, pets=True)
        db.session.add(driver)
        db.session.commit()
        assert driver.id is not None

def test_rating_update(app):
    with app.app_context():
        # Create a driver and add two ratings
        driver = Driver(name="Rated Driver", latitude=40.73061, longitude=-73.935242, smoking=False, music=True, pets=True)
        db.session.add(driver)
        db.session.commit()
        rating1 = Rating(user_id=1, driver_id=driver.id, score=4)
        rating2 = Rating(user_id=2, driver_id=driver.id, score=5)
        db.session.add_all([rating1, rating2])
        db.session.commit()

        avg = db.session.query(db.func.avg(Rating.score)).filter(Rating.driver_id == driver.id).scalar()
        assert round(avg, 2) == 4.5
