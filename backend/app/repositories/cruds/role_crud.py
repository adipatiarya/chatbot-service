
import uuid

from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.models.role import Role
from .crud import Crud

class RoleCrud(Crud[Role]):
    def __init__(self, session):
        super().__init__(session, Role)

    async def get_by_name_or_id(self, role: uuid.UUID | str) -> Role | None:
        stmt = select(Role).options(selectinload(Role.permissions)).where(
            Role.id == role if isinstance(role, uuid.UUID) else Role.name == role
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except:
            return None