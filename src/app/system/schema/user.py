from datetime import datetime

from pydantic import ConfigDict, EmailStr, Field, HttpUrl

from src.common.enums import AccountStatusType
from src.common.schema import SchemaBase


class AuthSchemaBase(SchemaBase):
    username: str
    password: str


class AuthLoginParam(AuthSchemaBase):
    pass


class AddUserParam(AuthSchemaBase):
    email: EmailStr = Field(examples=['user@example.com'])


# Add super admin
# NOTE: only for seeding command
class AddSuperAdminParam(AddUserParam):
    is_superuser: bool = True
    is_multi_login: bool = True
    status: int = 0


class UserInfoSchemaBase(SchemaBase):
    username: str
    email: EmailStr = Field(examples=['user@example.com'])


class UpdateUserParam(UserInfoSchemaBase):
    pass


class UpdateUserRoleParam(SchemaBase):
    pass


class AvatarParam(SchemaBase):
    url: HttpUrl = Field(description='头像 http 地址')


class GetUserInfoNoRelationDetail(UserInfoSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    avatar: str | None = None
    status: AccountStatusType = Field(default=AccountStatusType.enable)
    is_superuser: bool
    is_multi_login: bool
    join_time: datetime | None = None
    last_login_time: datetime | None = None


class GetUserInfoListDetails(GetUserInfoNoRelationDetail):
    model_config = ConfigDict(from_attributes=True)


class GetCurrentUserInfoDetail(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)


class CurrentUserIns(GetUserInfoListDetails):
    model_config = ConfigDict(from_attributes=True)


class ResetPasswordParam(SchemaBase):
    old_password: str
    new_password: str
    confirm_password: str
