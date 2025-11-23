"""Request."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request."""

    user_id: str
    password1: str
    password2: str


class ConfigRequest(BaseModel):
    """Config request."""

    user_id: str
    password1: str | None
    password2: str | None
    master_password: str | None
    guest_password: str | None
    delay_time: int | None
    phone_number: str | None


class PowerRequest(BaseModel):
    """Power request."""

    user_id: str
