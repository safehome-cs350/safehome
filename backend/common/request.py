"""Request."""

from pydantic import BaseModel


class ControlPanelLoginRequest(BaseModel):
    """Control panel login request."""

    user_id: str
    password: str


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


class GetConfigRequest(BaseModel):
    """Get config request."""

    user_id: str


class PowerRequest(BaseModel):
    """Power request."""

    user_id: str
