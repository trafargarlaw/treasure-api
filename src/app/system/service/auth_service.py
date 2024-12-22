from fastapi import Request, Response
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTask, BackgroundTasks

from src.app.system.crud.crud_user import user_dao
from src.app.system.models import User
from src.app.system.schema.token import GetLoginToken, GetNewToken
from src.app.system.schema.user import AuthLoginParam
from src.app.system.service.login_log_service import login_log_service
from src.common.enums import LoginLogStatusType
from src.common.exception import errors
from src.common.security.jwt import (
    create_access_token,
    create_refresh_token,
    get_token,
    jwt_decode,
    password_verify,
)
from src.core.conf import settings
from src.database.db_postgres import async_db_session
from src.database.db_redis import redis_client
from src.utils.timezone import timezone


class AuthService:
    @staticmethod
    async def swagger_login(*, obj: HTTPBasicCredentials) -> tuple[str, User]:
        async with async_db_session.begin() as db:
            current_user = await user_dao.get_by_username(db, obj.username)
            if not current_user:
                raise errors.NotFoundError(msg="Invalid username or password")
            elif not password_verify(f"{obj.password}", current_user.password):
                raise errors.AuthorizationError(msg="Invalid username or password")
            elif not current_user.status:
                raise errors.AuthorizationError(
                    msg="User is locked, please contact administrator"
                )
            access_token = await create_access_token(
                str(current_user.id), current_user.is_multi_login
            )
            await user_dao.update_login_time(db, obj.username)
            return access_token.access_token, current_user

    @staticmethod
    async def login(
        *,
        request: Request,
        response: Response,
        obj: AuthLoginParam,
        background_tasks: BackgroundTasks,
    ) -> GetLoginToken:
        async with async_db_session.begin() as db:
            try:
                current_user = await user_dao.get_by_username(db, obj.username)
                if not current_user:
                    raise errors.NotFoundError(msg="Invalid username or password")
                user_uuid = current_user.uuid
                username = current_user.username
                if not password_verify(obj.password, current_user.password):
                    raise errors.AuthorizationError(msg="Invalid username or password")
                elif not current_user.status:
                    raise errors.AuthorizationError(
                        msg="User is locked, please contact administrator"
                    )

                current_user_id = current_user.id
                access_token = await create_access_token(
                    str(current_user_id), current_user.is_multi_login
                )
                refresh_token = await create_refresh_token(
                    str(current_user_id), current_user.is_multi_login
                )
            except errors.NotFoundError as e:
                raise errors.NotFoundError(msg=e.msg or "Invalid username or password")
            except (errors.AuthorizationError, errors.CustomError) as e:
                task = BackgroundTask(
                    login_log_service.create,
                    db=db,
                    request=request,
                    user_uuid=user_uuid,
                    username=username,
                    login_time=timezone.now(),
                    status=LoginLogStatusType.fail.value,
                    msg=str(e.msg) if e.msg is not None else "Login failed",
                )
                raise errors.AuthorizationError(
                    msg=str(e.msg) if e.msg is not None else "Login failed",
                    background=task,
                )
            except Exception as e:
                raise e
            else:
                background_tasks.add_task(
                    login_log_service.create,
                    db=db,
                    request=request,
                    user_uuid=user_uuid,
                    username=username,
                    login_time=timezone.now(),
                    status=LoginLogStatusType.success.value,
                    msg="Login successful",
                )
                await user_dao.update_login_time(db, obj.username)
                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=timezone.f_utc(refresh_token.refresh_token_expire_time),
                    httponly=True,
                )
                await db.refresh(current_user)
                data = GetLoginToken(
                    access_token=access_token.access_token,
                    access_token_expire_time=access_token.access_token_expire_time,
                    user=current_user,  # type: ignore
                )
                return data

    @staticmethod
    async def new_token(*, request: Request, response: Response) -> GetNewToken | None:
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        if not refresh_token:
            raise errors.TokenError(msg="Refresh Token missing, please login again")
        try:
            user_id = jwt_decode(refresh_token)
        except Exception:
            raise errors.TokenError(msg="Invalid Refresh Token")
        if request.user.id != user_id:
            raise errors.TokenError(msg="Invalid Refresh Token")
        async with async_db_session.begin() as db:
            current_user = await user_dao.get(db, user_id)
            if not current_user:
                raise errors.NotFoundError(msg="Invalid username or password")
            elif not current_user.status:
                raise errors.AuthorizationError(
                    msg="User is locked, please contact administrator"
                )

    @staticmethod
    async def logout(*, request: Request, response: Response) -> None:
        token = get_token(request)
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)
        if request.user.is_multi_login:
            key = f"{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}"
            await redis_client.delete(key)
            if refresh_token:
                key = f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:{refresh_token}"
                await redis_client.delete(key)
        else:
            key_prefix = f"{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:"
            await redis_client.delete_prefix(key_prefix)
            key_prefix = f"{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:"
            await redis_client.delete_prefix(key_prefix)


auth_service: AuthService = AuthService()
