import uuid
from app.utils import logger
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserCreate, UserUpdate
from app.core.config import settings

from app.cruds.user_crud import UserCrud
from app.cruds.role_crud import RoleCrud

from app.services.user_service import UserService
from app.models.role import RoleCreate
from tests.helpers.util import random_email, random_lower_string

@pytest.mark.asyncio
async def test_create_user_service(async_db: AsyncSession, role:str) -> None:
    
    email = random_email()
    password = random_lower_string()

    
    user_crud = UserCrud(async_db)
    role_crud = RoleCrud(async_db)
    service = UserService(user_crud, role_crud)

    user_in = UserCreate(email=email, password=password, role=role)
    user = await service.create_user(user_in)
    
    assert user.email == email
    assert hasattr(user, "roles")
    assert any( settings.DEFAULT_ROLE == role.name for role in user.roles)
    
async def test_update_user_service(async_db: AsyncSession, role:str) -> None:
    
    email = random_email()
    password = random_lower_string()

    
    user_crud = UserCrud(async_db)
    role_crud = RoleCrud(async_db)
    service = UserService(user_crud, role_crud)

    user_in = UserCreate(email=email, password=password, role=role)
    user = await service.create_user(user_in)

    role_dummy:str = "Burio"

    role_in = RoleCreate(name=role_dummy)
    role_new = await service.create_role(role_in)

    user_in_update = UserUpdate(full_name='Kirun', role=role_new.name)
    if user.id is not None:
         await service.update_user(user, user_in=user_in_update)

    user_2 = await user_crud.session.get(User, user.id)
    assert user_2
    assert 'Kirun' == user_2.full_name

    assert any(role_dummy.lower() == role.name for role in user_2.roles)
    
