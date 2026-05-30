import pytest
from httpx import AsyncClient
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import generate_password_reset_token
from app.core.config import settings
from app.api.deps import get_user_service
from app.models.user import UserCreate

from tests.helpers.util import random_email, random_lower_string

@pytest.mark.asyncio
async def test_get_users_superuser_me(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    r = await client.get(f"{settings.API_V1_STR}/auth/me", headers=superuser_token_headers)
   
    assert r.status_code == 200

    current_user = r.json()
   
    assert current_user
    assert current_user["is_active"] is True
    assert current_user['is_superuser']
    assert current_user["email"]== settings.FIRST_SUPERUSER
    assert "role" in current_user
    assert settings.DEFAULT_ROLE == current_user["role"] 

@pytest.mark.asyncio
async def test_get_users_normal_user_me(client: AsyncClient, normal_user_token_headers: dict[str, str]) -> None:
    
    r = await client.get(f"{settings.API_V1_STR}/auth/me", headers=normal_user_token_headers)
   
    assert r.status_code == 200

    current_user = r.json()
   
    assert current_user
    assert current_user["is_active"] is True
    assert current_user['is_superuser'] is False
    assert current_user["email"]== settings.EMAIL_TEST_USER
    assert "role" in current_user
    assert settings.DEFAULT_ROLE_USER == current_user["role"]

@pytest.mark.asyncio
async def test_get_access_token(client: AsyncClient) -> None:
    login_data = {
        "username": str(settings.FIRST_SUPERUSER),
        "password": str(settings.FIRST_SUPERUSER_PASSWORD)
    }
   
    r = await client.post(f"{settings.API_V1_STR}/auth/access-token", data=login_data)
    tokens = r.json()

    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
@pytest.mark.asyncio
async def test_get_access_token_incorrect_password(client: AsyncClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": 'incorectpass'
    }
    r = await client.post(f"{settings.API_V1_STR}/auth/access-token", data=login_data)
    assert r.status_code == 401

@pytest.mark.asyncio
async def test_recovery_password(client: AsyncClient, normal_user_token_headers: dict[str, str]) -> None:
    
    with(
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
        patch("app.core.config.settings.SMTP_PASSWORD", "hello cil"),
       
    ):
        email = "test@example.com"
        r = await client.post(f"{settings.API_V1_STR}/auth/password-recovery/{email}", headers=normal_user_token_headers)
        assert r.status_code == 200
        assert r.json() == {
            "message":"If that email is registered, we sent a password recovery link"
        }

@pytest.mark.asyncio     
async def test_recovery_password_user_not_exist(client: AsyncClient, normal_user_token_headers: dict[str, str]) -> None:
    
    email = "tesddt@example.com"
    r = await client.post(f"{settings.API_V1_STR}/auth/password-recovery/{email}", headers=normal_user_token_headers)
    
    assert r.status_code == 200

    # Return 200 juga supaya tidak ada percobaan email
    assert r.json() == {
        "message":"If that email is registered, we sent a password recovery link"
    }
@pytest.mark.asyncio
async def test_reset_password(client:AsyncClient, async_db: AsyncSession, role_user) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()
    service = get_user_service(async_db)

    #simulasi user
    user_in =  UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        role=role_user
    )
    await service.create_user(user_in)

    #cek user yang baru dibuat
    user = await service.user_crud.get_by_email(email)
    #pastikan object terbentuk
    assert user
    #pastion email nya sama
    assert email == user.email

    token = generate_password_reset_token(email=email)
    data = {"new_password": new_password, "token":token}
  
    r = await client.post(f"{settings.API_V1_STR}/auth/reset-password", json=data)


    assert r.status_code == 200
    assert r.json() == {"message":"Password updated successfully"}

    await async_db.refresh(user)

    verified, _ = service.verify_password(new_password, user.hashed_password)
    assert verified
    
@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient) -> None:
    data = {"new_password":"changetus", "token":"invalid"}
    r = await client.post(f"{settings.API_V1_STR}/auth/reset-password", json=data)
    resp = r.json()

    assert "detail" in resp
    assert r.status_code == 400
    assert resp["detail"] == "Invalid token"

