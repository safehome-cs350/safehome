"""API for SafeHome System."""

from fastapi import FastAPI

from .common import router as common_router
from .security import router as security_router

app = FastAPI(title="SafeHome API", version="1.0")

app.include_router(common_router)
app.include_router(security_router)
