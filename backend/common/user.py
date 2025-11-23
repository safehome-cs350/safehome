"""User."""

from dataclasses import dataclass


@dataclass
class User:
    """User class."""

    user_id: str
    password1: str
    password2: str
    master_password: str
    guest_password: str
    delay_time: int
    phone_number: str
    is_powered_on: bool


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
        )
    ]

    @classmethod
    def find_user_by_id(cls, user_id: str) -> User | None:
        """Find a user by ID."""
        return next((u for u in cls.users if u.user_id == user_id), None)
