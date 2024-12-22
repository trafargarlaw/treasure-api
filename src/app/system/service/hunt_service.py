from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.system.crud.crud_hints import hints_dao
from src.app.system.models.hints import Hint
from src.common.enums import DirectionType
from src.database.db_postgres import async_engine


class HuntService:
    @staticmethod
    async def get_hints(x: int, y: int, direction: DirectionType) -> list[Hint]:
        async with AsyncSession(async_engine) as db:
            hints = await hints_dao.get_by_direction(db=db, direction=direction, x=x, y=y)
            return list(hints)
