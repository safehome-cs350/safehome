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
class AlarmEvent:
    """Alarm Event Log Entry."""
    
    id: int
    timestamp: datetime
    alarm_type: AlarmType
    device_id: int | None
    location: str
    description: str
    is_resolved: bool = False
