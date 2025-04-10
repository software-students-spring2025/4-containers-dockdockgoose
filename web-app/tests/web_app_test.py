# tests/test_app.py

# pylint: disable=redefined-outer-name
import os
import pytest
from flask import Flask
from app import app, User, db
from unittest.mock import patch, MagicMock
import io


# Set env vars before importing the app that uses them
os.environ["MONGO_URI"] = "mongodb://localhost:27017/"
os.environ["MONGO_DBNAME"] = "test_db"
os.environ["SECRET_KEY"] = "test_secret"

@pytest.fixture(autouse=True)
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            # Clean up test DB
            db.calcountInfo.delete_many({})
            db.calorieData.delete_many({})
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
    assert b"Intelligent" in response.data or b"testuser" in response.data

def test_login_failure(client):
    response = client.post("/login", data={
        "username": "wrong",
        "password": "wrong"
    }, follow_redirects=True)
    assert b"Log in" in response.data

def test_home_requires_login(client):
    client.get("/logout")  # ensure logged out
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