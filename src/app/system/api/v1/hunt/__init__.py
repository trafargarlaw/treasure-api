from fastapi import APIRouter

from src.app.system.api.v1.hunt.hunt import router as hunt_router

router = APIRouter(prefix='/hunt')

router.include_router(hunt_router, tags=['Hunt'])
