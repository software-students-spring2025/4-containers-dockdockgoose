import io
import pytest
from unittest.mock import patch
from flask import jsonify

# Import the Flask app and functions
from app import app, get_gemini_response


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test GET / returns 200 OK and correct message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"message": "ML client is running"}


def test_missing_file(client):
    """Test POST /predict with no file returns 400."""
    response = client.post("/predict", data={})
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "No file uploaded"


@patch("app.get_gemini_response")
def test_valid_file_upload(mock_response, client):
    """Test POST /predict with valid image and mocked Gemini response."""
    mock_response.return_value = "200"

    data = {
        "file": (io.BytesIO(b"fake image data"), "test.jpg"),
        "prompt": "How many calories?",
    }
    response = client.post("/predict", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    assert "calories" in response.json
    assert response.json["calories"] == "200"


@patch("app.get_gemini_response", side_effect=Exception("Gemini failed"))
def test_gemini_error_handling(_, client):
    """Test POST /predict handles Gemini API failure."""
    data = {"file": (io.BytesIO(b"fake"), "image.jpg"), "prompt": "test prompt"}
    response = client.post("/predict", data=data, content_type="multipart/form-data")

    assert response.status_code == 500
    assert "error" in response.json
    assert "Gemini failed" in response.json["error"]
