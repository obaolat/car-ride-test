import pytest
from app import create_app
from models import db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    # Use an in-memory database for testing.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.drop_all()

        db.create_all()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    # Assuming you have a simple index route or can call one of your routes.
    response = client.get('/users')  # For example, retrieving users.
    assert response.status_code in [200, 404]  # It may be empty initially.
