import json

import pytest
from httpx import AsyncClient
from app.core.config import settings

from tests.helpers.util import random_lower_string

@pytest.mark.asyncio
async def test_create_roles(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:

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
                "can_update_role": False,
                "can_view_role": False
            }
        }
    }

    r = await client.post(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers, json=payload)
    assert 201 == r.status_code
    resp = r.json()
    assert resp
    assert "id" in resp
    assert "name" in resp
    assert role_name == resp["name"]
    assert "description" in resp
    assert "permission" in resp
    assert json.dumps(resp["permission"], sort_keys=True) == json.dumps(payload["permission"], sort_keys=True)

@pytest.mark.asyncio
async def test_role_by_id(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:

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
                "can_view_role": True
            }
        }
    }
    #buat dulu
    r = await client.post(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers, json=payload)

    data = r.json()
    id = data["id"]
 
    
    r = await client.get(f"{settings.API_V1_STR}/roles/{id}", headers=superuser_token_headers)
    assert 200 == r.status_code
    resp = r.json()
    assert resp
    assert "id" in resp
    assert "name" in resp
    assert role_name == resp["name"]
    assert "description" in resp
    assert "permission" in resp
    assert json.dumps(resp["permission"], sort_keys=True) == json.dumps(payload["permission"], sort_keys=True)





