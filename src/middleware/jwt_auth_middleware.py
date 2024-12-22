from typing import Any, Mapping

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
)
from starlette.requests import HTTPConnection

from src.app.system.schema.user import CurrentUserIns
from src.common.exception.errors import TokenError
from src.common.log import log
from src.common.security.jwt import jwt_authentication
from src.core.conf import settings


class _AuthenticationError(AuthenticationError):
    """Override internal authentication error class"""

    def __init__(
        self,
        *,
        code: int | None = None,
        msg: str | None = None,
        headers: Mapping[str, Any] | None = None,
    ):
        self.code = code
        self.msg = msg
        self.headers = headers


class JwtAuthMiddleware(AuthenticationBackend):
    """JWT Authentication Middleware"""

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: Exception) -> JSONResponse:
        """Override internal authentication error handling"""
        return JSONResponse(
            status_code=401, content={"code": 401, "message": str(exc), "data": None}
        )

    async def authenticate(
        self, request: Request
    ) -> tuple[AuthCredentials, CurrentUserIns] | None:
        token = request.headers.get("Authorization")
        if not token:
            return

        if request.url.path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
            return

        scheme, token = get_authorization_scheme_param(token)
        if scheme.lower() != "bearer":
            return

        try:
            user = await jwt_authentication(token)
        except TokenError as exc:
            raise _AuthenticationError(
                code=exc.code, msg=exc.detail, headers=exc.headers
            )
        except Exception as e:
            log.error(f"JWT Authorization Error: {e}")
            raise _AuthenticationError(
                code=getattr(e, "code", 500),
                msg=getattr(e, "msg", "Internal Server Error"),
            )

        # Note: This return uses a non-standard pattern, so some standard features will be lost when authentication passes
        # For standard return pattern, please check: https://www.starlette.io/authentication/
        return AuthCredentials(["authenticated"]), user
