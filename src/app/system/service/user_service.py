import random

from fastapi import Request
from sqlalchemy import Select

from src.app.system.crud.crud_user import user_dao
from src.app.system.models import User
from src.app.system.schema.user import (
    AddUserParam,
    AvatarParam,
    ResetPasswordParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)
from src.common.exception import errors
from src.common.security.jwt import get_hash_password, get_token, password_verify, superuser_verify
from src.core.conf import settings
from src.database.db_postgres import async_db_session
from src.database.db_redis import redis_client


class UserService:
    @staticmethod  # TODO: allow admin to add users too
    async def add(*, request: Request, obj: AddUserParam) -> None:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            username = await user_dao.get_by_username(db, obj.username)
            if username:
                raise errors.ForbiddenError(msg='User already registered')
            if not obj.password:
                raise errors.ForbiddenError(msg='Password is empty')
            email = await user_dao.check_email(db, obj.email)
            if email:
                raise errors.ForbiddenError(msg='Email already registered')
            await user_dao.add(db, obj)

    @staticmethod
    async def pwd_reset(*, request: Request, obj: ResetPasswordParam) -> int:
        async with async_db_session.begin() as db:
            user = await user_dao.get(db, request.user.id)
            if user is None:
                raise errors.NotFoundError(msg='User does not exist')
            if not password_verify(f'{obj.old_password}', user.password):
                raise errors.ForbiddenError(msg='Incorrect old password')
            np1 = obj.new_password
            np2 = obj.confirm_password
            if np1 != np2:
                raise errors.ForbiddenError(msg='Passwords do not match')
            new_pwd = get_hash_password(f'{obj.new_password}', user.salt)
            count = await user_dao.reset_password(db, request.user.id, new_pwd)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}',
                f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count

    @staticmethod
    async def get_userinfo(*, username: str) -> User:
        async with async_db_session.begin() as db:
            user = await user_dao.get_with_relation(db, username=username)
            if not user:
                raise errors.NotFoundError(msg='User does not exist')
            return user

    @staticmethod
    async def update(*, request: Request, username: str, obj: UpdateUserParam) -> int:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.username != username:
                    raise errors.ForbiddenError(msg='You can only modify your own information')
            input_user = await user_dao.get_with_relation(db, username=username)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            if input_user.username != obj.username:
                _username = await user_dao.get_by_username(db, obj.username)
                if _username:
                    raise errors.ForbiddenError(msg='Username already registered')
            if input_user.email != obj.email:
                email = await user_dao.check_email(db, obj.email)
                if email:
                    raise errors.ForbiddenError(msg='Email already registered')
            count = await user_dao.update_userinfo(db, input_user.id, obj)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def update_roles(*, request: Request, username: str, obj: UpdateUserRoleParam) -> None:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.username != username:
                    raise errors.AuthorizationError
            input_user = await user_dao.get_with_relation(db, username=username)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            await user_dao.update_role(db, input_user, obj)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')

    @staticmethod
    async def update_avatar(*, request: Request, username: str, avatar: AvatarParam) -> int:
        async with async_db_session.begin() as db:
            if not request.user.is_superuser:
                if request.user.username != username:
                    raise errors.AuthorizationError
            input_user = await user_dao.get_by_username(db, username)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            count = await user_dao.update_avatar(db, input_user.id, avatar)
            await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
            return count

    @staticmethod
    async def get_select(
        *,
        username: str | None = None,
        status: int | None = None,
    ) -> Select:
        return await user_dao.get_list(username=username, status=status)

    @staticmethod
    async def update_permission(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg='Invalid operation')
                super_status = await user_dao.get_super(db, pk)
                count = await user_dao.set_super(db, pk, False if super_status else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{pk}')
                return count

    @staticmethod
    async def update_status(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            else:
                if pk == request.user.id:
                    raise errors.ForbiddenError(msg='Invalid operation')
                status = await user_dao.get_status(db, pk)
                count = await user_dao.set_status(db, pk, False if status else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{pk}')
                return count

    @staticmethod
    async def update_multi_login(*, request: Request, pk: int) -> int:
        async with async_db_session.begin() as db:
            superuser_verify(request)
            if not await user_dao.get(db, pk):
                raise errors.NotFoundError(msg='User does not exist')
            else:
                user_id = request.user.id
                multi_login = await user_dao.get_multi_login(db, pk) if pk != user_id else request.user.is_multi_login
                count = await user_dao.set_multi_login(db, pk, False if multi_login else True)
                await redis_client.delete(f'{settings.JWT_USER_REDIS_PREFIX}:{request.user.id}')
                token = get_token(request)
                latest_multi_login = await user_dao.get_multi_login(db, pk)
                # When superuser modifies themselves, all tokens except current one become invalid
                if pk == user_id:
                    if not latest_multi_login:
                        key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{pk}'
                        await redis_client.delete_prefix(key_prefix, exclude=f'{key_prefix}:{token}')
                        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
                        if refresh_token:
                            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{pk}'
                            await redis_client.delete_prefix(key_prefix, exclude=f'{key_prefix}:{refresh_token}')
                # When superuser modifies others, all their tokens become invalid
                else:
                    if not latest_multi_login:
                        key_prefix = [f'{settings.TOKEN_REDIS_PREFIX}:{pk}']
                        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
                        if refresh_token:
                            key_prefix.append(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{pk}')
                        for key in key_prefix:
                            await redis_client.delete_prefix(key)
                return count

    @staticmethod
    async def delete(*, username: str) -> int:
        async with async_db_session.begin() as db:
            input_user = await user_dao.get_by_username(db, username)
            if not input_user:
                raise errors.NotFoundError(msg='User does not exist')
            count = await user_dao.delete(db, input_user.id)
            key_prefix = [
                f'{settings.TOKEN_REDIS_PREFIX}:{input_user.id}',
                f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{input_user.id}',
            ]
            for key in key_prefix:
                await redis_client.delete_prefix(key)
            return count


user_service: UserService = UserService()
