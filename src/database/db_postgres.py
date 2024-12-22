import sys

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.core.conf import settings

# Create async engine
POSTGRES_URL = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


def create_engine_and_session(url: str | URL):
    try:
        engine = create_async_engine(url, echo=False, future=True, pool_pre_ping=True)
    except Exception as e:
        print(f"❌ No connection to the database {e}")
        sys.exit()
    else:
        db_session = async_sessionmaker(
            bind=engine, autoflush=False, expire_on_commit=False
        )
        return engine, db_session


async_engine, async_db_session = create_engine_and_session(POSTGRES_URL)


# Create tables function (call this on startup)
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Session dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_db_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# Type hint for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_session)]
