from datetime import datetime

from sqlmodel import Column, DateTime, Field, SQLModel, Text

from src.utils.timezone import timezone


class LoginLog(SQLModel, table=True):
    """Login Log Table"""

    __tablename__: str = "sys_login_log"

    id: int = Field(primary_key=True)
    user_uuid: str = Field(max_length=50, description="User UUID")
    username: str = Field(max_length=20, description="Username")
    status: int = Field(default=0, description="Login Status (0:Failed 1:Success)")
    ip: str = Field(max_length=50, description="Login IP Address")
    country: str | None = Field(max_length=50, description="Country")
    region: str | None = Field(max_length=50, description="Region")
    city: str | None = Field(max_length=50, description="City")
    user_agent: str = Field(max_length=500, description="User Agent")
    os: str | None = Field(max_length=100, description="Operating System")
    browser: str | None = Field(max_length=100, description="Browser")
    device: str | None = Field(max_length=100, description="Device")
    msg: str = Field(sa_column=Column(Text), description="Message")
    login_time: datetime = Field(
        description="Login Time",
        sa_column=Column(DateTime(timezone=True), default=None),
    )
    created_time: datetime = Field(
        default_factory=timezone.now,
        description="Creation Time",
        sa_column=Column(DateTime(timezone=True), default=None),
    )
