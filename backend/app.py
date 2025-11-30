"""API for SafeHome System."""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .common import router as common_router
from .security import router as security_router
from .surveillance.surveillance import router as surveillance_router

app = FastAPI(title="SafeHome API", version="1.0")

app.include_router(common_router)
app.include_router(surveillance_router)
app.include_router(security_router)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# /static → safehome/
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
