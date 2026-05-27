
from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlmodel import   SQLModel as Base

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
from app.models.permission import Permission, RolePermission

from app.api.deps import get_user_service, get_db, get_role_service
from app.main import app

from tests.helpers.util import permissions_test

async_engine = create_async_engine(
    url='postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db_test',
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
        for model in [UserRole, User, Role, Permission, RolePermission]:
            await session.execute(delete(model))
        await session.commit()

@pytest_asyncio.fixture(scope="function")
async def role(async_db: AsyncSession)->str:
    role_in = RoleCreate(name=settings.DEFAULT_ROLE, description='Hello Role')
    service = get_role_service(async_db)
    role = await service.create_role(role_in)
    return role.name



@pytest_asyncio.fixture(scope="function")
async def role_user(async_db: AsyncSession)->str:
    
    role_in = RoleCreate(name=settings.DEFAULT_ROLE_USER, description='Hello Role User')
    service = get_role_service(async_db)
    role = await service.create_role(role_in)
    return role.name


@pytest_asyncio.fixture(scope="function", autouse=True)
async def client(async_db, role):

   

    #crete user fisrt
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
    def override_get_db():
        yield async_db
    app.dependency_overrides[get_db] = override_get_db
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")

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


@pytest.fixture
async def normal_user_token_headers(async_db: AsyncSession, client: AsyncClient, role_user:str) -> dict[str, str]:
    username = settings.EMAIL_TEST_USER
    password = 'randompasswd'
    
    service = get_user_service(async_db)
    user = await service.user_crud.get_by_email(username)
    
    role = role_user #cek in env default_role_user

    if not user:
        user_in = UserCreate(
            email=username,
            password=password,
            role=role
        )
        await service.create_user(user_in)

    login_data = {
        "username": username,
        "password": password
    }
   
    r = await client.post(f"{settings.API_V1_STR}/auth/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization":f"Bearer {a_token}"}
    return headers
