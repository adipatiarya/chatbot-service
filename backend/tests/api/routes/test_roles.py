import json

import pytest
from httpx import AsyncClient
from app.core.config import settings

@pytest.mark.asyncio
async def test_create_roles(client: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    payload = {
        "name": "string",
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
    assert "name" in resp
    assert "description" in resp
    assert "permission" in resp
    assert json.dumps(resp["permission"], sort_keys=True) == json.dumps(payload["permission"], sort_keys=True)