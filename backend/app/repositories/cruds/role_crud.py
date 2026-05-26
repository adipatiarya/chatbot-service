
from sqlmodel import func, select

from app.models.role import Role
from app.repositories.cruds.crud import Crud


class RoleCrud(Crud[Role]):
    def __init__(self, session):
        super().__init__(session, Role)

    async def get_by_name(self, name: str) -> Role | None:
        statement = select(Role).where(func.lower(Role.name) == name.lower())
        result = await self.session.execute(statement)
        return result.scalars().first()