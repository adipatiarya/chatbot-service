
import pytest_asyncio
from sqlalchemy import delete
from app.models import Base
from app.core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.models.user import User
from app.models.role import Role, RoleCreate
from app.models.user_role import UserRole
from app.api.deps import get_user_service
from app.core.db import init_db

async_engine = create_async_engine(
    url=str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    poolclass=NullPool,
)


# Drop all tables after each test
@pytest_asyncio.fixture(scope="function")
async def async_db_engine():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_engine

    async with async_engine.begin() as conn:
        
        await conn.run_sync(Base.metadata.drop_all)



@pytest_asyncio.fixture(scope="function")
async def async_db(async_db_engine):
    async_session = async_sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_engine,
        class_=AsyncSession,
    )

    async with async_session() as session:
        await session.commit()
        yield session
        await session.execute(delete(UserRole))
        await session.execute(delete(User))
        await session.execute(delete(Role))
        await session.commit()

@pytest_asyncio.fixture(scope="function")
async def role(async_db: AsyncSession)->str:
    role_in = RoleCreate(name=settings.DEFAULT_ROLE, description='Hello Role')
    service = get_user_service(async_db)
    role = await service.create_role(role_in)
    await init_db(service, role.name)
    return role.name
