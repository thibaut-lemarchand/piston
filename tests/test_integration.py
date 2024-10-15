import sys
import os
import pytest

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db

@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # In-memory database for testing
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()  # Create the database tables

    yield app

    # Teardown (after tests run)
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client():
    app = create_app()  # Create the app within the fixture
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"pistON" in response.data


def test_toggle_website(client):
    response = client.get("/toggle/1")
    assert response.status_code == 302  # Redirect


def test_manual_scrape(client):
    response = client.get("/scrape/1")
    assert response.status_code == 200
    assert b"result" in response.data


def test_update_interval(client):
    response = client.post("/update_interval/1", json={"interval": "5min"})
    assert response.status_code == 200
    assert b"Scrape interval updated to 5min" in response.data


if __name__ == "__main__":
    pytest.main()
