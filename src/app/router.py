from fastapi import APIRouter

from src.app.system.api.router import v1 as admin_v1
from src.core.conf import settings

route = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

route.include_router(admin_v1)
