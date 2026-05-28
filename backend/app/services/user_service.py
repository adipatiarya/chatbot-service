import uuid
import jwt
from datetime import timedelta, datetime, timezone
from typing import Any

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import delete
from app.core.config import settings

from app.repositories.cruds.user_crud import UserCrud
from app.repositories.cruds.role_crud import RoleCrud


from app.models.user import User, UserCreate, UserPublic, UserUpdate
from app.models.user_role import UserRole

class UserService:
    def __init__(self, user_crud: UserCrud, role_crud: RoleCrud):
        self.user_crud = user_crud
        self.role_crud = role_crud
    
    @property
    def password_hash(self):
         self = PasswordHash((Argon2Hasher(),BcryptHasher()))
         return self
    
    def get_password_hash(self, password: str) -> str:

        return self.password_hash.hash(password)

    def verify_password(self, plain_password:str, hashed_password:str) -> tuple[bool, str | None] :
        return self.password_hash.verify_and_update(plain_password, hashed_password)

    def create_access_token(self, subject:str | Any, expires_delta:timedelta) -> str:
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode = {"exp": expire, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def assign_role(self, user_id: uuid.UUID, role_name: str) -> UserRole:

        user = await self.user_crud.get_by_id(user_id)
        role = await self.role_crud.get_by_name_or_id(role_name)
      
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
            update={"hashed_password": self.get_password_hash(user_create.password)},
        )
        user = await self.user_crud.add(user_model)

        await self.assign_role(user.id, user_create.role)
        return await self.user_crud.roles(user.id)
    
    async def update_user(self, db_user: User, user_in: UserUpdate) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = self.get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        if "role" in user_data:
            await self.delete_all_role(db_user.id)
            await self.assign_role(db_user.id, user_data["role"])
        db_user.sqlmodel_update(user_data, update=extra_data)

        user = await self.user_crud.add(db_user)
        
        return await self.user_crud.roles(user.id)

    async def authenticate(self, email:str, password:str) -> User | None:
        db_user = await self.user_crud.get_by_email(email)
        if not db_user:
            return None
        verified, update_password_hash = self.verify_password(password, db_user.hashed_password)
        if not verified:
            return None
        if update_password_hash:
            db_user.hashed_password = update_password_hash
            await self.user_crud.add(db_user)
        return db_user
    
    def populate_user(self, user: User) -> UserPublic:
        extra_data = {
            "role": None,
            "permissions": []
        }

        if user.roles:
            role = user.roles[0]  # ambil role pertama
            extra_data["role"] = role.name
            perms = {p.name for r in user.roles for p in r.permissions}
            extra_data["permissions"] = list(perms)
        
        return UserPublic(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            **extra_data
        )
