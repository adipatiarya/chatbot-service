
from sqlmodel import func, select

from .crud import Crud
from app.models.permission import Permission

class PermissionCrud(Crud[Permission]):
    def __init__(self, session):
        super().__init__(session, Permission)

    async def roles(self):
        pass
    
    async def get_by_name(self, name: str) -> Permission | None:
        statement = select(Permission).where(func.lower(Permission.name) == name.lower())
        result = await self.session.execute(statement)
        return result.scalars().first()