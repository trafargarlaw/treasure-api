from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from src.core.path_conf import BasePath


class Settings(BaseSettings):
    """Global Settings"""

    model_config = SettingsConfigDict(
        env_file=f'{BasePath}/.env',
        env_file_encoding='utf-8',
        extra='ignore',
        validate_default=False,
    )

    # Env Config
    ENVIRONMENT: Literal['dev', 'pro']

    # Env Postgres
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str

    # FastAPI
    FASTAPI_API_V1_PATH: str = '/api/v1'
    FASTAPI_TITLE: str = 'FastAPI'
    FASTAPI_VERSION: str = '0.0.1'
    FASTAPI_DESCRIPTION: str = 'FastAPI Best Architecture'
    FASTAPI_DOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/docs'
    FASTAPI_REDOCS_URL: str | None = f'{FASTAPI_API_V1_PATH}/redocs'
    FASTAPI_OPENAPI_URL: str | None = f'{FASTAPI_API_V1_PATH}/openapi'
    FASTAPI_STATIC_FILES: bool = True

    # Uvicorn
    UVICORN_RELOAD: bool = True

    # Env Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_DATABASE: int

    REDIS_TIMEOUT: int = 5

    DATETIME_TIMEZONE: str = 'Africa/Casablanca'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'

    DEMO_MODE: bool = False
    DEMO_MODE_EXCLUDE: list[tuple[str, str]] = []

    REQUEST_LIMITER_REDIS_PREFIX: str = 'request_limiter'

    # Middleware
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_ACCESS: bool = True

    # Trace ID
    TRACE_ID_REQUEST_HEADER_KEY: str = 'X-Request-ID'

    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://127.0.0.1:8000',
        'http://localhost:5173',
    ]
    CORS_EXPOSE_HEADERS: list[str] = [
        TRACE_ID_REQUEST_HEADER_KEY,
    ]

    # Token
    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str = 'HS256'  # algorithm
    TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 1  # 1 day
    TOKEN_REFRESH_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # refresh token expiration time in seconds
    TOKEN_REDIS_PREFIX: str = 'fba:token'
    TOKEN_REFRESH_REDIS_PREFIX: str = 'fba:refresh_token'
    TOKEN_REQUEST_PATH_EXCLUDE: list[str] = [  # JWT / RBAC whitelist
        f'{FASTAPI_API_V1_PATH}/auth/login',
    ]

    # JWT
    JWT_USER_REDIS_PREFIX: str = 'fba:user'
    JWT_USER_REDIS_EXPIRE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days

    # Cookies
    COOKIE_REFRESH_TOKEN_KEY: str = 'fba_refresh_token'
    COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS: int = TOKEN_REFRESH_EXPIRE_SECONDS

    # Log
    LOG_ROOT_LEVEL: str = 'NOTSET'
    LOG_STD_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_FILE_FORMAT: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> | <lvl>{level: <8}</> | '
        '<cyan> {correlation_id} </> | <lvl>{message}</>'
    )
    LOG_CID_DEFAULT_VALUE: str = '-'
    LOG_CID_UUID_LENGTH: int = 32  # must <= 32
    LOG_STDOUT_LEVEL: str = 'INFO'
    LOG_STDERR_LEVEL: str = 'ERROR'
    LOG_STDOUT_FILENAME: str = 'fba_access.log'
    LOG_STDERR_FILENAME: str = 'fba_error.log'

    # Super Admin
    SUPER_ADMIN_EMAIL: str
    SUPER_ADMIN_USERNAME: str
    SUPER_ADMIN_PASSWORD: str


@lru_cache
def get_settings() -> Settings:
    """Get global settings"""
    return Settings.model_validate({})


# Create configuration instance
settings = get_settings()
