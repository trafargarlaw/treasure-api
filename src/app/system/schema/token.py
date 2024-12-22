from datetime import datetime

from src.app.system.schema.user import GetUserInfoNoRelationDetail
from src.common.schema import SchemaBase


class GetSwaggerToken(SchemaBase):
    access_token: str
    token_type: str = "Bearer"
    user: GetUserInfoNoRelationDetail


class AccessTokenBase(SchemaBase):
    access_token: str
    access_token_type: str = "Bearer"
    access_token_expire_time: datetime


class GetNewToken(AccessTokenBase):
    pass


class GetLoginToken(AccessTokenBase):
    user: GetUserInfoNoRelationDetail
