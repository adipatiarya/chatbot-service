# repositories/base_repository.py
from datetime import datetime
from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import asc, desc, or_

from app.core.exception import commit_with_integrity

T = TypeVar("T")  # tipe model (User, Role, dll)

class Crud(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, obj_id) -> T | None:
        return await self.session.get(self.model, obj_id)

    async def list_all(self) -> list[T]:
        result = await self.session.execute(select(self.model))
        return result.scalars().all()
    
    async def list_filtered(
        self,
        page: int = 1,
        limit: int = 10,
        filters: dict[str, str] | None = None,
        search: str | None = None,
        order_by: str = "created_at",
        order_dir: str = "asc",
        start_date: datetime | None = None,
        end_date: datetime | None = None
    ) -> list[T]:
        query = select(self.model)

        # generic filters (by specific field)
        if filters:
            for field, value in filters.items():
                column = getattr(self.model, field, None)
                if column is not None and value:
                    query = query.where(column.ilike(f"%{value}%"))

        # multi-field search (keyword dicari di beberapa kolom sekaligus)
        if search:
            query = query.where(
                or_(
                    self.model.name.ilike(f"%{search}%"),
                    self.model.description.ilike(f"%{search}%")
                )
            )

        # range filter (created_at)
        if start_date:
            query = query.where(self.model.created_at >= start_date)
        if end_date:
            query = query.where(self.model.created_at <= end_date)

        # sorting
        column = getattr(self.model, order_by, None)
        if column is not None:
            query = query.order_by(desc(column) if order_dir.lower() == "desc" else asc(column))

        # pagination
        result = await self.session.execute(
            query.offset((page - 1) * limit).limit(limit)
        )
        return result.scalars().all()

    async def add(self, obj: T) -> T:
        try:
            self.session.add(obj)
            await commit_with_integrity(self.session)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except Exception:
            await self.session.rollback()
            raise
    async def add_many(self, objs: list[T]) -> list[T]:
        try:
            self.session.add_all(objs)
            
            await commit_with_integrity(self.session)
            
            await self.session.commit()

            for obj in objs:
                await self.session.refresh(obj)

            return objs
        except Exception:
            await self.session.rollback()
            raise

    async def delete(self, obj: T) -> None:
        try:
            await self.session.delete(obj)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
