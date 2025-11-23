"""Tests for the common use cases."""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.common.user import Device, DeviceType, User, UserDB

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_user_db():
    """Reset UserDB to initial state before each test."""
    UserDB.users = [
        User(
            user_id="homeowner1",
            password1="12345678",
            password2="abcdefgh",
            master_password="1234",
            guest_password="5678",
            delay_time=300,
            phone_number="01012345678",
            is_powered_on=True,
            address="123 Main St",
            devices=[
                Device(type=DeviceType.SENSOR, id=1),
                Device(type=DeviceType.SENSOR, id=2),
                Device(type=DeviceType.CAMERA, id=3),
            ],
            safety_zones=[],
        )
    ]


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


def test_config_success():
    """Test successful config update."""
    response = client.post(
        "/config/",
        json={
            "user_id": "homeowner1",
            "password1": "newpass1",
            "password2": "newpass2",
            "master_password": "newmaster",
            "guest_password": "newguest",
            "delay_time": 600,
            "phone_number": "01098765432",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Configuration updated successfully"}


def test_config_invalid_user():
    """Test config with invalid user ID."""
    response = client.post(
        "/config/",
        json={
            "user_id": "unknown",
            "password1": "newpass1",
            "password2": "newpass2",
            "master_password": "newmaster",
            "guest_password": "newguest",
            "delay_time": 600,
            "phone_number": "01098765432",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_config_delay_time_too_small():
    """Test config with delay time less than 300."""
    response = client.post(
        "/config/",
        json={
            "user_id": "homeowner1",
            "password1": None,
            "password2": None,
            "master_password": None,
            "guest_password": None,
            "delay_time": 200,
            "phone_number": None,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Delay time must be at least 300"


def test_power_on_success():
    """Test successful power on."""
    response = client.post(
        "/power_on/",
        json={"user_id": "homeowner1"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "System powered on"}


def test_power_on_invalid_user():
    """Test power on with invalid user ID."""
    response = client.post(
        "/power_on/",
        json={"user_id": "unknown"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_power_off_success():
    """Test successful power off."""
    response = client.post(
        "/power_off/",
        json={"user_id": "homeowner1"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "System powered off"}


def test_power_off_invalid_user():
    """Test power off with invalid user ID."""
    response = client.post(
        "/power_off/",
        json={"user_id": "unknown"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"
