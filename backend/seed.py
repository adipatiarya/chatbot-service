from sqlalchemy.orm import sessionmaker

from app.api.deps import get_user_service, get_role_service
from app.models.user import UserCreate, UserUpdate
from app.models.role import RoleCreate
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import engine

import asyncio

from app.utils import all_perms
async def initial_role(sess: AsyncSession):
    result = []
    for _, perms in all_perms().items():
        for perm_name, _ in perms.items():
            result.append(perm_name)


    default_role = settings.DEFAULT_ROLE
    service = get_role_service(sess)
    await service.create_permissions(result)

    role = await service.role_crud.get_by_name_or_id(default_role)
    if role is None:
        print(f"Role {default_role} akan dibuat")
        role_in = RoleCreate(name=default_role, permission_strs=result, description='Ini adalah role superuser')
        role = await service.create_role(role_in)
    return role
   
async def initial_user(sess: AsyncSession, role_name):
    default_email = settings.FIRST_SUPERUSER
    default_password = settings.FIRST_SUPERUSER_PASSWORD 
    service_user = get_user_service(sess)
    user = await service_user.user_crud.get_by_email(default_email)
    if user is None:
        print('Create user')
        user_in = UserCreate(email=default_email, password=default_password, role=role_name, is_superuser=True)
        user = await service_user.create_user(user_in)
    user_in = UserUpdate(email=default_email, password=default_password, role=role_name, is_superuser=True)
    user = await service_user.update_user(user, user_in)
    return user
       
   
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


if __name__ == "__main__":
    async def main():
      async with AsyncSessionLocal() as session:
            await initial_role(session)

            default_role = settings.DEFAULT_ROLE
            service = get_role_service(session)
            role = await service.role_crud.get_by_name_or_id(default_role)
            if role:
                user = await initial_user(session, role.name)
                print(user)

    asyncio.run(main())