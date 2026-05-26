# repositories/base_repository.py
from typing import TypeVar, Generic, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

    async def add(self, obj: T) -> T:
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
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
