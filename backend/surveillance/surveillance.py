from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import base64
import io
import threading
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from device.device_camera import DeviceCamera
from device.device_motion_detector import DeviceMotionDetector
from device.device_windoor_sensor import DeviceWinDoorSensor

router = APIRouter(
    prefix="/surveillance",
    tags=["surveillance"],
)


class CameraViewResponse(BaseModel):
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
    pan: Optional[int] = None
    zoom: Optional[int] = None
    
class PTZResponse(BaseModel):
    camera_id: int
    pan_position: int
    zoom_level: int
    success: bool
    message: str

class CameraPasswordRequest(BaseModel):
    password: str

class SensorStatus(BaseModel):
    sensor_id: int
    sensor_type: str
    is_armed: bool
    is_triggered: bool
    location: str

class SensorListResponse(BaseModel):
    sensors: List[SensorStatus]

class CameraPasswordStatus(BaseModel):
    camera_id: int
    has_password: bool

class ThumbnailShot(BaseModel):
    id: int
    camera_id: int
    captured_at: str
    image_url: str

class CameraStateResponse(BaseModel):
    camera_id: int
    is_enabled: bool

camera_instances = {}
camera_instances_lock = threading.Lock()

def get_or_create_camera(camera_id: int) -> DeviceCamera:
    with camera_instances_lock:
        if camera_id not in camera_instances:
            camera_instances[camera_id] = DeviceCamera()
            camera_instances[camera_id].set_id(camera_id)
        return camera_instances[camera_id]

def load_camera_png_as_base64() -> str:
    camera_png_path = os.path.join(os.path.dirname(__file__), '../../img/camera.png')
    try:
        with open(camera_png_path, 'rb') as image_file:
            img_str = base64.b64encode(image_file.read()).decode()
            return img_str
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Camera image not found")

motion_detectors = {}
windoor_sensors = {}
sensors_lock = threading.Lock()

def get_or_create_motion_detector(sensor_id: int) -> DeviceMotionDetector:
    with sensors_lock:
        if sensor_id not in motion_detectors:
            motion_detectors[sensor_id] = DeviceMotionDetector()
        return motion_detectors[sensor_id]

def get_or_create_windoor_sensor(sensor_id: int) -> DeviceWinDoorSensor:
    with sensors_lock:
        if sensor_id not in windoor_sensors:
            windoor_sensors[sensor_id] = DeviceWinDoorSensor()
        return windoor_sensors[sensor_id]

camera_configs = {
    1: {"name": "거실 카메라", "location": "거실", "is_enabled": True, "has_password": False},
    2: {"name": "현관 카메라", "location": "현관", "is_enabled": True, "has_password": True},
    3: {"name": "침실 카메라", "location": "침실", "is_enabled": False, "has_password": False},
}

sensor_locations = {
    "motion": {1: "거실", 2: "현관", 3: "침실"},
    "windoor": {1: "정문", 2: "뒷문", 3: "거실 창문", 4: "침실 창문"}
}

def get_camera_config(camera_id: int) -> dict:
    if camera_id not in camera_configs:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera_configs[camera_id]

def validate_camera_exists(camera_id: int) -> None:
    get_camera_config(camera_id)

class CameraListItem(BaseModel):
    camera_id: int
    name: str
    location: str
    is_enabled: bool
    is_online: bool
    has_password: bool

class CameraListResponse(BaseModel):
    cameras: List[CameraListItem]

@router.get("/cameras", response_model=CameraListResponse)
async def list_cameras():
    cameras = []
    
    for camera_id, config in camera_configs.items():
        try:
            device_camera = get_or_create_camera(camera_id)
            is_online = True 
        except Exception:
            is_online = False
        
        cameras.append(CameraListItem(
            camera_id=camera_id,
            name=config["name"],
            location=config["location"],
            is_enabled=config["is_enabled"],
            is_online=is_online,
            has_password=config["has_password"],
        ))
    
    return CameraListResponse(cameras=cameras)


@router.get("/cameras/{camera_id}/view", response_model=CameraViewResponse)
async def display_camera_view(camera_id: int):
    config = get_camera_config(camera_id)

    if not config["is_enabled"]:
        raise HTTPException(status_code=400, detail="Camera is disabled")

    try:
        device_camera = get_or_create_camera(camera_id)
        view_base64 = load_camera_png_as_base64()
        
        return CameraViewResponse(
            camera_id=camera_id,
            name=config["name"],
            is_enabled=config["is_enabled"],
            is_online=True,
            stream_url=f"https://example.com/stream/cam{camera_id}.m3u8", 
            current_view_base64=view_base64,
            pan_position=device_camera.pan,
            zoom_level=device_camera.zoom,
            current_time=device_camera.time,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get camera view: {str(e)}")



@router.post("/cameras/{camera_id}/ptz", response_model=PTZResponse)
async def control_camera_ptz(camera_id: int, cmd: PTZCommand):
    config = get_camera_config(camera_id)

    if not config["is_enabled"]:
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
                else:
                    break
                    
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
                else:
                    break
                    
            if not success:
                messages.append(f"Zoom limit reached at {current_zoom}")

        message = "; ".join(messages) if messages else "PTZ command completed successfully"
        
        return PTZResponse(
            camera_id=camera_id,
            pan_position=device_camera.pan,
            zoom_level=device_camera.zoom,
            success=success,
            message=message,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PTZ control failed: {str(e)}")


@router.put("/cameras/{camera_id}/password", response_model=CameraPasswordStatus)
async def set_camera_password(camera_id: int, req: CameraPasswordRequest):
    config = get_camera_config(camera_id)

    camera_configs[camera_id]["has_password"] = True

    return CameraPasswordStatus(camera_id=camera_id, has_password=True)


@router.delete("/cameras/{camera_id}/password", response_model=CameraPasswordStatus)
async def delete_camera_password(camera_id: int):
    config = get_camera_config(camera_id)

    camera_configs[camera_id]["has_password"] = False
    return CameraPasswordStatus(camera_id=camera_id, has_password=False)


@router.get("/cameras/{camera_id}/thumbnails", response_model=List[ThumbnailShot])
async def list_thumbnails(camera_id: int):
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


@router.post("/cameras/{camera_id}/enable", response_model=CameraStateResponse)
async def enable_camera(camera_id: int):
    config = get_camera_config(camera_id)
    camera_configs[camera_id]["is_enabled"] = True
    return CameraStateResponse(camera_id=camera_id, is_enabled=True)


@router.post("/cameras/{camera_id}/disable", response_model=CameraStateResponse)
async def disable_camera(camera_id: int):
    config = get_camera_config(camera_id)
    camera_configs[camera_id]["is_enabled"] = False
    return CameraStateResponse(camera_id=camera_id, is_enabled=False)


@router.get("/sensors", response_model=SensorListResponse)
async def list_all_sensors():
    sensors = []
    
    for sensor_id, location in sensor_locations["motion"].items():
        try:
            motion_detector = get_or_create_motion_detector(sensor_id)
            sensors.append(SensorStatus(
                sensor_id=sensor_id,
                sensor_type="motion",
                is_armed=motion_detector.armed,
                is_triggered=motion_detector.detected,
                location=location,
            ))
        except Exception:
            sensors.append(SensorStatus(
                sensor_id=sensor_id,
                sensor_type="motion",
                is_armed=False,
                is_triggered=False,
                location=location,
            ))
    
    for sensor_id, location in sensor_locations["windoor"].items():
        try:
            windoor_sensor = get_or_create_windoor_sensor(sensor_id)
            sensors.append(SensorStatus(
                sensor_id=sensor_id,
                sensor_type="windoor",
                is_armed=windoor_sensor.armed,
                is_triggered=windoor_sensor.opened,
                location=location,
            ))
        except Exception:
            sensors.append(SensorStatus(
                sensor_id=sensor_id,
                sensor_type="windoor",
                is_armed=False,
                is_triggered=False,
                location=location,
            ))
    
    return SensorListResponse(sensors=sensors)


@router.post("/sensors/motion/{sensor_id}/arm")
async def arm_motion_detector(sensor_id: int):
    if sensor_id not in sensor_locations["motion"]:
        raise HTTPException(status_code=404, detail="Motion detector not found")
    
    motion_detector = get_or_create_motion_detector(sensor_id)
    motion_detector.arm()
    
    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_armed": True}


@router.post("/sensors/motion/{sensor_id}/disarm")
async def disarm_motion_detector(sensor_id: int):
    if sensor_id not in sensor_locations["motion"]:
        raise HTTPException(status_code=404, detail="Motion detector not found")
    
    motion_detector = get_or_create_motion_detector(sensor_id)
    motion_detector.disarm()
    
    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_armed": False}


@router.post("/sensors/motion/{sensor_id}/trigger")
async def trigger_motion_detector(sensor_id: int):
    if sensor_id not in sensor_locations["motion"]:
        raise HTTPException(status_code=404, detail="Motion detector not found")
    
    motion_detector = get_or_create_motion_detector(sensor_id)
    motion_detector.intrude()
    
    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_triggered": True}


@router.post("/sensors/motion/{sensor_id}/release")
async def release_motion_detector(sensor_id: int):
    if sensor_id not in sensor_locations["motion"]:
        raise HTTPException(status_code=404, detail="Motion detector not found")
    
    motion_detector = get_or_create_motion_detector(sensor_id)
    motion_detector.release()
    
    return {"sensor_id": sensor_id, "sensor_type": "motion", "is_triggered": False}


@router.post("/sensors/windoor/{sensor_id}/arm")
async def arm_windoor_sensor(sensor_id: int):
    if sensor_id not in sensor_locations["windoor"]:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")
    
    windoor_sensor = get_or_create_windoor_sensor(sensor_id)
    windoor_sensor.arm()
    
    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_armed": True}


@router.post("/sensors/windoor/{sensor_id}/disarm")
async def disarm_windoor_sensor(sensor_id: int):
    if sensor_id not in sensor_locations["windoor"]:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")
    
    windoor_sensor = get_or_create_windoor_sensor(sensor_id)
    windoor_sensor.disarm()
    
    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_armed": False}


@router.post("/sensors/windoor/{sensor_id}/open")
async def open_windoor_sensor(sensor_id: int):
    if sensor_id not in sensor_locations["windoor"]:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")
    
    windoor_sensor = get_or_create_windoor_sensor(sensor_id)
    windoor_sensor.intrude()
    
    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_opened": True}


@router.post("/sensors/windoor/{sensor_id}/close")
async def close_windoor_sensor(sensor_id: int):
    if sensor_id not in sensor_locations["windoor"]:
        raise HTTPException(status_code=404, detail="Window/door sensor not found")
    
    windoor_sensor = get_or_create_windoor_sensor(sensor_id)
    windoor_sensor.release()
    
    return {"sensor_id": sensor_id, "sensor_type": "windoor", "is_opened": False}


@router.get("/sensors/{sensor_type}/{sensor_id}/status")
async def get_sensor_status(sensor_type: str, sensor_id: int):
    if sensor_type == "motion":
        if sensor_id not in sensor_locations["motion"]:
            raise HTTPException(status_code=404, detail="Motion detector not found")
        
        motion_detector = get_or_create_motion_detector(sensor_id)
        return {
            "sensor_id": sensor_id,
            "sensor_type": "motion",
            "location": sensor_locations["motion"][sensor_id],
            "is_armed": motion_detector.armed,
            "is_triggered": motion_detector.detected,
            "reading": motion_detector.read(),
        }
    
    elif sensor_type == "windoor":
        if sensor_id not in sensor_locations["windoor"]:
            raise HTTPException(status_code=404, detail="Window/door sensor not found")
        
        windoor_sensor = get_or_create_windoor_sensor(sensor_id)
        return {
            "sensor_id": sensor_id,
            "sensor_type": "windoor",
            "location": sensor_locations["windoor"][sensor_id],
            "is_armed": windoor_sensor.armed,
            "is_opened": windoor_sensor.opened,
            "reading": windoor_sensor.read(),
        }
    
    else:
        raise HTTPException(status_code=400, detail="Invalid sensor type. Use 'motion' or 'windoor'.")
