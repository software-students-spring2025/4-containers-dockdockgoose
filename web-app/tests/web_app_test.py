# pylint: disable=redefined-outer-name
"""
Unit tests for the web application.

Tests include user registration, login, access control,
calorie data submission, and logout functionality.
"""

import os
import io
from unittest.mock import patch
import pytest
from app import app, User

# Set test environment variables before importing anything else
os.environ["MONGO_URI"] = "mongodb://localhost:27017/"
os.environ["MONGO_DBNAME"] = "test_webapp_db"
os.environ["SECRET_KEY"] = "testing_secret"


@pytest.fixture(autouse=True)
def client():
    """
    Pytest fixture to configure the Flask test client and reset the test DB.

    Yields:
        flask.testing.FlaskClient: Test client for sending requests.
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            from pymongo import MongoClient

            test_db = MongoClient(os.environ["MONGO_URI"])[os.environ["MONGO_DBNAME"]]
            test_db.calcountInfo.delete_many({"username": "testuser"})
            test_db.calorieData.delete_many({"user_id": "testuser"})
            User.create_user("test@example.com", "testuser", "password123")
        yield client


def login(client):
    """
    Helper function to log in a test user.

    Args:
        client (FlaskClient): The Flask test client.

    Returns:
        flask.Response: Response object from the login request.
    """
    return client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )


def test_register_redirect(client):
    """
    Test that accessing the root path redirects to the registration page.
    """
    response = client.get("/")
    assert response.status_code == 302
    assert "/register" in response.headers["Location"]


def test_login_success(client):
    """
    Test that valid login credentials result in a successful login.
    """
    response = login(client)
    assert b"testuser" in response.data or b"Login successful!" in response.data


def test_login_failure(client):
    """
    Test that invalid login credentials show the login form again.
    """
    response = client.post(
        "/login", data={"username": "wrong", "password": "wrong"}, follow_redirects=True
    )
    assert b"Log in" in response.data


def test_home_requires_login(client):
    """
    Test that the home page redirects to login when not authenticated.
    """
    response = client.get("/home")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_home_after_login(client):
    """
    Test that the home page is accessible after a successful login.
    """
    login(client)
    response = client.get("/home")
    assert response.status_code == 200
    assert b"testuser" in response.data


@patch("app.requests.post")
def test_capture_success(mock_post, client):
    """
    Test successful image capture and calorie submission.

    Args:
        mock_post (Mock): Mocked requests.post to simulate ML service response.
    """
    login(client)
    mock_post.return_value.json.return_value = {"calories": "123"}
    mock_post.return_value.status_code = 200

    fake_file = (io.BytesIO(b"fake image data"), "test.jpg")

    response = client.post(
        "/capture",
        data={"file": fake_file, "prompt": "Estimate calories"},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b"123" in response.data


def test_logout(client):
    """
    Test that logging out redirects to the login page.
    """
    login(client)
    response = client.get("/logout", follow_redirects=True)
    assert b"Log in" in response.data
