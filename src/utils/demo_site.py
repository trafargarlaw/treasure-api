from fastapi import Request

from src.common.exception import errors
from src.core.conf import settings


async def demo_site(request: Request):
    """Demo site"""

    method = request.method
    path = request.url.path
    if (
        settings.DEMO_MODE
        and method != "GET"
        and method != "OPTIONS"
        and (method, path) not in settings.DEMO_MODE_EXCLUDE
    ):
        raise errors.ForbiddenError(msg="Operation not allowed in demo environment")
