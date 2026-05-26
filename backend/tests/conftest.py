
from httpx import ASGITransport, AsyncClient
import pytest
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

from app.models.user import User, UserCreate
from app.models.role import Role, RoleCreate
from app.models.user_role import UserRole
from app.api.deps import get_user_service
from app.main import app

async_engine = create_async_engine(
    url=str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    poolclass=NullPool,
)


# Drop all tables after each test
@pytest.fixture(scope="session", autouse=True)
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
    return role.name


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def superuser_token_headers(async_db: AsyncSession, client: AsyncClient, role:str) -> dict[str, str]:
    service = get_user_service(async_db)
    user = await service.user_crud.get_by_email(settings.FIRST_SUPERUSER)

    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            role=role
        )
        await service.create_user(user_in)

    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD
    }
    # user = await service.user_crud.get_by_email(settings.FIRST_SUPERUSER)
    # print(user)
    r = await client.post(f"{settings.API_V1_STR}/auth/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization":f"Bearer {a_token}"}
    return headers
