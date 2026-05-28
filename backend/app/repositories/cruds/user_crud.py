import uuid

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.user import User
from app.models.role import Role
from .crud import Crud

class UserCrud(Crud[User]):
    def __init__(self, session):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.roles)).where(User.email == email)
        )
        return result.scalars().first()
    
    async def roles(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id))
        user = result.scalar_one()
        return user
    