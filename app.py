# app.py
import os
from flask import Flask
from routes import routes
from database import db  # Import the db instance
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "your_default_secret_key"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///ride_matching.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    
    # Initialize database
    db.init_app(app)
    
    # Initialize Flask-Migrate
    Migrate(app, db)

    # Register Blueprints
    app.register_blueprint(routes)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True", host="0.0.0.0", port=5000)
