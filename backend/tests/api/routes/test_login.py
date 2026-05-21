from unittest.mock import patch
from sqlmodel import Session
from fastapi.testclient import TestClient

from app.core.config import settings
from app.models import UserCreate
from app import crud
from app.utils import generate_password_reset_token

from tests.helpers.user import user_authentication_headers
from tests.helpers.util import random_email, random_lower_string

def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()

    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]

def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": 'incorectpass'
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 400

def test_user_access_token(client: TestClient, superuser_token_headers: dict[str, str]) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers
        )
    result = r.json()

    assert r.status_code == 200
    assert "email" in result

def test_recovery_password(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    
    with(
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
        patch("app.core.config.settings.SMTP_PASSWORD", "hello cil"),
       
    ):
        email = "test@example.com"
        r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}", headers=normal_user_token_headers)
        assert r.status_code == 200
        assert r.json() == {
            "message":"If that email is registered, we sent a password recovery link"
        }
        
def test_recovery_password_user_not_exist(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    
    email = "tesddt@example.com"
    r = client.post(f"{settings.API_V1_STR}/password-recovery/{email}", headers=normal_user_token_headers)
    
    assert r.status_code == 200

    # Return 200 juga supaya tidak ada percobaan email
    assert r.json() == {
        "message":"If that email is registered, we sent a password recovery link"
    }

def test_reset_password(client:TestClient, sess:Session) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    user_create =  UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False 
    )

    user = crud.create_user(session=sess, user_create=user_create)
    token = generate_password_reset_token(email=email)
    data = {"new_password": new_password, "token":token}

    r = client.post(f"{settings.API_V1_STR}/reset-password", json=data)
    
    assert r.status_code == 200
    assert r.json() == {"message":"Password updated successfully"}

    sess.refresh(user)

