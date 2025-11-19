"""API for SafeHome System."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SafeHome API", version="1.0")


class LoginRequest(BaseModel):
    """Login Request Model."""

    user_id: str
    password1: str
    password2: str


users_db = {"homeowner1": {"password1": "12345678", "password2": "abcdefgh"}}


@app.post(
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
def login(login_request: LoginRequest):
    """UC1.b. Log onto the system through web browser."""
    user = users_db.get(login_request.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="ID not recognized")

    if (
        login_request.password1 != user["password1"]
        or login_request.password2 != user["password2"]
    ):
        raise HTTPException(status_code=401, detail="Password incorrect")

    return "Welcome!"
