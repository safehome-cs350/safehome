"""API for security use cases."""

from fastapi import APIRouter, HTTPException

from ..common.device import AlarmType, SafetyZone
from ..common.user import UserDB
from .request import (
    AlarmEventRequest,
    PanicRequest,
    ReconfirmRequest,
    SafeHomeModeRequest,
    SafetyZoneRequest,
    SetModeRequest,
    ViewLogRequest,
)

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

    # Verify that at least one field is provided
    if not request.address and not request.phone_number:
        raise HTTPException(
            status_code=401, detail="Please provide address or phone number"
        )

    # Verify that at least one field matches (address OR phone number)
    address_match = (
        request.address is not None
        and request.address.strip() != ""
        and request.address == user.address
    )
    phone_match = (
        request.phone_number is not None
        and request.phone_number.strip() != ""
        and request.phone_number == user.phone_number
    )

    if not (address_match or phone_match):
        raise HTTPException(status_code=401, detail="Information mismatch")

    return {"message": "Reconfirmed successfully"}


@router.get(
    "/get-safety-zones/",
    summary="Get safety zones for a user.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def get_safety_zones(user_id: str):
    """Get safety zones for a user."""
    user = UserDB.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Convert SafetyZone dataclass objects to serializable format
    safety_zones_data = []
    for zone in user.safety_zones:
        safety_zones_data.append(
            {
                "name": zone.name,
                "devices": [
                    {"id": device.id, "type": device.type.value}
                    for device in zone.devices
                ],
                "is_armed": zone.is_armed,
            }
        )

    return {"safety_zones": safety_zones_data}


@router.post(
    "/arm/",
    summary="UC2.a/b. Arm system.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def arm(user_id: str):
    """UC2.a/b. Arm system."""
    user = UserDB.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    for device in user.devices:
        device.is_armed = True

    return {"message": "All devices armed successfully"}


@router.post(
    "/disarm/",
    summary="UC2.a/b. Disarm system.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def disarm(user_id: str):
    """UC2.a/b. Disarm system."""
    user = UserDB.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    for device in user.devices:
        device.is_armed = False

    return {"message": "All devices disarmed successfully"}


@router.post(
    "/arm-safety-zone/",
    summary="UC2.c. Arm safety zone selectively.",
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
def arm_safety_zone(request: SafetyZoneRequest):
    """UC2.c. Arm safety zone selectively."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Find the safety zone by name
    zone_to_arm = None
    for zone in user.safety_zones:
        if zone.name == request.name:
            zone_to_arm = zone
            break

    if not zone_to_arm:
        raise HTTPException(status_code=400, detail="Safety zone not found")

    # Arm the safety zone
    zone_to_arm.is_armed = True

    # Log the zone arming event
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=None,
        location=request.name,
        description=f"Safety zone '{request.name}' armed",
    )

    return {"message": "Safety zone armed successfully"}


@router.post(
    "/disarm-safety-zone/",
    summary="UC2.c. Disarm safety zone selectively.",
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
def disarm_safety_zone(request: SafetyZoneRequest):
    """UC2.c. Disarm safety zone selectively."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Find the safety zone by name
    zone_to_disarm = None
    for zone in user.safety_zones:
        if zone.name == request.name:
            zone_to_disarm = zone
            break

    if not zone_to_disarm:
        raise HTTPException(status_code=400, detail="Safety zone not found")

    # Disarm the safety zone
    zone_to_disarm.is_armed = False

    # Log the zone disarming event
    user.add_alarm_event(
        alarm_type=AlarmType.INTRUSION,
        device_id=None,
        location=request.name,
        description=f"Safety zone '{request.name}' disarmed",
    )

    return {"message": "Safety zone disarmed successfully"}


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
    new_zone = SafetyZone(name=request.name, devices=devices, is_armed=False)

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


@router.post(
    "/configure-safehome-modes/",
    summary="UC2.i. Configure SafeHome modes.",
    responses={
        400: {
            "description": "Validation error - occurs when:\n"
            "  - Invalid mode type\n"
            "  - Device not found",
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
def configure_safehome_modes(request: SafeHomeModeRequest):
    """UC2.i. Configure SafeHome modes."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Validate devices exist
    for device_id in request.enabled_device_ids:
        device = user.find_device_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=400, detail=f"Device with id {device_id} not found"
            )

    # Update the mode configuration
    from ..common.device import SafeHomeMode

    user.safehome_modes[request.mode_type] = SafeHomeMode(
        mode_type=request.mode_type, enabled_device_ids=request.enabled_device_ids
    )

    return {
        "message": f"SafeHome mode {request.mode_type.value} configured successfully"
    }


@router.get(
    "/get-safehome-modes/",
    summary="Get SafeHome modes configuration.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def get_safehome_modes(user_id: str):
    """Get SafeHome modes configuration."""
    user = UserDB.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    modes_config = {}
    for mode_type, mode_config in user.safehome_modes.items():
        modes_config[mode_type.value] = {
            "mode_type": mode_config.mode_type.value,
            "enabled_device_ids": mode_config.enabled_device_ids,
        }

    return {
        "current_mode": user.current_mode.value,
        "modes_configuration": modes_config,
    }


@router.post(
    "/set-safehome-mode/",
    summary="Set current SafeHome mode.",
    responses={
        400: {
            "description": "Validation error - occurs when:\n"
            "  - Doors or windows not closed when arming\n"
            "  - Invalid mode type",
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
def set_safehome_mode(request: SetModeRequest):
    """Set current SafeHome mode."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Check if mode configuration exists
    if request.mode_type not in user.safehome_modes:
        raise HTTPException(status_code=400, detail="Mode not configured")

    mode_config = user.safehome_modes[request.mode_type]

    # Check doors/windows status for arming modes
    if len(mode_config.enabled_device_ids) > 0 and not user.doors_windows_closed:
        raise HTTPException(status_code=400, detail="doors and windows not closed")

    # Apply mode configuration
    user.current_mode = request.mode_type

    # Arm/disarm devices according to mode configuration
    for device in user.devices:
        device.is_armed = device.id in mode_config.enabled_device_ids

    user.is_system_armed = len(mode_config.enabled_device_ids) > 0

    return {
        "message": f"SafeHome mode set to {request.mode_type.value}",
        "current_mode": user.current_mode.value,
        "armed_devices": mode_config.enabled_device_ids,
    }


@router.post(
    "/alarm-condition/",
    summary="UC2.d. Alarm condition encountered.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def alarm_condition_encountered(request: AlarmEventRequest):
    """UC2.d. Alarm condition encountered."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # device_id가 실제로 존재하는지 확인
    device = next((d for d in user.devices if d.id == request.device_id), None)
    if not device:
        raise HTTPException(status_code=400, detail="Device not found")

    # Record alarm event
    event_id = user.add_alarm_event(
        alarm_type=request.alarm_type,
        device_id=request.device_id,
        location=request.location,
        description=request.description,
    )

    # Simulate alarm actions based on use case
    response_data = {
        "event_id": event_id,
        "message": "Alarm condition encountered",
        "actions_taken": [
            "Audible alarm activated",
            "Event recorded in database",
            "Control panel displays alarm condition",
        ],
    }

    # Add monitoring service call simulation after delay
    if user.delay_time > 0:
        response_data["actions_taken"].append(
            f"Monitoring service will be called after {user.delay_time} seconds delay"
        )

    return response_data


@router.post(
    "/view-intrusion-log/",
    summary="UC2.j. View intrusion log.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def view_intrusion_log(request: ViewLogRequest):
    """UC2.j. View intrusion log."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Filter events based on request parameters
    filtered_events = user.alarm_events

    if request.start_date:
        filtered_events = [
            e for e in filtered_events if e.timestamp >= request.start_date
        ]

    if request.end_date:
        filtered_events = [
            e for e in filtered_events if e.timestamp <= request.end_date
        ]

    if request.alarm_type:
        filtered_events = [
            e for e in filtered_events if e.alarm_type == request.alarm_type
        ]

    # Convert to serializable format
    events_data = []
    for event in filtered_events:
        events_data.append(
            {
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "alarm_type": event.alarm_type.value,
                "device_id": event.device_id,
                "location": event.location,
                "description": event.description,
                "is_resolved": event.is_resolved,
            }
        )

    return {"total_events": len(events_data), "events": events_data}


@router.post(
    "/panic-call/",
    summary="UC2.k. Call monitoring service through control panel (panic function).",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def panic_call_monitoring_service(request: PanicRequest):
    """UC2.k. Call monitoring service through control panel (panic function)."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Record panic event
    event_id = user.add_alarm_event(
        alarm_type=AlarmType.PANIC,
        device_id=None,
        location=request.location,
        description="Panic button pressed by homeowner",
    )

    return {
        "event_id": event_id,
        "message": "Panic call initiated - monitoring service contacted immediately",
        "actions_taken": [
            "Panic alarm activated",
            "Monitoring service called immediately (no delay)",
            "Event logged in system",
            "Emergency response dispatched",
        ],
        "monitoring_service_status": "contacted",
    }


@router.get(
    "/configure-safety-zone/",
    summary="UC2.e. Configure safety zone - main interface.",
    responses={
        401: {
            "description": "Invalid user ID - occurs when the user ID does not exist",
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
def configure_safety_zone_interface(user_id: str):
    """UC2.e. Configure safety zone - main interface."""
    user = UserDB.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    # Return floor plan with existing safety zones and available devices
    safety_zones_data = []
    for zone in user.safety_zones:
        safety_zones_data.append(
            {
                "name": zone.name,
                "device_ids": [d.id for d in zone.devices],
                "is_armed": zone.is_armed,
            }
        )

    available_devices = []
    for device in user.devices:
        available_devices.append({"id": device.id, "type": device.type.value})

    return {
        "message": "Safety zone configuration interface",
        "available_functions": [
            "create_new_safety_zone",
            "delete_safety_zone",
            "update_safety_zone",
        ],
        "existing_safety_zones": safety_zones_data,
        "available_devices": available_devices,
        "floor_plan_info": (
            "Floor plan with safety zones and device locations displayed"
        ),
    }
