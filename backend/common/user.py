"""User."""

from dataclasses import dataclass

from .device import Device, DeviceType, SafetyZone


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

    def find_device_by_id(self, device_id: int) -> Device | None:
        """Find a device by ID."""
        return next((d for d in self.devices if d.id == device_id), None)


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
                Device(type=DeviceType.SENSOR, id=1),
                Device(type=DeviceType.SENSOR, id=2),
                Device(type=DeviceType.CAMERA, id=3),
            ],
            safety_zones=[],
        )
    ]

    @classmethod
    def find_user_by_id(cls, user_id: str) -> User | None:
        """Find a user by ID."""
        return next((u for u in cls.users if u.user_id == user_id), None)

    
