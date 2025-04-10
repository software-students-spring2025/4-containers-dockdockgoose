"""
Unit tests for the machine learning client service.

Covers health check endpoint, image upload handling, and
interactions with the Gemini response function.
"""
import io
import sys
import os
from unittest.mock import patch
from app import app  # noqa: E402
import pytest
# Ensure the app module is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))


@pytest.fixture
def client():
    """
    Pytest fixture to provide a test client for the ML Flask app.

    Yields:
        flask.testing.FlaskClient: The test client instance.
    """
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """
    Test that the root route returns a healthy status.

    Asserts:
        - Status code is 200.
        - Response message confirms the app is running.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"message": "ML client is running"}


def test_missing_file(client):
    """
    Test that sending a POST request to /predict with no file returns a 400 error.

    Asserts:
        - Status code is 400.
        - Response includes an 'error' message.
    """
    response = client.post("/predict", data={})
    assert response.status_code == 400
    assert "error" in response.json
    assert response.json["error"] == "No file uploaded"


@patch("app.get_gemini_response")
def test_valid_file_upload(mock_response, client):
    """
    Test a valid image upload and mock Gemini response.

    Args:
        mock_response (Mock): A mock of the Gemini response function.

    Asserts:
        - Status code is 200.
        - The JSON response contains the expected calorie value.
    """
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
    """
    Test that the server handles exceptions from the Gemini API call gracefully.

    Asserts:
        - Status code is 500.
        - The error message is included in the response.
    """
    data = {"file": (io.BytesIO(b"fake"), "image.jpg"), "prompt": "test prompt"}
    response = client.post("/predict", data=data, content_type="multipart/form-data")

    assert response.status_code == 500
    assert "error" in response.json
    assert "Gemini failed" in response.json["error"]
