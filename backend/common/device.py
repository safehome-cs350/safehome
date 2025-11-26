"""Device."""

from dataclasses import dataclass
from enum import Enum


class DeviceType(Enum):
    """Device Type Enum."""

    CAMERA = "camera"
    SENSOR = "sensor"


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
