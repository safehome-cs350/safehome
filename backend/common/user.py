"""User."""

from dataclasses import dataclass, field
from datetime import datetime

from .device import (
    AlarmEvent,
    CameraDB,
    Device,
    DeviceType,
    SafeHomeMode,
    SafeHomeModeType,
    SafetyZone,
    SensorDB,
)


@dataclass
class User:
    """User class."""

    # Common
    user_id: str
    password1: str
    password2: str
    master_password: str
    guest_password: str
    delay_time: int
    phone_number: str
    is_powered_on: bool
    address: str

    # Security
    devices: list[Device]
    safety_zones: list[SafetyZone]

    # SafeHome modes configuration
    safehome_modes: dict[SafeHomeModeType, SafeHomeMode] = field(default_factory=dict)
    current_mode: SafeHomeModeType = SafeHomeModeType.HOME

    # Alarm events log
    alarm_events: list[AlarmEvent] = field(default_factory=list)

    # System status
    is_system_armed: bool = False
    doors_windows_closed: bool = True
    login_attempts: int = 0
    last_failed_login: datetime | None = None

    def find_device_by_id(self, device_id: int) -> Device | None:
        """Find a device by ID."""
        return next((d for d in self.devices if d.id == device_id), None)

    def add_alarm_event(
        self, alarm_type, device_id: int | None, location: str, description: str
    ) -> int:
        """Add an alarm event and return its ID."""
        event_id = len(self.alarm_events) + 1
        event = AlarmEvent(
            id=event_id,
            timestamp=datetime.now(),
            alarm_type=alarm_type,
            device_id=device_id,
            location=location,
            description=description,
        )
        self.alarm_events.append(event)
        return event_id


class UserDB:
    """User database class."""

    users = [
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
                # All motion sensors from SensorDB (device IDs: 1-2)
                Device(
                    type=DeviceType.SENSOR,
                    id=1,
                    sensor_info=SensorDB.get_motion_sensor(1),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=2,
                    sensor_info=SensorDB.get_motion_sensor(2),
                ),
                # All windoor sensors from SensorDB (device IDs: 3-10)
                Device(
                    type=DeviceType.SENSOR,
                    id=3,
                    sensor_info=SensorDB.get_windoor_sensor(1),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=4,
                    sensor_info=SensorDB.get_windoor_sensor(2),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=5,
                    sensor_info=SensorDB.get_windoor_sensor(3),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=6,
                    sensor_info=SensorDB.get_windoor_sensor(4),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=7,
                    sensor_info=SensorDB.get_windoor_sensor(5),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=8,
                    sensor_info=SensorDB.get_windoor_sensor(6),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=9,
                    sensor_info=SensorDB.get_windoor_sensor(7),
                ),
                Device(
                    type=DeviceType.SENSOR,
                    id=10,
                    sensor_info=SensorDB.get_windoor_sensor(8),
                ),
                # All cameras from CameraDB (device IDs: 11-13)
                Device(
                    type=DeviceType.CAMERA,
                    id=11,
                    camera_info=CameraDB.get_camera(1),
                ),
                Device(
                    type=DeviceType.CAMERA,
                    id=12,
                    camera_info=CameraDB.get_camera(2),
                ),
                Device(
                    type=DeviceType.CAMERA,
                    id=13,
                    camera_info=CameraDB.get_camera(3),
                ),
            ],
            safety_zones=[],
            safehome_modes={
                SafeHomeModeType.HOME: SafeHomeMode(SafeHomeModeType.HOME, []),
                # AWAY mode: all sensors and cameras (device IDs: 1-13)
                SafeHomeModeType.AWAY: SafeHomeMode(
                    SafeHomeModeType.AWAY, list(range(1, 14))
                ),
                # OVERNIGHT_TRAVEL mode: all sensors and cameras
                SafeHomeModeType.OVERNIGHT_TRAVEL: SafeHomeMode(
                    SafeHomeModeType.OVERNIGHT_TRAVEL, list(range(1, 14))
                ),
                # EXTENDED_TRAVEL mode: all sensors and cameras
                SafeHomeModeType.EXTENDED_TRAVEL: SafeHomeMode(
                    SafeHomeModeType.EXTENDED_TRAVEL, list(range(1, 14))
                ),
                # GUEST_HOME mode: motion sensors only (device IDs: 1-2)
                SafeHomeModeType.GUEST_HOME: SafeHomeMode(
                    SafeHomeModeType.GUEST_HOME, [1, 2]
                ),
            },
        )
    ]

    @classmethod
    def find_user_by_id(cls, user_id: str) -> User | None:
        """Find a user by ID."""
        return next((u for u in cls.users if u.user_id == user_id), None)
