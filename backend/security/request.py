"""Request."""

from pydantic import BaseModel


class ReconfirmRequest(BaseModel):
    """Reconfirm request."""

    user_id: str
    address: str
    phone_number: str
