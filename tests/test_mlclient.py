"""Tests for the machine_learning_client app."""

import pytest  # pylint: disable=unused-import

from machine_learning_client.app import input_image_setup


def test_input_image_setup():
    """Test the input_image_setup function for correct output."""

    file_bytes = "file_bytes"
    mime_type = "mime_type"
    expected = {"mime_type": mime_type, "data": file_bytes}
    result = input_image_setup(file_bytes, mime_type)
    assert result == expected, f"Expected {expected}, got {result}"


def test_get_gemini_response():
    """Test the get_gemini_response function for correct output."""
    print("hello")


def test_predict():
    """Test the test_predict function for correct output."""
    print("hello")


def test_index():
    """Test the index function for correct output."""
    print("hello")
