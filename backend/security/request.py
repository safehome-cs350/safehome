"""Request."""

from pydantic import BaseModel


class ReconfirmRequest(BaseModel):
    """Reconfirm request."""

    user_id: str
    address: str | None
    phone_number: str | None


class SafetyZoneRequest(BaseModel):
    """Safety zone request."""

    user_id: str
    name: str
    device_ids: list[int]
