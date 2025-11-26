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


def test_get_safety_zones_success():
    """Test successful retrieval of safety zones."""
    client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [1, 2],
        },
    )

    response = client.get("/get-safety-zones/", params={"user_id": "homeowner1"})
    assert response.status_code == 200
    data = response.json()
    expected = {
        "safety_zones": [
            {
                "name": "Living Room",
                "devices": [
                    {"type": "sensor", "id": 1},
                    {"type": "sensor", "id": 2},
                ],
                "is_armed": False,
            }
        ]
    }
    assert data == expected


def test_get_safety_zones_invalid_user():
    """Test get safety zones with invalid user ID."""
    response = client.get("/get-safety-zones/", params={"user_id": "unknown"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_arm_success():
    """Test successful arming of all devices."""
    response = client.post("/arm/", params={"user_id": "homeowner1"})
    assert response.status_code == 200
    assert response.json() == {"message": "All devices armed successfully"}

    user = UserDB.find_user_by_id("homeowner1")
    for device in user.devices:
        assert device.is_armed is True


def test_arm_invalid_user():
    """Test arming with invalid user ID."""
    response = client.post("/arm/", params={"user_id": "unknown"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_disarm_success():
    """Test successful disarming of all devices."""
    client.post("/arm/", params={"user_id": "homeowner1"})
    response = client.post("/disarm/", params={"user_id": "homeowner1"})
    assert response.status_code == 200
    assert response.json() == {"message": "All devices disarmed successfully"}

    user = UserDB.find_user_by_id("homeowner1")
    for device in user.devices:
        assert device.is_armed is False


def test_disarm_invalid_user():
    """Test disarming with invalid user ID."""
    response = client.post("/disarm/", params={"user_id": "unknown"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_arm_safety_zone_success():
    """Test successful arming of safety zone."""
    # First create a safety zone
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [1, 2],
        },
    )
    assert response.status_code == 200

    # Arm the safety zone
    response = client.post(
        "/arm-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Living Room",
            "device_ids": [],  # Ignored
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Safety zone armed successfully"}

    # Verify the safety zone is armed
    response = client.get("/get-safety-zones/?user_id=homeowner1")
    assert response.status_code == 200
    safety_zones = response.json()["safety_zones"]
    expected_safety_zones = [
        {
            "name": "Living Room",
            "devices": [
                {"type": "sensor", "id": 1},
                {"type": "sensor", "id": 2},
            ],
            "is_armed": True,
        }
    ]
    assert safety_zones == expected_safety_zones


def test_arm_safety_zone_invalid_user():
    """Test arming safety zone with invalid user ID."""
    response = client.post(
        "/arm-safety-zone/",
        json={
            "user_id": "unknown",
            "name": "Living Room",
            "device_ids": [],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_arm_safety_zone_not_found():
    """Test arming non-existent safety zone."""
    response = client.post(
        "/arm-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Nonexistent",
            "device_ids": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Safety zone not found"


def test_disarm_safety_zone_success():
    """Test successful disarming of safety zone."""
    # First create and arm a safety zone
    response = client.post(
        "/create-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Bedroom",
            "device_ids": [3],
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/arm-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Bedroom",
            "device_ids": [],
        },
    )
    assert response.status_code == 200

    # Disarm the safety zone
    response = client.post(
        "/disarm-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Bedroom",
            "device_ids": [],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Safety zone disarmed successfully"}

    # Verify the safety zone is disarmed
    response = client.get("/get-safety-zones/?user_id=homeowner1")
    assert response.status_code == 200
    safety_zones = response.json()["safety_zones"]
    expected_safety_zones = [
        {
            "name": "Bedroom",
            "devices": [
                {"type": "camera", "id": 3},
            ],
            "is_armed": False,
        }
    ]
    assert safety_zones == expected_safety_zones


def test_disarm_safety_zone_invalid_user():
    """Test disarming safety zone with invalid user ID."""
    response = client.post(
        "/disarm-safety-zone/",
        json={
            "user_id": "unknown",
            "name": "Living Room",
            "device_ids": [],
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user ID"


def test_disarm_safety_zone_not_found():
    """Test disarming non-existent safety zone."""
    response = client.post(
        "/disarm-safety-zone/",
        json={
            "user_id": "homeowner1",
            "name": "Nonexistent",
            "device_ids": [],
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Safety zone not found"


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

    # Check if safety zone was added via get-safety-zones
    response = client.get("/get-safety-zones/?user_id=homeowner1")
    assert response.status_code == 200
    safety_zones = response.json()["safety_zones"]
    expected_safety_zones = [
        {
            "name": "Living Room",
            "devices": [
                {"type": "sensor", "id": 1},
                {"type": "sensor", "id": 2},
            ],
            "is_armed": False,
        }
    ]
    assert safety_zones == expected_safety_zones


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

    # Check if safety zone was deleted
    response = client.get("/get-safety-zones/?user_id=homeowner1")
    assert response.status_code == 200
    safety_zones = response.json()["safety_zones"]
    assert safety_zones == []


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

    # Check if safety zone was updated
    response = client.get("/get-safety-zones/?user_id=homeowner1")
    assert response.status_code == 200
    safety_zones = response.json()["safety_zones"]
    expected_safety_zones = [
        {
            "name": "Test Zone",
            "devices": [
                {"type": "sensor", "id": 1},
                {"type": "camera", "id": 3},
            ],
            "is_armed": False,
        }
    ]
    assert safety_zones == expected_safety_zones


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
