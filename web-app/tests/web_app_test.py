# pylint: disable=redefined-outer-name
import os
import io
import pytest
from app import app, User
from unittest.mock import patch

# Set test environment variables before importing anything else
os.environ["MONGO_URI"] = "mongodb://localhost:27017/"
os.environ["MONGO_DBNAME"] = "test_webapp_db"
os.environ["SECRET_KEY"] = "testing_secret"


@pytest.fixture(autouse=True)
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            # Clear the test collection before each test
            app.config["MONGO_DBNAME"] = "test_webapp_db"
            from pymongo import MongoClient
            test_db = MongoClient(os.environ["MONGO_URI"])[os.environ["MONGO_DBNAME"]]
            test_db.calcountInfo.delete_many({"username": "testuser"})
            test_db.calorieData.delete_many({"user_id": "testuser"})
            User.create_user("test@example.com", "testuser", "password123")
        yield client


def login(client):
    return client.post("/login", data={
        "username": "testuser",
        "password": "password123"
    }, follow_redirects=True)


def test_register_redirect(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/register" in response.headers["Location"]


def test_login_success(client):
    response = login(client)
    assert b"testuser" in response.data or b"Login successful!" in response.data


def test_login_failure(client):
    response = client.post("/login", data={
        "username": "wrong",
        "password": "wrong"
    }, follow_redirects=True)
    assert b"Log in" in response.data


def test_home_requires_login(client):
    response = client.get("/home")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_home_after_login(client):
    login(client)
    response = client.get("/home")
    assert response.status_code == 200
    assert b"testuser" in response.data


@patch("app.requests.post")
def test_capture_success(mock_post, client):
    login(client)
    mock_post.return_value.json.return_value = {"calories": "123"}
    mock_post.return_value.status_code = 200

    fake_file = (io.BytesIO(b"fake image data"), "test.jpg")

    response = client.post("/capture", data={
        "file": fake_file,
        "prompt": "Estimate calories"
    }, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"123" in response.data


def test_logout(client):
    login(client)
    response = client.get("/logout", follow_redirects=True)
    assert b"Log in" in response.data