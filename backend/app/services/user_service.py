import uuid

from app.cruds.user_crud import UserCrud
from app.cruds.role_crud import RoleCrud
from app.models.user import User, UserCreate
from app.core.security import get_password_hash
from app.models.user_role import UserRole

class UserService:
    def __init__(self, user_crud: UserCrud, role_crud: RoleCrud):
        self.user_crud = user_crud
        self.role_crud = role_crud

    async def assign_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:

        user = await self.user_crud.get_by_id(user_id)
        role = await self.role_crud.get_by_id(role_id)
        if not user or not role:
            raise ValueError("User atau Role tidak ditemukan")
        
        link = UserRole(user_id=user_id, role_id=role_id)
        self.user_crud.session.add(link)
        await self.user_crud.session.commit()
        await self.user_crud.session.refresh(link)
        
        return link
       

    async def create_user(self, user_create: UserCreate) -> User:
        user = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        assign = await self.user_crud.add(user)
        await self.assign_role(assign.id, user_create.role_id)
        return await self.user_crud.get_user_roles(assign.id)
     