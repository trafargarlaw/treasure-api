from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from user_agents import parse


class StateMiddleware(BaseHTTPMiddleware):
    """Request state middleware"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get IP info
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else "unknown")
        )

        # Get User-Agent info
        ua_string = request.headers.get("User-Agent", "")
        user_agent = parse(ua_string)

        # Set additional request information
        request.state.ip = ip
        request.state.country = None  # Can be extended with geo-IP lookup
        request.state.region = None
        request.state.city = None
        request.state.user_agent = ua_string
        request.state.os = str(user_agent.os)
        request.state.browser = (
            f"{user_agent.browser.family} {user_agent.browser.version_string}"
        )
        request.state.device = str(user_agent.device)

        response = await call_next(request)
        return response
