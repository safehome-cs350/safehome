"""API for security use cases."""

from fastapi import APIRouter, HTTPException

from ..common.device import SafetyZone
from ..common.user import UserDB
from .request import ReconfirmRequest, SafetyZoneRequest

router = APIRouter()


@router.post(
    "/reconfirm/",
    summary="Reconfirm user with address and phone number.",
    responses={
        401: {
            "description": "Invalid user ID or information mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        }
    },
)
def reconfirm(request: ReconfirmRequest):
    """Reconfirm user with address and phone number."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    if not (
        request.address == user.address or request.phone_number == user.phone_number
    ):
        raise HTTPException(status_code=401, detail="Information mismatch")

    return {"message": "Reconfirmed successfully"}


@router.post(
    "/create-safety-zone/",
    summary="UC2.f. Create new safety zone.",
    responses={
        400: {
            "description": "Validation error - occurs when:\n"
            "  - Safety zone name is empty\n"
            "  - No devices selected\n"
            "  - Safety zone with same name exists\n"
            "  - Device not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
    },
)
def create_safety_zone(request: SafetyZoneRequest):
    """UC2.f. Create new safety zone."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Check if name is provided
    if not request.name.strip():
        raise HTTPException(
            status_code=400, detail="Select new safety zone and type safety zone name"
        )

    # Check if devices are selected
    if not request.device_ids:
        raise HTTPException(
            status_code=400, detail="Select new safety zone and type safety zone name"
        )

    # Check if safety zone with same name exists
    if any(zone.name == request.name for zone in user.safety_zones):
        raise HTTPException(status_code=400, detail="Same safety zone exists")

    # Find devices by ids
    devices = []
    for device_id in request.device_ids:
        device = user.find_device_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=400, detail=f"Device with id {device_id} not found"
            )
        devices.append(device)

    # Create new safety zone
    new_zone = SafetyZone(name=request.name, devices=devices)

    # Add to user's safety zones
    user.safety_zones.append(new_zone)

    return {"message": "Safety zone created successfully"}


@router.post(
    "/delete-safety-zone/",
    summary="UC2.g. Delete safety zone.",
    responses={
        400: {
            "description": "Validation error - occurs when safety zone not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
    },
)
def delete_safety_zone(request: SafetyZoneRequest):
    """UC2.g. Delete safety zone."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Find the safety zone by name
    zone_to_delete = None
    for zone in user.safety_zones:
        if zone.name == request.name:
            zone_to_delete = zone
            break

    if not zone_to_delete:
        raise HTTPException(status_code=400, detail="Safety zone not found")

    # Remove the safety zone
    user.safety_zones.remove(zone_to_delete)

    return {"message": "Safety zone deleted successfully"}


@router.post(
    "/update-safety-zone/",
    summary="UC2.h. Update existing safety zone.",
    responses={
        400: {
            "description": "Validation error - occurs when:\n"
            "  - Safety zone not found\n"
            "  - No devices selected\n"
            "  - Device not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
    },
)
def update_safety_zone(request: SafetyZoneRequest):
    """UC2.h. Update existing safety zone."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Find the safety zone by name
    zone_to_update = None
    for zone in user.safety_zones:
        if zone.name == request.name:
            zone_to_update = zone
            break

    if not zone_to_update:
        raise HTTPException(status_code=400, detail="Safety zone not found")

    # Check if devices are selected
    if not request.device_ids:
        raise HTTPException(
            status_code=400, detail="Select safety zone and choose security devices"
        )

    # Find devices by ids
    devices = []
    for device_id in request.device_ids:
        device = user.find_device_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=400, detail=f"Device with id {device_id} not found"
            )
        devices.append(device)

    # Update the safety zone devices
    zone_to_update.devices = devices

    return {"message": "Safety zone updated successfully"}
