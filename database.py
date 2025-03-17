from flask import Flask
from models import db

def init_db(app: Flask):
    """Initialize SQLite database."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ride_matching.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()