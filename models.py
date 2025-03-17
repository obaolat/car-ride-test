from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Passenger model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    smoking = db.Column(db.Boolean, default=False)
    music = db.Column(db.Boolean, default=False)
    pets = db.Column(db.Boolean, default=False) 

    ratings = db.relationship('Rating', backref='user', lazy=True)

class Driver(db.Model):
    """Driver model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=5.0)  # Dynamic rating
    is_available = db.Column(db.Boolean, default=True)
    smoking = db.Column(db.Boolean, default=False)
    music = db.Column(db.Boolean, default=False)
    pets = db.Column(db.Boolean, default=False)

    ratings = db.relationship('Rating', backref='driver', lazy=True)

    def update_rating(self):
        """Recalculates the driver's rating based on user feedback."""
        ratings = Rating.query.filter_by(driver_id=self.id).all()
        if ratings:
            self.rating = sum(r.score for r in ratings) / len(ratings)
        else:
            self.rating = 5.0  # Default if no ratings yet
        db.session.commit()

class Rating(db.Model):
    """Stores user ratings for drivers."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # Rating between 1-5
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Rating(user={self.user_id}, driver={self.driver_id}, score={self.score})>"

class Admin(db.Model):
    """Admin model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  

    def create_user(self, name, latitude, longitude, smoking, music):
        """Admin function to create a user."""
        user = User(name=name, latitude=latitude, longitude=longitude, smoking=smoking, music=music)
        db.session.add(user)
        db.session.commit()

    def delete_user(self, user_id):
        """Admin function to delete a user."""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()

    def create_driver(self, name, latitude, longitude, smoking, music):
        """Admin function to create a driver."""
        driver = Driver(name=name, latitude=latitude, longitude=longitude, smoking=smoking, music=music)
        db.session.add(driver)
        db.session.commit()

    def delete_driver(self, driver_id):
        """Admin function to delete a driver."""
        driver = Driver.query.get(driver_id)
        if driver:
            db.session.delete(driver)
            db.session.commit()
