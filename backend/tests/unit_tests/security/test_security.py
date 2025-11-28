"""Tests for the security use cases."""

import pytest
from fastapi import HTTPException
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


@pytest.fixture
def test_user():
    """Fixture for a valid test user object."""
    from backend.common.user import UserDB

    return UserDB.users[0]


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


def test_alarm_condition_encountered(test_user):
    """Test alarm_condition_encountered 정상 동작."""
    # Add a dummy alarm event to test_user
    from backend.common.user import AlarmEvent
    from backend.security.request import AlarmEventRequest
    from backend.security.security import alarm_condition_encountered

    test_user.alarm_events.append(
        AlarmEvent(
            id=1,
            alarm_type="intrusion",
            timestamp="2025-11-28T00:00:00",
            device_id=1,
            location="거실",
            description="Test alarm",
        )
    )
    req = AlarmEventRequest(
        user_id=test_user.user_id,
        alarm_type=test_user.alarm_events[0].alarm_type,
        device_id=1,
        location="거실",
        description="Test alarm",
    )
    result = alarm_condition_encountered(req)
    assert "event_id" in result
    assert "message" in result
    assert "actions_taken" in result


def test_alarm_condition_encountered_invalid_user(test_user):
    """Test alarm_condition_encountered invalid user."""
    from backend.security.request import AlarmEventRequest
    from backend.security.security import alarm_condition_encountered

    req = AlarmEventRequest(
        user_id="invalid_user",
        alarm_type="intrusion",
        device_id=1,
        location="거실",
        description="Test alarm",
    )
    with pytest.raises(HTTPException) as exc_info:
        alarm_condition_encountered(req)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_alarm_condition_encountered_invalid_device(test_user):
    """Test alarm_condition_encountered invalid device."""
    from backend.security.request import AlarmEventRequest
    from backend.security.security import alarm_condition_encountered

    req = AlarmEventRequest(
        user_id=test_user.user_id,
        alarm_type="intrusion",
        device_id=999,  # 존재하지 않는 device
        location="거실",
        description="Test alarm",
    )
    with pytest.raises(HTTPException) as exc_info:
        alarm_condition_encountered(req)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Device not found"


def test_view_intrusion_log(test_user):
    """Test view_intrusion_log 정상 동작."""
    from backend.security.request import ViewLogRequest
    from backend.security.security import view_intrusion_log

    req = ViewLogRequest(
        user_id=test_user.user_id, start_date=None, end_date=None, alarm_type=None
    )
    result = view_intrusion_log(req)
    assert "total_events" in result
    assert "events" in result


def test_view_intrusion_log_empty(test_user):
    """Test view_intrusion_log with empty events."""
    from backend.security.request import ViewLogRequest
    from backend.security.security import view_intrusion_log

    req = ViewLogRequest(
        user_id=test_user.user_id, start_date=None, end_date=None, alarm_type=None
    )
    # test_user의 alarm_events를 비웁니다
    test_user.alarm_events.clear()
    result = view_intrusion_log(req)
    assert result["total_events"] == 0
    assert result["events"] == []


def test_panic_call_monitoring_service(test_user):
    """Test panic_call_monitoring_service 정상 동작."""
    from backend.security.request import PanicRequest
    from backend.security.security import panic_call_monitoring_service

    req = PanicRequest(user_id=test_user.user_id, location="거실")
    result = panic_call_monitoring_service(req)
    assert "event_id" in result
    assert "message" in result
    assert "actions_taken" in result
    assert result["monitoring_service_status"] == "contacted"


def test_configure_safety_zone_interface(test_user):
    """Test configure_safety_zone_interface 정상 동작."""
    from backend.security.security import configure_safety_zone_interface

    result = configure_safety_zone_interface(test_user.user_id)
    assert "message" in result
    assert "available_functions" in result
    assert "existing_safety_zones" in result
    assert "available_devices" in result
    assert "floor_plan_info" in result
    assert result["floor_plan_info"] == (
        "Floor plan with safety zones and device locations displayed"
    )


def test_configure_safehome_modes(test_user):
    """Test configure_safehome_modes 정상 동작."""
    from backend.common.device import SafeHomeModeType
    from backend.security.request import SafeHomeModeRequest
    from backend.security.security import configure_safehome_modes

    req = SafeHomeModeRequest(
        user_id=test_user.user_id,
        mode_type=SafeHomeModeType.AWAY,
        enabled_device_ids=[1, 2],
    )
    response = configure_safehome_modes(req)
    assert response["message"] == "SafeHome mode away configured successfully"


def test_configure_safehome_modes_invalid_device(test_user):
    """Test configure_safehome_modes with invalid device."""
    import pytest

    from backend.common.device import SafeHomeModeType
    from backend.security.request import SafeHomeModeRequest
    from backend.security.security import configure_safehome_modes

    req = SafeHomeModeRequest(
        user_id=test_user.user_id,
        mode_type=SafeHomeModeType.AWAY,
        enabled_device_ids=[999],  # 없는 device
    )
    with pytest.raises(HTTPException) as exc_info:
        configure_safehome_modes(req)
    assert exc_info.value.status_code == 400
    assert "Device with id" in exc_info.value.detail


def test_configure_safehome_modes_invalid_user():
    """Test configure_safehome_modes with invalid user."""
    import pytest

    from backend.common.device import SafeHomeModeType
    from backend.security.request import SafeHomeModeRequest
    from backend.security.security import configure_safehome_modes

    req = SafeHomeModeRequest(
        user_id="invalid_user", mode_type=SafeHomeModeType.AWAY, enabled_device_ids=[]
    )
    with pytest.raises(HTTPException) as exc_info:
        configure_safehome_modes(req)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_set_safehome_mode_not_configured(test_user):
    """Test set_safehome_mode with not configured mode."""
    import pytest

    from backend.common.device import SafeHomeModeType
    from backend.security.request import SetModeRequest
    from backend.security.security import set_safehome_mode

    req = SetModeRequest(user_id=test_user.user_id, mode_type=SafeHomeModeType.AWAY)
    with pytest.raises(HTTPException) as exc_info:
        set_safehome_mode(req)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Mode not configured"


def test_set_safehome_mode_doors_windows_open(test_user):
    """Test set_safehome_mode with doors/windows open."""
    import pytest

    from backend.common.device import SafeHomeMode, SafeHomeModeType
    from backend.security.request import SetModeRequest
    from backend.security.security import set_safehome_mode

    # 모드 설정
    test_user.safehome_modes[SafeHomeModeType.AWAY] = SafeHomeMode(
        mode_type=SafeHomeModeType.AWAY, enabled_device_ids=[1]
    )
    test_user.doors_windows_closed = False
    req = SetModeRequest(user_id=test_user.user_id, mode_type=SafeHomeModeType.AWAY)
    with pytest.raises(HTTPException) as exc_info:
        set_safehome_mode(req)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "doors and windows not closed"


def test_view_intrusion_log_filter_by_date_and_type(test_user):
    """Test view_intrusion_log with date/type filter."""
    import datetime

    from backend.common.device import AlarmType
    from backend.common.user import AlarmEvent
    from backend.security.request import ViewLogRequest
    from backend.security.security import view_intrusion_log

    test_user.alarm_events.clear()
    test_user.alarm_events.append(
        AlarmEvent(
            id=1,
            alarm_type=AlarmType.INTRUSION,
            timestamp=datetime.datetime(2025, 11, 28, 10, 0, 0),
            device_id=1,
            location="거실",
            description="Test",
            is_resolved=False,
        )
    )
    req = ViewLogRequest(
        user_id=test_user.user_id,
        start_date=datetime.datetime(2025, 11, 28, 9, 0, 0),
        end_date=datetime.datetime(2025, 11, 28, 11, 0, 0),
        alarm_type=AlarmType.INTRUSION,
    )
    result = view_intrusion_log(req)
    assert result["total_events"] == 1
    assert result["events"][0]["alarm_type"] == "intrusion"


def test_panic_call_monitoring_service_invalid_user():
    """Test panic_call_monitoring_service with invalid user."""
    import pytest

    from backend.security.request import PanicRequest
    from backend.security.security import panic_call_monitoring_service

    req = PanicRequest(user_id="invalid_user", location="거실")
    with pytest.raises(HTTPException) as exc_info:
        panic_call_monitoring_service(req)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_get_safehome_modes_invalid_user():
    """Test get_safehome_modes with invalid user."""
    import pytest

    from backend.security.security import get_safehome_modes

    with pytest.raises(HTTPException) as exc_info:
        get_safehome_modes("invalid_user")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_set_safehome_mode_invalid_user():
    """Test set_safehome_mode with invalid user."""
    import pytest

    from backend.common.device import SafeHomeModeType
    from backend.security.request import SetModeRequest
    from backend.security.security import set_safehome_mode

    req = SetModeRequest(user_id="invalid_user", mode_type=SafeHomeModeType.AWAY)
    with pytest.raises(HTTPException) as exc_info:
        set_safehome_mode(req)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_view_intrusion_log_invalid_user():
    """Test view_intrusion_log with invalid user."""
    import pytest

    from backend.security.request import ViewLogRequest
    from backend.security.security import view_intrusion_log

    req = ViewLogRequest(
        user_id="invalid_user", start_date=None, end_date=None, alarm_type=None
    )
    with pytest.raises(HTTPException) as exc_info:
        view_intrusion_log(req)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_configure_safety_zone_interface_invalid_user():
    """Test configure_safety_zone_interface with invalid user."""
    import pytest

    from backend.security.security import configure_safety_zone_interface

    with pytest.raises(HTTPException) as exc_info:
        configure_safety_zone_interface("invalid_user")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid user ID"


def test_get_safehome_modes_multiple_modes(test_user):
    """SafeHome 모드가 여러 개일 때 get_safehome_modes 정상 동작."""
    from backend.common.device import SafeHomeMode, SafeHomeModeType
    from backend.security.security import get_safehome_modes

    # 여러 모드 추가
    test_user.safehome_modes[SafeHomeModeType.AWAY] = SafeHomeMode(
        mode_type=SafeHomeModeType.AWAY, enabled_device_ids=[1]
    )
    test_user.safehome_modes[SafeHomeModeType.HOME] = SafeHomeMode(
        mode_type=SafeHomeModeType.HOME, enabled_device_ids=[2, 3]
    )
    result = get_safehome_modes(test_user.user_id)
    assert "modes_configuration" in result
    assert set(result["modes_configuration"].keys()) == {"away", "home"}
    assert result["modes_configuration"]["away"]["enabled_device_ids"] == [1]
    assert result["modes_configuration"]["home"]["enabled_device_ids"] == [2, 3]


def test_set_safehome_mode_multiple_devices(test_user):
    """여러 device가 있는 모드에서 set_safehome_mode 정상 동작."""
    from backend.common.device import SafeHomeMode, SafeHomeModeType
    from backend.security.request import SetModeRequest
    from backend.security.security import set_safehome_mode

    # 모드 설정
    test_user.safehome_modes[SafeHomeModeType.AWAY] = SafeHomeMode(
        mode_type=SafeHomeModeType.AWAY, enabled_device_ids=[1, 2, 3]
    )
    test_user.doors_windows_closed = True
    req = SetModeRequest(user_id=test_user.user_id, mode_type=SafeHomeModeType.AWAY)
    result = set_safehome_mode(req)
    assert result["current_mode"] == "away"
    assert set(result["armed_devices"]) == {1, 2, 3}
    for device in test_user.devices:
        assert device.is_armed is True
    assert test_user.is_system_armed is True


def test_configure_safety_zone_interface_multiple_zones_devices(test_user):
    """여러 safety zone, 여러 device가 있을 때 인터페이스 정상 동작."""
    from backend.common.user import SafetyZone
    from backend.security.security import configure_safety_zone_interface

    # 여러 zone 추가
    zone1 = SafetyZone(name="거실", devices=[test_user.devices[0]], is_armed=True)
    zone2 = SafetyZone(
        name="침실",
        devices=[test_user.devices[1], test_user.devices[2]],
        is_armed=False,
    )
    test_user.safety_zones = [zone1, zone2]
    result = configure_safety_zone_interface(test_user.user_id)
    assert "existing_safety_zones" in result
    assert len(result["existing_safety_zones"]) == 2
    assert set([z["name"] for z in result["existing_safety_zones"]]) == {"거실", "침실"}
    assert "available_devices" in result
    assert len(result["available_devices"]) == 3
