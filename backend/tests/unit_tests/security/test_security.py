"""Tests for the security use cases."""

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.common.user import Device, DeviceType, User, UserDB

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_user_db():
    """Reset UserDB."""
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


def test_reconfirm_success_with_address():
    """Test successful reconfirm with correct address."""
    response = client.post(
        "/reconfirm/",
        json={
            "user_id": "homeowner1",
            "address": "123 Main St",
            "phone_number": None,
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Reconfirmed successfully"}


def test_reconfirm_success_with_phone():
    """Test successful reconfirm with correct phone number."""
    response = client.post(
        "/reconfirm/",
        json={
            "user_id": "homeowner1",
            "address": None,
            "phone_number": "01012345678",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Reconfirmed successfully"}


def test_reconfirm_invalid_user():
    """Test reconfirm with invalid user ID."""
    response = client.post(
        "/reconfirm/",
        json={
            "user_id": "unknown",
            "address": None,
            "phone_number": "01012345678",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_reconfirm_info_mismatch():
    """Test reconfirm with mismatched information."""
    response = client.post(
        "/reconfirm/",
        json={
            "user_id": "homeowner1",
            "address": "wrong",
            "phone_number": "wrong",
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Information mismatch"


def test_create_safety_zone_success():
    """Test successful creation of safety zone."""
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Safety zone created successfully"}


def test_create_safety_zone_invalid_user():
    """Test create safety zone with invalid user ID."""
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "unknown",
            "name": "Living Room",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_create_safety_zone_empty_name():
    """Test create safety zone with empty name."""
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Select new safety zone and type safety zone name"
    )


def test_create_safety_zone_no_devices():
    """Test create safety zone with no devices selected."""
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Select new safety zone and type safety zone name"
    )


def test_create_safety_zone_same_name():
    """Test create safety zone with existing name."""
    # First create one
    client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [1],
        },
    )
    # Try to create another with same name
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [2],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Same safety zone exists"


def test_create_safety_zone_device_not_found():
    """Test create safety zone with non-existent device."""
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Kitchen",
            "device_ids": [99],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Device with id 99 not found"


def test_delete_safety_zone_success():
    """Test successful deletion of safety zone."""
    # First create a zone
    client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [1, 2],
        },
    )

    response = client.post(
        "/delete-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Safety zone deleted successfully"}


def test_delete_safety_zone_invalid_user():
    """Test delete safety zone with invalid user ID."""
    response = client.post(
        "/delete-safety-zone/",
        json={
            "user_id": "unknown",
            "name": "Living Room",
            "device_ids": [],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_delete_safety_zone_not_found():
    """Test delete safety zone that doesn't exist."""
    response = client.post(
        "/delete-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Nonexistent Zone",
            "device_ids": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Safety zone not found"


def test_update_safety_zone_success():
    """Test successful update of safety zone devices."""
    # First create a safety zone
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Test Zone",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 200

    # Now update the devices
    response = client.post(
        "/update-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Test Zone",
            "device_ids": [1, 3],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Safety zone updated successfully"}


def test_update_safety_zone_invalid_user():
    """Test update safety zone with invalid user ID."""
    response = client.post(
        "/update-safety-zone/",
        json={
            "user_id": "unknown",
            "name": "Test Zone",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_update_safety_zone_not_found():
    """Test update safety zone that doesn't exist."""
    response = client.post(
        "/update-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Nonexistent Zone",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Safety zone not found"


def test_update_safety_zone_no_devices():
    """Test update safety zone with no devices."""
    # First create a safety zone
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Test Zone",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 200

    # Try to update with no devices
    response = client.post(
        "/update-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Test Zone",
            "device_ids": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Select safety zone and choose security devices"


def test_update_safety_zone_device_not_found():
    """Test update safety zone with device that doesn't exist."""
    # First create a safety zone
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Test Zone",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 200

    # Try to update with nonexistent device
    response = client.post(
        "/update-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Test Zone",
            "device_ids": [1, 99],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Device with id 99 not found"
