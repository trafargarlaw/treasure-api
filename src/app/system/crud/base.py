from typing import Any, Dict, Generic, List, Type, TypeVar

from pydantic import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, *, pk: int | None = None) -> ModelType | None:
        """
        Get one record by primary key id

        :param db:
        :param pk:
        :return:
        """
        model = await db.exec(select(self.model).where(getattr(self.model, "id") == pk))
        return model.first()

    async def create(
        self, db: AsyncSession, obj_in: CreateSchemaType, user_id: int | None = None
    ) -> ModelType:
        """
        Create one new record

        :param db:
        :param obj_in: Pydantic model class
        :param user_id:
        :return:
        """
        if user_id:
            create_data = self.model(**obj_in.model_dump(), create_user=user_id)
        else:
            create_data = self.model(**obj_in.model_dump())

        db.add(create_data)

        await db.commit()
        await db.refresh(create_data)

        return create_data

    async def update(
        self,
        db: AsyncSession,
        pk: int,
        obj_in: UpdateSchemaType | Dict[str, Any],
    ) -> ModelType | None:
        """
        Update one record by primary key id

        :param db:
        :param pk:
        :param obj_in: Pydantic model class or dictionary matching database fields
        :return:
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump()
        result = await db.exec(
            select(self.model).where(getattr(self.model, "id") == pk)
        )
        model = result.first()
        if model is None:
            return None
        for key, value in update_data.items():
            setattr(model, key, value)
        await db.commit()
        await db.refresh(model)
        return model

    async def delete(self, db: AsyncSession, pk: int) -> None:
        """
        Delete one record by primary key id

        :param db:
        :param pk:
        :return:
        """

        result = await db.exec(
            select(self.model).where(getattr(self.model, "id") == pk)
        )
        model = result.one()
        await db.delete(model)
        await db.commit()

    async def list(self, db: AsyncSession, **kwargs) -> list[ModelType]:
        """
        Get all records
        """
        result = await db.exec(select(self.model).filter_by(**kwargs))
        return list(result.unique().all())

    # bulk operations
    async def bulk_create(
        self,
        db: AsyncSession,
        objects: List[CreateSchemaType],
        user_id: int | None = None,
    ) -> bool:
        """
        Create multiple records in bulk

        :param db:
        :param objects: List of Pydantic model objects
        :param user_id:
        :return:
        """
        db_objects = []
        for obj_in in objects:
            if user_id:
                db_obj = self.model(**obj_in.model_dump(), create_user=user_id)
            else:
                db_obj = self.model(**obj_in.model_dump())
            db_objects.append(db_obj)

        db.add_all(db_objects)
        await db.commit()

        return True
