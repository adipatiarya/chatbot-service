import uuid

from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.models.user import User
from app.repositories.cruds.crud import Crud

class UserCrud(Crud[User]):
    def __init__(self, session):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.roles)).where(User.email == email)
        )
        return result.scalars().first()
    
    async def get_user_roles(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
        user = result.scalars().first()
        return user