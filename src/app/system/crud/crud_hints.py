from typing import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.system.crud.base import CRUDBase
from src.app.system.models.hints import Hint
from src.app.system.schema.hints import HintCreate, HintUpdate
from src.common.enums import DirectionType


class CRUDHints(CRUDBase[Hint, HintCreate, HintUpdate]):
    async def get_by_direction(self, db: AsyncSession, direction: DirectionType, x: int, y: int) -> Sequence[Hint]:
        if direction == DirectionType.RIGHT:
            return await self.get_hints_right(db, x=x, y=y)
        elif direction == DirectionType.LEFT:
            return await self.get_hints_left(db, x=x, y=y)
        elif direction == DirectionType.UP:
            return await self.get_hints_up(db, x=x, y=y)
        elif direction == DirectionType.DOWN:
            return await self.get_hints_down(db, x=x, y=y)
        else:
            raise ValueError('Invalid direction')

    async def get_hints_right(self, db: AsyncSession, y: int, x: int) -> Sequence[Hint]:
        query = select(Hint).where(Hint.posY == y, Hint.posX > x, Hint.posX <= x + 10)
        result = await db.exec(query)
        return result.all()

    async def get_hints_left(self, db: AsyncSession, y: int, x: int) -> Sequence[Hint]:
        query = select(Hint).where(Hint.posY == y, Hint.posX < x, Hint.posX >= x - 10)
        result = await db.exec(query)
        return result.all()

    async def get_hints_up(self, db: AsyncSession, x: int, y: int) -> Sequence[Hint]:
        query = select(Hint).where(Hint.posX == x, Hint.posY < y, Hint.posY >= y - 10)
        result = await db.exec(query)
        return result.all()

    async def get_hints_down(self, db: AsyncSession, x: int, y: int) -> Sequence[Hint]:
        query = select(Hint).where(Hint.posX == x, Hint.posY > y, Hint.posY <= y + 10)
        result = await db.exec(query)
        return result.all()


hints_dao = CRUDHints(Hint)
