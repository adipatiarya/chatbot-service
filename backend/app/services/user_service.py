import uuid

from sqlalchemy import delete
from sqlmodel import select

from app.cruds.user_crud import UserCrud
from app.cruds.role_crud import RoleCrud
from app.models.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.models.user_role import UserRole
from app.models.role import RoleCreate, Role

class UserService:
    def __init__(self, user_crud: UserCrud, role_crud: RoleCrud):
        self.user_crud = user_crud
        self.role_crud = role_crud

    async def assign_role(self, user_id: uuid.UUID, role_name: str) -> UserRole:

        user = await self.user_crud.get_by_id(user_id)
        role = await self.role_crud.get_by_name(role_name)
        if not user or not role:
            raise ValueError("User atau Role tidak ditemukan")
        
        link = UserRole(user_id=user_id, role_id=role.id)
        self.user_crud.session.add(link)
        await self.user_crud.session.commit()
        await self.user_crud.session.refresh(link)
        
        return link
    
    async def delete_all_role(self, user_id: uuid.UUID):
        try:
            await self.user_crud.session.execute(
                delete(UserRole).where(UserRole.user_id == user_id)
            )
            await self.user_crud.session.commit()
        except Exception:
            await self.user_crud.session.rollback()
            raise

    async def create_user(self, user_create: UserCreate) -> User:
        user_model = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
        )
        user = await self.user_crud.add(user_model)

        await self.assign_role(user.id, user_create.role)
        return await self.user_crud.get_user_roles(user.id)
    
    async def update_user(self, db_user: User, user_in: UserUpdate) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        if "role" in user_data:
            await self.delete_all_role(db_user.id)
            await self.assign_role(db_user.id, user_data["role"])
        db_user.sqlmodel_update(user_data, update=extra_data)

        user = await self.user_crud.add(db_user)
        
        return await self.user_crud.get_user_roles(user.id)

    async def create_role(self, role_create: RoleCreate) -> Role:
        role_model = Role.model_validate(role_create)
        role = await self.role_crud.add(role_model)
        return role
