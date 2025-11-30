"""Surveillance module for handling camera and sensor operations."""

import os
import sys
import threading
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from backend.common.device import AlarmType, CameraDB, SensorDB
from backend.common.user import UserDB
from device.device_camera import DeviceCamera

router = APIRouter(
    prefix="/surveillance",
    tags=["surveillance"],
)


class CameraViewResponse(BaseModel):
    """Response model for camera view data."""

    camera_id: int
    name: str
    is_enabled: bool
    is_online: bool
    stream_url: str
    image_url: str
    pan_position: int = 0
    zoom_level: int = 2
    current_time: int = 0


class PTZCommand(BaseModel):
    """Command model for PTZ operations."""

    pan: Optional[int] = None
    zoom: Optional[int] = None


class PTZResponse(BaseModel):
    """Response model for PTZ operations."""

    camera_id: int
    pan_position: int
    zoom_level: int
    success: bool
    message: str


class CameraPasswordRequest(BaseModel):
    """Request model for camera password operations."""

    old_password: str | None = None
    new_password: str


class SensorStatus(BaseModel):
    """Model for sensor status information."""

    sensor_id: int
    sensor_type: str
    is_armed: bool
    is_triggered: bool
    location: str


class SensorListResponse(BaseModel):
    """Response model for sensor list."""

    sensors: List[SensorStatus]


class CameraPasswordStatus(BaseModel):
    """Response model for camera password status."""

    camera_id: int
    has_password: bool


class ThumbnailShot(BaseModel):
    """Model for camera thumbnail information."""

    id: int
    camera_id: int
    captured_at: str
    image_url: str


class CameraStateResponse(BaseModel):
    """Response model for camera state."""

    camera_id: int
    is_enabled: bool


camera_instances = {}
camera_instances_lock = threading.Lock()


def get_or_create_camera(camera_id: int) -> DeviceCamera:
    """Get or create a camera instance."""
    with camera_instances_lock:
        if camera_id not in camera_instances:
            camera_instances[camera_id] = DeviceCamera()
            camera_instances[camera_id].set_id(camera_id)
        return camera_instances[camera_id]


# Default user for demo purposes - in real implementation this would come
# from authentication
DEFAULT_USER_ID = "homeowner1"


def get_default_user():
    """Get the default user for demo purposes."""
    user = UserDB.find_user_by_id(DEFAULT_USER_ID)
    if not user:
        raise HTTPException(status_code=500, detail="Default user not found")
    return user


def get_camera_info(camera_id: int):
    """Get camera info from CameraDB."""
    camera = CameraDB.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


def validate_camera_exists(camera_id: int) -> None:
    """Validate that camera exists."""
    get_camera_info(camera_id)


class CameraListItem(BaseModel):
    """Model for camera list item."""

    camera_id: int
    name: str
    location: str
    is_enabled: bool
    is_online: bool
    has_password: bool


class CameraListResponse(BaseModel):
    """Response model for camera list."""

    cameras: List[CameraListItem]


@router.get(
    "/cameras",
    response_model=CameraListResponse,
    summary="UC1.a. List all cameras",
    responses={
        200: {
            "description": "Successfully retrieved camera list",
            "content": {
                "application/json": {
                    "example": {
                        "cameras": [
                            {
                                "camera_id": 1,
                                "name": "거실 카메라",
                                "location": "거실",
                                "is_enabled": True,
                                "is_online": True,
                                "has_password": False,
                            }
                        ]
                    }
                }
            },
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
async def list_cameras():
    """List all available cameras."""
    cameras = []

    for camera_info in CameraDB.get_all_cameras():
        try:
            get_or_create_camera(camera_info.camera_id)
            is_online = True
        except Exception:
            is_online = False

        cameras.append(
            CameraListItem(
                camera_id=camera_info.camera_id,
                name=camera_info.name,
                location=camera_info.location,
                is_enabled=camera_info.is_enabled,
                is_online=is_online,
                has_password=camera_info.has_password,
            )
        )

    return CameraListResponse(cameras=cameras)


@router.get(
    "/cameras/{camera_id}/view",
    response_model=CameraViewResponse,
    summary="UC1.b. Display camera view",
    responses={
        200: {
            "description": "Successfully retrieved camera view",
            "content": {
                "application/json": {
                    "example": {
                        "camera_id": 1,
                        "name": "거실 카메라",
                        "is_enabled": True,
                        "is_online": True,
                        "stream_url": "https://example.com/stream/cam1.m3u8",
                        "image_url": "/camera1.jpg",
                        "pan_position": 0,
                        "zoom_level": 2,
                        "current_time": 0,
                    }
                }
            },
        },
        400: {
            "description": "Camera is disabled or password required/incorrect",
            "content": {
                "application/json": {"example": {"detail": "Camera is disabled"}}
            },
        },
        401: {
            "description": "Password required or incorrect",
            "content": {
                "application/json": {"example": {"detail": "Password required"}}
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
        500: {
            "description": "Failed to get camera view",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to get camera view: error message"}
                }
            },
        },
    },
)
async def display_camera_view(camera_id: int, password: str | None = None):
    """Display camera view with current settings.

    Args:
        camera_id: Camera identifier
        password: Optional password if camera is password protected
    """
    camera = get_camera_info(camera_id)

    if not camera.is_enabled:
        raise HTTPException(status_code=400, detail="Camera is disabled")

    if camera.has_password:
        if not password:
            raise HTTPException(
                status_code=401, detail="Password required to view this camera"
            )
        if camera.password != password:
            raise HTTPException(status_code=401, detail="Incorrect password")

    try:
        device_camera = get_or_create_camera(camera_id)
        return CameraViewResponse(
            camera_id=camera_id,
            name=camera.name,
            is_enabled=camera.is_enabled,
            is_online=camera.is_online,
            stream_url=f"https://example.com/stream/cam{camera_id}.m3u8",
            image_url=camera.url,
            pan_position=device_camera.pan,
            zoom_level=device_camera.zoom,
            current_time=device_camera.time,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get camera view: {str(e)}"
        ) from e


@router.post(
    "/cameras/{camera_id}/ptz",
    response_model=PTZResponse,
    summary="UC1.c. Control camera PTZ (Pan-Tilt-Zoom)",
    responses={
        200: {
            "description": "Successfully controlled camera PTZ",
            "content": {
                "application/json": {
                    "example": {
                        "camera_id": 1,
                        "pan_position": 2,
                        "zoom_level": 3,
                        "success": True,
                        "message": "PTZ command completed successfully",
                    }
                }
            },
        },
        400: {
            "description": "Camera is disabled",
            "content": {
                "application/json": {"example": {"detail": "Camera is disabled"}}
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
        500: {
            "description": "PTZ control failed",
            "content": {
                "application/json": {
                    "example": {"detail": "PTZ control failed: error message"}
                }
            },
        },
    },
)
async def control_camera_ptz(camera_id: int, cmd: PTZCommand):
    """Control camera PTZ (Pan-Tilt-Zoom) operations."""
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    if not camera_info.is_enabled:
        raise HTTPException(status_code=400, detail="Camera is disabled")

    try:
        device_camera = get_or_create_camera(camera_id)
        success = True
        messages = []

        if cmd.pan is not None:
            current_pan = device_camera.pan
            target_pan = cmd.pan

            while current_pan != target_pan and success:
                if current_pan < target_pan:
                    success = device_camera.pan_right()
                    current_pan = device_camera.pan
                elif current_pan > target_pan:
                    success = device_camera.pan_left()
                    current_pan = device_camera.pan

            if not success:
                messages.append(f"Pan limit reached at {current_pan}")

        if cmd.zoom is not None:
            current_zoom = device_camera.zoom
            target_zoom = cmd.zoom

            while current_zoom != target_zoom and success:
                if current_zoom < target_zoom:
                    success = device_camera.zoom_in()
                    current_zoom = device_camera.zoom
                elif current_zoom > target_zoom:
                    success = device_camera.zoom_out()
                    current_zoom = device_camera.zoom

            if not success:
                messages.append(f"Zoom limit reached at {current_zoom}")

        message = (
            "; ".join(messages) if messages else "PTZ command completed successfully"
        )

        return PTZResponse(
            camera_id=camera_id,
            pan_position=device_camera.pan,
            zoom_level=device_camera.zoom,
            success=success,
            message=message,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"PTZ control failed: {str(e)}"
        ) from e


@router.put(
    "/cameras/{camera_id}/password",
    response_model=CameraPasswordStatus,
    summary="UC1.d. Set camera password",
    responses={
        200: {
            "description": "Successfully set camera password",
            "content": {
                "application/json": {"example": {"camera_id": 1, "has_password": True}}
            },
        },
        401: {
            "description": "Password required or incorrect",
            "content": {
                "application/json": {"example": {"detail": "Old password required"}}
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def set_camera_password(camera_id: int, req: CameraPasswordRequest):
    """Set password for a camera.

    Args:
        camera_id: Camera identifier
        req: Password request with old_password (if changing) and new_password
    """
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    # If camera already has a password, verify old password
    if camera_info.has_password:
        if not req.old_password:
            raise HTTPException(
                status_code=401, detail="Old password required to change password"
            )
        if camera_info.password != req.old_password:
            raise HTTPException(status_code=401, detail="Incorrect old password")

    CameraDB.update_camera(camera_id, has_password=True, password=req.new_password)
    return CameraPasswordStatus(camera_id=camera_id, has_password=True)


@router.delete(
    "/cameras/{camera_id}/password",
    response_model=CameraPasswordStatus,
    summary="UC1.e. Delete camera password",
    responses={
        200: {
            "description": "Successfully deleted camera password",
            "content": {
                "application/json": {"example": {"camera_id": 1, "has_password": False}}
            },
        },
        401: {
            "description": "Password required or incorrect",
            "content": {
                "application/json": {"example": {"detail": "Password required"}}
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def delete_camera_password(camera_id: int, password: str | None = None):
    """Delete password for a camera.

    Args:
        camera_id: Camera identifier
        password: Password to verify before deletion
    """
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    if camera_info.has_password:
        if not password:
            raise HTTPException(
                status_code=401, detail="Password required to delete camera password"
            )
        if camera_info.password != password:
            raise HTTPException(status_code=401, detail="Incorrect password")

    CameraDB.update_camera(camera_id, has_password=False, password=None)
    return CameraPasswordStatus(camera_id=camera_id, has_password=False)


@router.get(
    "/cameras/{camera_id}/thumbnails",
    response_model=ThumbnailShot,
    summary="UC1.f. Get camera thumbnail",
    responses={
        200: {
            "description": "Successfully retrieved camera thumbnail",
            "content": {
                "application/json": {
                    "example": {
                        "id": 101,
                        "camera_id": 1,
                        "captured_at": "2025-11-19T10:00:00Z",
                        "image_url": "/camera1.jpg",
                    }
                }
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def list_thumbnails(camera_id: int):
    """Get camera thumbnail (only one per camera)."""
    validate_camera_exists(camera_id)

    url = CameraDB.get_url(camera_id)
    thumbnail = ThumbnailShot(
        id=100 + camera_id,
        camera_id=camera_id,
        captured_at="2025-11-19T10:00:00Z",
        image_url=url,
    )

    return thumbnail


@router.post(
    "/cameras/{camera_id}/enable",
    response_model=CameraStateResponse,
    summary="UC1.g. Enable camera",
    responses={
        200: {
            "description": "Successfully enabled camera",
            "content": {
                "application/json": {"example": {"camera_id": 1, "is_enabled": True}}
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def enable_camera(camera_id: int):
    """Enable a camera."""
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    CameraDB.update_camera(camera_id, is_enabled=True)
    return CameraStateResponse(camera_id=camera_id, is_enabled=True)


@router.post(
    "/cameras/{camera_id}/disable",
    response_model=CameraStateResponse,
    summary="UC1.h. Disable camera",
    responses={
        200: {
            "description": "Successfully disabled camera",
            "content": {
                "application/json": {"example": {"camera_id": 1, "is_enabled": False}}
            },
        },
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def disable_camera(camera_id: int):
    """Disable a camera."""
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    CameraDB.update_camera(camera_id, is_enabled=False)
    return CameraStateResponse(camera_id=camera_id, is_enabled=False)


@router.get(
    "/sensors",
    response_model=SensorListResponse,
    summary="UC2.a. List all sensors",
    responses={
        200: {
            "description": "Successfully retrieved sensor list",
            "content": {
                "application/json": {
                    "example": {
                        "sensors": [
                            {
                                "sensor_id": 1,
                                "sensor_type": "motion",
                                "is_armed": False,
                                "is_triggered": False,
                                "location": "거실",
                            }
                        ]
                    }
                }
            },
        }
    },
)
async def list_all_sensors():
    """List all available sensors."""
    sensors = []

    # Add motion sensors - use dictionary key as unique sensor_id
    for sensor_key, sensor_info in SensorDB.motion_sensors.items():
        sensors.append(
            SensorStatus(
                sensor_id=sensor_key,  # Use dictionary key for unique ID
                sensor_type="motion",
                is_armed=sensor_info.is_armed,
                is_triggered=sensor_info.is_triggered,
                location=sensor_info.location,
            )
        )

    # Add windoor sensors - use dictionary key as unique sensor_id
    for sensor_key, sensor_info in SensorDB.windoor_sensors.items():
        sensors.append(
            SensorStatus(
                sensor_id=sensor_key,  # Use dictionary key for unique ID
                sensor_type="windoor",
                is_armed=sensor_info.is_armed,
                is_triggered=sensor_info.is_opened,
                location=sensor_info.location,
            )
        )

    return SensorListResponse(sensors=sensors)


@router.post(
    "/sensors/motion/{sensor_id}/arm",
    summary="UC2.b. Arm motion sensor",
    responses={
        200: {
            "description": "Successfully armed motion sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "motion",
                        "is_armed": True,
                    }
                }
            },
        },
        404: {
            "description": "Motion detector not found",
            "content": {
                "application/json": {"example": {"detail": "Motion detector not found"}}
            },
        },
    },
)
async def arm_motion_detector(sensor_id: int):
    """Arm a motion detector sensor."""
    sensor_info = SensorDB.get_motion_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Motion detector not found")

    # Update state in database - no direct device manipulation
    SensorDB.update_motion_sensor(sensor_id, is_armed=True)

    # Log the sensor arming event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Motion sensor {sensor_id} armed",
    )

    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_armed": True}


@router.post(
    "/sensors/motion/{sensor_id}/disarm",
    summary="UC2.c. Disarm motion sensor",
    responses={
        200: {
            "description": "Successfully disarmed motion sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "motion",
                        "is_armed": False,
                    }
                }
            },
        },
        404: {
            "description": "Motion detector not found",
            "content": {
                "application/json": {"example": {"detail": "Motion detector not found"}}
            },
        },
    },
)
async def disarm_motion_detector(sensor_id: int):
    """Disarm a motion detector sensor."""
    sensor_info = SensorDB.get_motion_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Motion detector not found")

    # Update state in database - no direct device manipulation
    SensorDB.update_motion_sensor(sensor_id, is_armed=False)

    # Log the sensor disarming event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Motion sensor {sensor_id} disarmed",
    )

    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_armed": False}


@router.post(
    "/sensors/motion/{sensor_id}/trigger",
    summary="UC2.d. Trigger motion sensor (simulate motion detection)",
    responses={
        200: {
            "description": "Successfully triggered motion sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "motion",
                        "is_triggered": True,
                    }
                }
            },
        },
        404: {
            "description": "Motion detector not found",
            "content": {
                "application/json": {"example": {"detail": "Motion detector not found"}}
            },
        },
    },
)
async def trigger_motion_detector(sensor_id: int):
    """Trigger motion detection on a motion sensor."""
    sensor_info = SensorDB.get_motion_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Motion detector not found")

    # Update state in database - this would typically come from client/tester
    SensorDB.update_motion_sensor(sensor_id, is_triggered=True)

    # Log the sensor trigger event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Motion sensor {sensor_id} triggered",
    )

    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_triggered": True}


@router.post(
    "/sensors/motion/{sensor_id}/release",
    summary="UC2.e. Release motion sensor (clear motion detection)",
    responses={
        200: {
            "description": "Successfully released motion sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "motion",
                        "is_triggered": False,
                    }
                }
            },
        },
        404: {
            "description": "Motion detector not found",
            "content": {
                "application/json": {"example": {"detail": "Motion detector not found"}}
            },
        },
    },
)
async def release_motion_detector(sensor_id: int):
    """Release motion detection on a motion sensor."""
    sensor_info = SensorDB.get_motion_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Motion detector not found")

    # Update state in database - this would typically come from client/tester
    SensorDB.update_motion_sensor(sensor_id, is_triggered=False)

    # Log the sensor release event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Motion sensor {sensor_id} released",
    )

    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_triggered": False}


@router.post(
    "/sensors/windoor/{sensor_id}/arm",
    summary="UC2.f. Arm window/door sensor",
    responses={
        200: {
            "description": "Successfully armed window/door sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "windoor",
                        "is_armed": True,
                    }
                }
            },
        },
        400: {
            "description": "Doors and windows not closed",
            "content": {
                "application/json": {
                    "example": {"detail": "doors and windows not closed"}
                }
            },
        },
        404: {
            "description": "Window/door sensor not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Window/door sensor not found"}
                }
            },
        },
    },
)
async def arm_windoor_sensor(sensor_id: int):
    """Arm a window/door sensor."""
    sensor_info = SensorDB.get_windoor_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")

    # Check if door/window is open before allowing arming
    if sensor_info.is_opened:
        raise HTTPException(status_code=400, detail="doors and windows not closed")

    # Update state in database - no direct device manipulation
    SensorDB.update_windoor_sensor(sensor_id, is_armed=True)

    # Log the sensor arming event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Windoor sensor {sensor_id} armed",
    )

    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_armed": True}


@router.post(
    "/sensors/windoor/{sensor_id}/disarm",
    summary="UC2.g. Disarm window/door sensor",
    responses={
        200: {
            "description": "Successfully disarmed window/door sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "windoor",
                        "is_armed": False,
                    }
                }
            },
        },
        404: {
            "description": "Window/door sensor not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Window/door sensor not found"}
                }
            },
        },
    },
)
async def disarm_windoor_sensor(sensor_id: int):
    """Disarm a window/door sensor."""
    sensor_info = SensorDB.get_windoor_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")

    # Update state in database - no direct device manipulation
    SensorDB.update_windoor_sensor(sensor_id, is_armed=False)

    # Log the sensor disarming event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Windoor sensor {sensor_id} disarmed",
    )

    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_armed": False}


@router.post(
    "/sensors/windoor/{sensor_id}/open",
    summary="UC2.h. Open window/door sensor (simulate opening)",
    responses={
        200: {
            "description": "Successfully opened window/door sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "windoor",
                        "is_opened": True,
                    }
                }
            },
        },
        404: {
            "description": "Window/door sensor not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Window/door sensor not found"}
                }
            },
        },
    },
)
async def open_windoor_sensor(sensor_id: int):
    """Simulate opening a window/door sensor."""
    sensor_info = SensorDB.get_windoor_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")

    # Update state in database - this would typically come from client/tester
    SensorDB.update_windoor_sensor(sensor_id, is_opened=True)

    # Log the sensor open event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.DOOR_WINDOW_OPEN,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Windoor sensor {sensor_id} opened",
    )

    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_opened": True}


@router.post(
    "/sensors/windoor/{sensor_id}/close",
    summary="UC2.i. Close window/door sensor (simulate closing)",
    responses={
        200: {
            "description": "Successfully closed window/door sensor",
            "content": {
                "application/json": {
                    "example": {
                        "sensor_id": 1,
                        "sensor_type": "windoor",
                        "is_opened": False,
                    }
                }
            },
        },
        404: {
            "description": "Window/door sensor not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Window/door sensor not found"}
                }
            },
        },
    },
)
async def close_windoor_sensor(sensor_id: int):
    """Simulate closing a window/door sensor."""
    sensor_info = SensorDB.get_windoor_sensor(sensor_id)
    if not sensor_info:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")

    # Update state in database - this would typically come from client/tester
    SensorDB.update_windoor_sensor(sensor_id, is_opened=False)

    # Log the sensor close event
    user = get_default_user()
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=sensor_id,
        location=sensor_info.location,
        description=f"Windoor sensor {sensor_id} closed",
    )

    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_opened": False}


@router.get(
    "/sensors/{sensor_type}/{sensor_id}/status",
    summary="UC2.j. Get detailed sensor status",
    responses={
        200: {
            "description": "Successfully retrieved sensor status",
            "content": {
                "application/json": {
                    "examples": {
                        "motion_sensor": {
                            "summary": "Motion sensor status",
                            "value": {
                                "sensor_id": 1,
                                "sensor_type": "motion",
                                "location": "거실",
                                "is_armed": True,
                                "is_triggered": False,
                                "reading": 0,
                            },
                        },
                        "windoor_sensor": {
                            "summary": "Window/door sensor status",
                            "value": {
                                "sensor_id": 1,
                                "sensor_type": "windoor",
                                "location": "정문",
                                "is_armed": True,
                                "is_opened": False,
                                "reading": 0,
                            },
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid sensor type",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid sensor type. Use 'motion' or 'windoor'."
                    }
                }
            },
        },
        404: {
            "description": "Sensor not found",
            "content": {
                "application/json": {
                    "examples": {
                        "motion_not_found": {
                            "summary": "Motion detector not found",
                            "value": {"detail": "Motion detector not found"},
                        },
                        "windoor_not_found": {
                            "summary": "Window/door sensor not found",
                            "value": {"detail": "Window/door sensor not found"},
                        },
                    }
                }
            },
        },
    },
)
async def get_sensor_status(sensor_type: str, sensor_id: int):
    """Get detailed status of a sensor.

    sensor_id is the dictionary key (unique identifier) for the sensor.
    """
    if sensor_type == "motion":
        sensor_info = SensorDB.get_motion_sensor(sensor_id)
        if not sensor_info:
            raise HTTPException(status_code=404, detail="Motion detector not found")

        # Return state from database only - no direct device access
        # Provide a simulated reading based on current state
        reading = 1 if sensor_info.is_triggered else 0
        return {
            "sensor_id": sensor_id,  # Dictionary key (unique identifier)
            "sensor_type": "motion",
            "location": sensor_info.location,
            "is_armed": sensor_info.is_armed,
            "is_triggered": sensor_info.is_triggered,
            "reading": reading,
        }

    elif sensor_type == "windoor":
        sensor_info = SensorDB.get_windoor_sensor(sensor_id)
        if not sensor_info:
            raise HTTPException(status_code=404, detail="Window/door sensor not found")

        # Return state from database only - no direct device access
        # Provide a simulated reading based on current state
        reading = 1 if sensor_info.is_opened else 0
        return {
            "sensor_id": sensor_id,  # Dictionary key (unique identifier)
            "sensor_type": "windoor",
            "location": sensor_info.location,
            "is_armed": sensor_info.is_armed,
            "is_opened": sensor_info.is_opened,
            "reading": reading,
        }

    else:
        raise HTTPException(
            status_code=400, detail="Invalid sensor type. Use 'motion' or 'windoor'."
        )
