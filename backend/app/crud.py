import uuid

from sqlalchemy.orm import selectinload
from sqlmodel import  select

from app.models.user import UserCreate, User, UserUpdate
from app.models.role import Role, RoleCreate
from app.models.user_role import UserRole
from app.utils import logger
from app.core.security import get_password_hash, verify_password
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

async def assign_role_to_user(*, session: AsyncSession, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole:
    try:
        # cek apakah user ada
        user = await session.get(User, user_id)
        if not user:
            raise ValueError(f"User dengan id {user_id} tidak ditemukan")

        # cek apakah role ada
        role = await session.get(Role, role_id)
        if not role:
            raise ValueError(f"Role dengan id {role_id} tidak ditemukan")

        # buat link
        link = UserRole(user_id=user_id, role_id=role_id)
        session.add(link)
        await session.commit()
        await session.refresh(link)
        return link

    except Exception as e:
        await session.rollback()
        logger.error(f"assign_role_to_user error: {e}")
        raise

async def get_user_by_email(*, session: AsyncSession, email:str) -> User | None:
    statemen = select(User).where(User.email == email)
    session_user = await session.execute(statemen)
    return session_user.scalars().first()

async def create_user(*, session:  AsyncSession, user_create: UserCreate) -> User:
    try:
        db_obj = User.model_validate(user_create,update={"hashed_password": get_password_hash(user_create.password)})
        session.add(db_obj)
        await session.commit()
        await assign_role_to_user(session=session, user_id=db_obj.id, role_id=user_create.role_id)
        await session.refresh(db_obj)
        return db_obj
    except Exception as e:
        await session.rollback()
        logger.error(f"create_user error: {e}")
        raise 
   


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        verify_password(plain_password=password, hashed_password=DUMMY_HASH)
        return None
    
    virified, update_password_hash = verify_password(plain_password=password, hashed_password=db_user.hashed_password)
    
    if not virified:
        return None
    if update_password_hash:
        db_user.hashed_password = update_password_hash
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

    return db_user

async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user

async def get_role_by_id(*, session: AsyncSession, id:uuid.UUID) -> Role | None:
    session_role = await session.get(Role, id)
    return session_role

async def create_role(*, session:  AsyncSession, role_create: RoleCreate) -> Role:
    db_obj = Role.model_validate(role_create)
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj

async def get_user_with_roles(*,session: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await session.execute(select(User).options(selectinload(User.roles)).where(User.id == user_id))
    user = result.scalars().first()
    return user