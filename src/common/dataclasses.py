import dataclasses

from datetime import datetime


@dataclasses.dataclass
class NewToken:
    new_access_token: str
    new_access_token_expire_time: datetime
    new_refresh_token: str
    new_refresh_token_expire_time: datetime


@dataclasses.dataclass
class AccessToken:
    access_token: str
    access_token_expire_time: datetime


@dataclasses.dataclass
class RefreshToken:
    refresh_token: str
    refresh_token_expire_time: datetime
