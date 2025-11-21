"""Request."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request."""

    user_id: str
    password1: str
    password2: str
