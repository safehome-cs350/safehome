"""Tests for the app module."""

from fastapi.testclient import TestClient

from backend.app import app

client = TestClient(app)


def test_login_success():
    """Test successful login."""
    response = client.post(
        "/login/",
        json={
            "user_id": "homeowner1",
            "password1": "12345678",
            "password2": "abcdefgh",
        },
    )
    assert response.status_code == 200
    assert response.json() == "Welcome!"


def test_login_invalid_user():
    """Test login with invalid user ID."""
    response = client.post(
        "/login/",
        json={
            "user_id": "unknown",
            "password1": "12345678",
            "password2": "abcdefgh",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "ID not recognized"


def test_login_wrong_password():
    """Test login with wrong password."""
    response = client.post(
        "/login/",
        json={
            "user_id": "homeowner1",
            "password1": "wrongpass",
            "password2": "abcdefgh",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Password incorrect"
