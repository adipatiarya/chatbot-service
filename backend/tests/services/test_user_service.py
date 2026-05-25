import uuid
from app.utils import logger
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserCreate
from app.core.config import settings

from app.cruds.user_crud import UserCrud
from app.cruds.role_crud import RoleCrud

from app.services.user_service import UserService
from tests.helpers.util import random_email, random_lower_string

@pytest.mark.asyncio
async def test_create_user_service(async_db: AsyncSession, role_id:uuid.UUID) -> None:
    
    email = random_email()
    password = random_lower_string()

    
    user_crud = UserCrud(async_db)
    role_crud = RoleCrud(async_db)
    service = UserService(user_crud, role_crud)

    user_in = UserCreate(email=email, password=password, role_id=role_id)
    user = await service.create_user(user_in)
    
    assert user.email == email
    assert hasattr(user, "roles")
    assert any(role.id == role_id for role in user.roles)
    assert any( settings.DEFAULT_ROLE == role.name for role in user.roles)
    