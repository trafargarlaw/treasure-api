from fastapi import APIRouter

from src.app.system.api.v1.auth.auth import router as auth_router

router = APIRouter(prefix="/auth")

router.include_router(auth_router, tags=["Authorization"])
