"""API for common use cases."""

from fastapi import APIRouter, HTTPException

from .request import ConfigRequest, LoginRequest, PowerRequest
from .user import UserDB

router = APIRouter()


@router.post(
    "/login/",
    summary="UC1.b. Log onto the system through web browser.",
    responses={
        401: {
            "description": "Invalid user ID or password",
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
def login(request: LoginRequest):
    """UC1.b. Log onto the system through web browser."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="ID not recognized")

    if request.password1 != user.password1 or request.password2 != user.password2:
        raise HTTPException(status_code=401, detail="Password incorrect")

    return "Welcome!"


@router.post(
    "/config/",
    summary="UC1.c. Configure system setting.",
    responses={
        400: {
            "description": "Delay time must be at least 300",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "string",
                    },
                }
            },
        },
        401: {
            "description": "Invalid user ID",
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
def config(request: ConfigRequest):
    """UC1.c. Configure system setting."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    if request.password1 is not None:
        user.password1 = request.password1
    if request.password2 is not None:
        user.password2 = request.password2
    if request.master_password is not None:
        user.master_password = request.master_password
    if request.guest_password is not None:
        user.guest_password = request.guest_password
    if request.delay_time is not None:
        if request.delay_time < 300:
            raise HTTPException(
                status_code=400, detail="Delay time must be at least 300"
            )
        user.delay_time = request.delay_time
    if request.phone_number is not None:
        user.phone_number = request.phone_number

    return {"message": "Configuration updated successfully"}


@router.post(
    "/power_on/",
    summary="UC1.d. Turn the system on.",
    responses={
        401: {
            "description": "Invalid user ID",
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
def power_on(request: PowerRequest):
    """UC1.d. Turn the system on."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    user.is_powered_on = True
    return {"message": "System powered on"}


@router.post(
    "/power_off/",
    summary="UC1.e. Turn the system off.",
    responses={
        401: {
            "description": "Invalid user ID",
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
def power_off(request: PowerRequest):
    """UC1.e. Turn the system off."""
    user = UserDB.find_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    user.is_powered_on = False
    return {"message": "System powered off"}
