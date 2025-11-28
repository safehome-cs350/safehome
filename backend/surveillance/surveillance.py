"""Surveillance module for handling camera and sensor operations."""

import base64
import os
import sys
import threading
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from backend.common.device import CameraDB, SensorDB
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
    current_view_base64: Optional[str] = None
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

    password: str


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


def load_camera_png_as_base64() -> str:
    """Load camera image and return as base64 string."""
    camera_png_path = os.path.join(os.path.dirname(__file__), "../../img/camera.png")
    try:
        with open(camera_png_path, "rb") as image_file:
            img_str = base64.b64encode(image_file.read()).decode()
            return img_str
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Camera image not found") from None


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
                        "current_view_base64": (
                            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
                            "AAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
                        ),
                        "pan_position": 0,
                        "zoom_level": 2,
                        "current_time": 0,
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
            "description": "Failed to get camera view",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to get camera view: error message"}
                }
            },
        },
    },
)
async def display_camera_view(camera_id: int):
    """Display camera view with current settings."""
    camera = get_camera_info(camera_id)

    if not camera.is_enabled:
        raise HTTPException(status_code=400, detail="Camera is disabled")

    try:
        device_camera = get_or_create_camera(camera_id)
        view_base64 = load_camera_png_as_base64()

        return CameraViewResponse(
            camera_id=camera_id,
            name=camera.name,
            is_enabled=camera.is_enabled,
            is_online=camera.is_online,
            stream_url=f"https://example.com/stream/cam{camera_id}.m3u8",
            current_view_base64=view_base64,
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
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def set_camera_password(camera_id: int, req: CameraPasswordRequest):
    """Set password for a camera."""
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    CameraDB.update_camera(camera_id, has_password=True)
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
        404: {
            "description": "Camera not found",
            "content": {
                "application/json": {"example": {"detail": "Camera not found"}}
            },
        },
    },
)
async def delete_camera_password(camera_id: int):
    """Delete password for a camera."""
    camera_info = CameraDB.get_camera(camera_id)
    if not camera_info:
        raise HTTPException(status_code=404, detail="Camera not found")

    CameraDB.update_camera(camera_id, has_password=False)
    return CameraPasswordStatus(camera_id=camera_id, has_password=False)


@router.get(
    "/cameras/{camera_id}/thumbnails",
    response_model=List[ThumbnailShot],
    summary="UC1.f. Get camera thumbnail history",
    responses={
        200: {
            "description": "Successfully retrieved camera thumbnails",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 101,
                            "camera_id": 1,
                            "captured_at": "2025-11-19T10:00:00Z",
                            "image_url": "https://example.com/thumbs/1_1.jpg",
                        }
                    ]
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
    """List camera thumbnail history."""
    validate_camera_exists(camera_id)

    fake_thumbnails = [
        ThumbnailShot(
            id=100 + camera_id,
            camera_id=camera_id,
            captured_at="2025-11-19T10:00:00Z",
            image_url=f"https://example.com/thumbs/{camera_id}_1.jpg",
        ),
        ThumbnailShot(
            id=200 + camera_id,
            camera_id=camera_id,
            captured_at="2025-11-19T11:00:00Z",
            image_url=f"https://example.com/thumbs/{camera_id}_2.jpg",
        ),
    ]

    return fake_thumbnails


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

    # Add motion sensors
    for sensor_info in SensorDB.get_all_motion_sensors():
        sensors.append(
            SensorStatus(
                sensor_id=sensor_info.sensor_id,
                sensor_type="motion",
                is_armed=sensor_info.is_armed,
                is_triggered=sensor_info.is_triggered,
                location=sensor_info.location,
            )
        )

    # Add windoor sensors
    for sensor_info in SensorDB.get_all_windoor_sensors():
        sensors.append(
            SensorStatus(
                sensor_id=sensor_info.sensor_id,
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

    # Update state in database - no direct device manipulation
    SensorDB.update_windoor_sensor(sensor_id, is_armed=True)

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
    """Get detailed status of a sensor."""
    if sensor_type == "motion":
        sensor_info = SensorDB.get_motion_sensor(sensor_id)
        if not sensor_info:
            raise HTTPException(status_code=404, detail="Motion detector not found")

        # Return state from database only - no direct device access
        # Provide a simulated reading based on current state
        reading = 1 if sensor_info.is_triggered else 0
        return {
            "sensor_id": sensor_id,
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
            "sensor_id": sensor_id,
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
