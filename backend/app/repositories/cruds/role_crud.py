
from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from app.models.role import Role
from .crud import Crud

class RoleCrud(Crud[Role]):
    def __init__(self, session):
        super().__init__(session, Role)

    async def get_by_name(self, name: str) -> Role | None:
        statement = select(Role).where(func.lower(Role.name) == name.lower())
        result = await self.session.execute(statement)
        return result.scalars().first()
    
    async def permissions(self, role_id)->Role:
        result = await self.session.execute(select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id))
        role = result.scalars().first()
        return role