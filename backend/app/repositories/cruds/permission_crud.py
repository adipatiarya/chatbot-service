
import uuid

from sqlalchemy.orm import selectinload
from sqlmodel import func, select

from .crud import Crud
from app.models.permission import Permission

class PermissionCrud(Crud[Permission]):
    def __init__(self, session):
        super().__init__(session, Permission)
    
    async def get_by_name_or_id(self, name: uuid.UUID | str) -> Permission | None:
        stmt = select(Permission).options(selectinload(Permission.roles)).where(
            Permission.id == name if isinstance(name, uuid.UUID) else Permission.name == name
        )
        try:
            result = await self.session.execute(stmt)
            return result.scalars().first()
        except:
            return None