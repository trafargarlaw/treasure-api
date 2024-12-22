from fastapi import APIRouter

from src.app.system.api.v1.sys.user import router as user_router

router = APIRouter(prefix='/sys')

router.include_router(user_router, prefix='/users', tags=['System Users'])
