import pytest
from httpx import AsyncClient
from app.core.config import settings
from tests.helpers.util import random_email, random_lower_string

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient , superuser_token_headers: dict[str, str]) -> None:
    #create role permision dulu
    role_name  = random_lower_string()

    payload = {
        "name": role_name,
        "description": "string",
        "permission": {
            "user": {
                "can_create_user": False,
                "can_delete_user": True,
                "can_update_user": False,
                "can_view_user": False
            },
            "role": {
                "can_create_role": False,
                "can_delete_role": False,
                "can_update_role": True,
                "can_view_role": False
            }
        }
    }

    r = await client.post(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers, json=payload)
    assert 201 == r.status_code

    email = random_email()
    password = random_lower_string()

    payload = {
        'email':email,
        'password':password,
        'role': role_name
    }
    r = await client.post(f"{settings.API_V1_STR}/users", headers=superuser_token_headers, json=payload)
    assert 201 == r.status_code  

    #cek dooble
    r = await client.post(f"{settings.API_V1_STR}/users", headers=superuser_token_headers, json=payload)
    assert 400 == r.status_code #pastikan error

@pytest.mark.asyncio
async def test_get_user(client: AsyncClient , superuser_token_headers: dict[str, str]) -> None:
    #create role permision dulu
    role_name  = random_lower_string()

    payload = {
        "name": role_name,
        "description": "string",
        "permission": {
            "user": {
                "can_create_user": True,
                "can_delete_user": True,
                "can_update_user": False,
                "can_view_user": False
            },
            "role": {
                "can_create_role": False,
                "can_delete_role": False,
                "can_update_role": True,
                "can_view_role": False
            }
        }
    }

    r = await client.post(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers, json=payload)
    assert 201 == r.status_code

    email = random_email()
    password = random_lower_string()

    payload = {
        'email':email,
        'password':password,
        'role': role_name
    }
    r = await client.post(f"{settings.API_V1_STR}/users", headers=superuser_token_headers, json=payload)
    assert 201 == r.status_code
    resp = r.json()
    assert resp

    #cek dooble
    r = await client.get(f"{settings.API_V1_STR}/users/{resp['id']}", headers=superuser_token_headers)
    assert 200 == r.status_code #pastikan error
    resp = r.json()
    assert payload["email"] == resp['email']
    assert payload["role"] == resp['role']