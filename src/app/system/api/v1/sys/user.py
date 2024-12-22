from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.system.schema.user import (
    AddUserParam,
    AvatarParam,
    GetCurrentUserInfoDetail,
    GetUserInfoListDetails,
    ResetPasswordParam,
    UpdateUserParam,
    UpdateUserRoleParam,
)
from src.app.system.service.user_service import user_service
from src.common.pagination import DependsPagination, paging_data
from src.common.response.response_schema import ResponseModel, response_base
from src.common.security.jwt import DependsJwtAuth
from src.database.db_postgres import get_session

router = APIRouter()


@router.post('/add', summary='Add User', dependencies=[DependsJwtAuth])
async def add_user(request: Request, obj: AddUserParam) -> ResponseModel[GetUserInfoListDetails]:
    await user_service.add(request=request, obj=obj)
    current_user = await user_service.get_userinfo(username=obj.username)
    data = GetUserInfoListDetails(**current_user.model_dump())
    return response_base.success(data=data)


@router.post('/password/reset', summary='Reset Password', dependencies=[DependsJwtAuth])
async def password_reset(request: Request, obj: ResetPasswordParam) -> ResponseModel:
    count = await user_service.pwd_reset(request=request, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get(
    '/me',
    summary='Get Current User Info',
    dependencies=[DependsJwtAuth],
    response_model_exclude={'password'},
)
async def get_current_user(request: Request) -> ResponseModel[GetCurrentUserInfoDetail]:
    data = GetCurrentUserInfoDetail(**request.user.model_dump())
    return response_base.success(data=data)


@router.get('/{username}', summary='View User Info', dependencies=[DependsJwtAuth])
async def get_user(
    username: Annotated[str, Path(...)],
) -> ResponseModel[GetUserInfoListDetails]:
    current_user = await user_service.get_userinfo(username=username)
    data = GetUserInfoListDetails(**current_user.model_dump())
    return response_base.success(data=data)


@router.put('/{username}', summary='Update User Info', dependencies=[DependsJwtAuth])
async def update_user(request: Request, username: Annotated[str, Path(...)], obj: UpdateUserParam) -> ResponseModel:
    count = await user_service.update(request=request, username=username, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put(
    '/{username}/role',
    summary='Update User Role',
    dependencies=[
        DependsJwtAuth,
    ],
)
async def update_user_role(
    request: Request, username: Annotated[str, Path(...)], obj: UpdateUserRoleParam
) -> ResponseModel:
    await user_service.update_roles(request=request, username=username, obj=obj)
    return response_base.success()


@router.put('/{username}/avatar', summary='Update Avatar', dependencies=[DependsJwtAuth])
async def update_avatar(request: Request, username: Annotated[str, Path(...)], avatar: AvatarParam) -> ResponseModel:
    count = await user_service.update_avatar(request=request, username=username, avatar=avatar)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get(
    '',
    summary='Get All Users with Fuzzy Conditions and Pagination',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_pagination_users(
    db: AsyncSession = Depends(get_session),
    username: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
):
    user_select = await user_service.get_select(username=username, status=status)
    page_data = await paging_data(db, user_select, GetUserInfoListDetails)
    return response_base.success(data=page_data)


@router.put('/{pk}/super', summary='Modify User Super Permissions', dependencies=[DependsJwtAuth])
async def super_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_permission(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/status', summary='Modify User Status', dependencies=[DependsJwtAuth])
async def status_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_status(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{pk}/multi', summary='Modify User Multi-Login Status', dependencies=[DependsJwtAuth])
async def multi_set(request: Request, pk: Annotated[int, Path(...)]) -> ResponseModel:
    count = await user_service.update_multi_login(request=request, pk=pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    path='/{username}',
    summary='Delete User Account',
    description='Delete User Account != User Logout, after deletion the user will be removed from database',
    dependencies=[
        DependsJwtAuth,
    ],
)
async def delete_user(username: Annotated[str, Path(...)]) -> ResponseModel:
    count = await user_service.delete(username=username)
    if count > 0:
        return response_base.success()
    return response_base.fail()
