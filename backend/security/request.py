"""Request."""

from datetime import datetime
from pydantic import BaseModel

from ..common.device import SafeHomeModeType, AlarmType


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


class SafeHomeModeRequest(BaseModel):
    """SafeHome mode configuration request."""
    
    user_id: str
    mode_type: SafeHomeModeType
    enabled_device_ids: list[int]


class SetModeRequest(BaseModel):
    """Set SafeHome mode request."""
    
    user_id: str
    mode_type: SafeHomeModeType


class AlarmEventRequest(BaseModel):
    """Alarm event request."""
    
    user_id: str
    alarm_type: AlarmType
    device_id: int | None
    location: str
    description: str


class ViewLogRequest(BaseModel):
    """View intrusion log request."""
    
    user_id: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    alarm_type: AlarmType | None = None


class PanicRequest(BaseModel):
    """Panic button request."""
    
    user_id: str
    location: str
