import sys
import os
import pytest

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Website

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
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})

    with app.app_context():
        db.create_all()  # Create all tables
        # Add test data
        test_website = Website(
            id=1,  # Set the ID that you expect to test with
            name="Test Website",
            url="http://test.com",
            plugin_name="default",
            is_enabled=True,
            scrape_interval="never"
        )
        db.session.add(test_website)
        db.session.commit()  # Commit the test data
        
        yield app.test_client()  # Yield the test client for use in tests

        db.session.remove()  # Clean up session after tests
        db.drop_all()  # Drop all tables after tests


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
