
import uuid

import pytest_asyncio
from sqlalchemy import delete
from app.models import Base
from app.core.config import settings
from app.core.db import init_db
from app import crud
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.models.user import User
from app.models.role import Role, RoleCreate
from app.models.user_role import UserRole

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
async def role_id(async_db: AsyncSession)->uuid.UUID:
    role_in = RoleCreate(name=settings.DEFAULT_ROLE, description='Hello Role')
    role = await crud.create_role(session=async_db, role_create=role_in)
    await init_db(async_db, role.id)
    return role.id
