from enum import Enum
from enum import IntEnum as SourceIntEnum
from typing import Type


class _EnumBase(Enum):
    @classmethod
    def get_member_keys(cls: Type[Enum]) -> list[str]:
        return [name for name in cls.__members__.keys()]

    @classmethod
    def get_member_values(cls: Type[Enum]) -> list:
        return [item.value for item in cls.__members__.values()]


class IntEnum(_EnumBase, SourceIntEnum):
    """Integer enumeration"""

    pass


class StrEnum(_EnumBase, str, Enum):
    """String enumeration"""

    pass


class AccountStatusType(IntEnum):
    """Account status type"""

    disable = 0
    enable = 1


class LoginLogStatusType(IntEnum):
    """Login log status"""

    fail = 0
    success = 1


class MethodType(StrEnum):
    """Request method"""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


class DirectionType(StrEnum):
    """Direction type"""

    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'
