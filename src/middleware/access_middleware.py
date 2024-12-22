from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.common.log import log
from src.utils.timezone import timezone


class AccessMiddleware(BaseHTTPMiddleware):
    """Request logging middleware"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = timezone.now()
        response = await call_next(request)
        end_time = timezone.now()
        client_host = request.client.host if request.client else "unknown"
        log.info(
            f"{client_host: <15} | {request.method: <8} | {response.status_code: <6} | "
            f"{request.url.path} | {round((end_time - start_time).total_seconds(), 3) * 1000.0}ms"
        )
        return response
