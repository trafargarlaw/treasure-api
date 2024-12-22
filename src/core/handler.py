from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from starlette.middleware.authentication import AuthenticationMiddleware

from src.app.router import route
from src.common.exception.exception_handler import register_exception
from src.core.conf import settings
from src.database.db_postgres import create_db_and_tables
from src.database.db_redis import redis_client
from src.middleware.jwt_auth_middleware import JwtAuthMiddleware
from src.middleware.state_middleware import StateMiddleware
from src.utils import demo_site, simplify_operation_ids
from src.utils.health_check import ensure_unique_route_names, http_limit_callback


@asynccontextmanager
async def init_handler(app: FastAPI):
    await create_db_and_tables()

    # Connect to redis
    await redis_client.open()
    # Initialize limiter
    await FastAPILimiter.init(
        redis=redis_client,
        prefix=settings.REQUEST_LIMITER_REDIS_PREFIX,
        http_callback=http_limit_callback,
    )

    yield

    # Close redis connection
    await redis_client.close()
    # Close limiter
    await FastAPILimiter.close()


def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        redoc_url=settings.FASTAPI_REDOCS_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        lifespan=init_handler,
    )

    register_router(app)
    register_middleware(app)
    register_exception(app)
    return app


def register_router(app: FastAPI):
    """
    Router

    :param app: FastAPI
    :return:
    """
    dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # API
    app.include_router(route, dependencies=dependencies)

    # Extra
    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_middleware(app: FastAPI):
    """
    Middleware, execution order from bottom to top

    :param app:
    :return:
    """
    # Opera log (required)
    # JWT auth (required)
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JwtAuthMiddleware(),
        on_error=JwtAuthMiddleware.auth_exception_handler,
    )
    # Access log
    if settings.MIDDLEWARE_ACCESS:
        from src.middleware.access_middleware import AccessMiddleware

        app.add_middleware(AccessMiddleware)
    # State
    app.add_middleware(StateMiddleware)
    # Trace ID (required)
    app.add_middleware(CorrelationIdMiddleware, validator=False)
    # CORS: Always at the end
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )
