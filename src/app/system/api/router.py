from fastapi import APIRouter

from src.app.system.api.v1.auth import router as auth_router
from src.app.system.api.v1.hunt import router as hunt_router
from src.app.system.api.v1.sys import router as sys_router

v1 = APIRouter()

v1.include_router(auth_router)
v1.include_router(sys_router)
v1.include_router(hunt_router)
