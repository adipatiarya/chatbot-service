from unittest.mock import patch

from fastapi.testclient import TestClient
from app.core.config import settings

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