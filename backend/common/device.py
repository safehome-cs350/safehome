"""Device."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DeviceType(Enum):
    """Device Type Enum."""

    CAMERA = "camera"
    SENSOR = "sensor"


class SafeHomeModeType(Enum):
    """SafeHome Mode Type Enum."""

    HOME = "home"
    AWAY = "away"
    OVERNIGHT_TRAVEL = "overnight_travel"
    EXTENDED_TRAVEL = "extended_travel"
    GUEST_HOME = "guest_home"


class AlarmType(Enum):
    """Alarm Type Enum."""

    INTRUSION = "intrusion"
    SENSOR_FAILURE = "sensor_failure"
    PANIC = "panic"
    DOOR_WINDOW_OPEN = "door_window_open"


@dataclass
class AlarmEvent:
    """Alarm Event Log Entry."""

    id: int
    timestamp: datetime
    alarm_type: AlarmType
    device_id: int | None
    location: str
    description: str
    is_resolved: bool = False


@dataclass
class Device:
    """Device."""

    type: DeviceType
    id: int


@dataclass
class SafetyZone:
    """Safety Zone."""

    name: str
    devices: list[Device]
    is_armed: bool


@dataclass
class SafeHomeMode:
    """SafeHome Mode Configuration."""

    mode_type: SafeHomeModeType
    enabled_device_ids: list[int]


@dataclass
class CameraInfo:
    """Camera information."""

    camera_id: int
    name: str
    location: str
    is_enabled: bool
    is_online: bool = True
    has_password: bool = False
    password: str | None = None


@dataclass
class SensorInfo:
    """Sensor information."""

    sensor_id: int
    sensor_type: str  # "motion" or "windoor"
    location: str
    is_armed: bool = False
    is_triggered: bool = False
    is_opened: bool = False  # For windoor sensors only


@dataclass
class CameraDB:
    """Camera database class."""

    cameras = {
        1: CameraInfo(
            camera_id=1,
            name="거실 카메라",
            location="거실",
            is_enabled=True,
            has_password=False,
            password=None,
        ),
        2: CameraInfo(
            camera_id=2,
            name="현관 카메라",
            location="현관",
            is_enabled=True,
            has_password=True,
            password="camera123",
        ),
        3: CameraInfo(
            camera_id=3,
            name="침실 카메라",
            location="침실",
            is_enabled=False,
            has_password=False,
            password=None,
        ),
    }

    @classmethod
    def get_camera(cls, camera_id: int) -> CameraInfo | None:
        """Get camera by ID."""
        return cls.cameras.get(camera_id)

    @classmethod
    def get_all_cameras(cls) -> list[CameraInfo]:
        """Get all cameras."""
        return list(cls.cameras.values())

    @classmethod
    def update_camera(cls, camera_id: int, **kwargs) -> bool:
        """Update camera configuration."""
        if camera_id in cls.cameras:
            for key, value in kwargs.items():
                if hasattr(cls.cameras[camera_id], key):
                    setattr(cls.cameras[camera_id], key, value)
            return True
        return False


@dataclass
class SensorDB:
    """Sensor database class."""

    motion_sensors = {
        1: SensorInfo(sensor_id=1, sensor_type="motion", location="거실"),
        2: SensorInfo(sensor_id=2, sensor_type="motion", location="현관"),
        3: SensorInfo(sensor_id=3, sensor_type="motion", location="침실"),
    }

    windoor_sensors = {
        1: SensorInfo(sensor_id=1, sensor_type="windoor", location="정문"),
        2: SensorInfo(sensor_id=2, sensor_type="windoor", location="뒷문"),
        3: SensorInfo(sensor_id=3, sensor_type="windoor", location="거실 창문"),
        4: SensorInfo(sensor_id=4, sensor_type="windoor", location="침실 창문"),
    }

    @classmethod
    def get_motion_sensor(cls, sensor_id: int) -> SensorInfo | None:
        """Get motion sensor by ID."""
        return cls.motion_sensors.get(sensor_id)

    @classmethod
    def get_windoor_sensor(cls, sensor_id: int) -> SensorInfo | None:
        """Get windoor sensor by ID."""
        return cls.windoor_sensors.get(sensor_id)

    @classmethod
    def get_all_motion_sensors(cls) -> list[SensorInfo]:
        """Get all motion sensors."""
        return list(cls.motion_sensors.values())

    @classmethod
    def get_all_windoor_sensors(cls) -> list[SensorInfo]:
        """Get all windoor sensors."""
        return list(cls.windoor_sensors.values())

    @classmethod
    def update_motion_sensor(cls, sensor_id: int, **kwargs) -> bool:
        """Update motion sensor configuration."""
        if sensor_id in cls.motion_sensors:
            for key, value in kwargs.items():
                if hasattr(cls.motion_sensors[sensor_id], key):
                    setattr(cls.motion_sensors[sensor_id], key, value)
            return True
        return False

    @classmethod
    def update_windoor_sensor(cls, sensor_id: int, **kwargs) -> bool:
        """Update windoor sensor configuration."""
        if sensor_id in cls.windoor_sensors:
            for key, value in kwargs.items():
                if hasattr(cls.windoor_sensors[sensor_id], key):
                    setattr(cls.windoor_sensors[sensor_id], key, value)
            return True
        return False
