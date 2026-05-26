import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserCreate, UserUpdate
from app.core.config import settings

from app.models.role import RoleCreate
from tests.helpers.util import random_email, random_lower_string
from app.api.deps import get_user_service

@pytest.mark.asyncio
async def test_create_user_service(async_db: AsyncSession, role:str) -> None:
    
    email = random_email()
    password = random_lower_string()
    service = get_user_service(async_db)
    user_in = UserCreate(email=email, password=password, role=role)
    user = await service.create_user(user_in)
    
    assert user.email == email
    assert hasattr(user, "roles")
    assert any( settings.DEFAULT_ROLE == role.name for role in user.roles)
    
async def test_update_user_service(async_db: AsyncSession, role:str) -> None:
    
    email = random_email()
    password = random_lower_string()

    service = get_user_service(async_db)

    user_in = UserCreate(email=email, password=password, role=role)
    user = await service.create_user(user_in)

    role_dummy:str = "Burio"

    role_in = RoleCreate(name=role_dummy)
    role_new = await service.create_role(role_in)

    user_in_update = UserUpdate(full_name='Kirun', role=role_new.name)
    if user.id is not None:
         await service.update_user(user, user_in=user_in_update)

    user_2 = await service.user_crud.session.get(User, user.id)
    assert user_2
    assert 'Kirun' == user_2.full_name

    assert any(role_dummy.lower() == role.name for role in user_2.roles)
    

@pytest.mark.asyncio
async def test_authenticate_user_user(async_db: AsyncSession, role:str) -> None:
    email = random_email()
    password = random_lower_string()

    service = get_user_service(async_db)
    user_in = UserCreate(email=email, password=password, role=role)

    user = await service.create_user(user_create=user_in)
    authenticate_user = await service.authenticate(email=email, password=password)
    assert authenticate_user
    assert user.email == authenticate_user.email