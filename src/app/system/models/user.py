import uuid

from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel, String

from src.utils.timezone import timezone


class User(SQLModel, table=True):
    """User Table"""

    __tablename__: str = 'sys_user'

    id: int = Field(primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, max_length=50)
    username: str = Field(sa_column=Column(String(20), unique=True, index=True, comment='Username'))
    password: str = Field(max_length=255, description='Password')
    salt: bytes | None = Field(description='Encryption salt')
    email: str = Field(unique=True, index=True, max_length=50, description='Email')
    is_superuser: bool = Field(default=False, description='Super admin permissions (0 no, 1 yes)')
    status: int = Field(default=1, description='User account status (0 disabled, 1 normal)')
    is_multi_login: bool = Field(default=False, description='Allow multiple logins (0 no, 1 yes)')
    avatar: str | None = Field(default=None, max_length=255, description='Avatar')

    join_time: datetime = Field(
        default_factory=timezone.now,
        description='Registration time',
        sa_column=Column(DateTime(timezone=True)),
    )
    last_login_time: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), default=None, onupdate=timezone.now),
        description='Last login time',
    )
