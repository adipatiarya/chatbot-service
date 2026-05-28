import json

from faker import Faker
import pytest
from httpx import AsyncClient
from app.core.config import settings

from tests.helpers.util import random_lower_string
from app.utils import logger

#normal_user_token_headers
@pytest.mark.asyncio
async def test_get_all_role(client: AsyncClient, normal_user_token_headers: dict[str, str]) -> None:
    r = await client.get(f"{settings.API_V1_STR}/roles", headers=normal_user_token_headers)
    assert 200 == r.status_code

@pytest.mark.asyncio
async def test_create_roles(client: AsyncClient, normal_user_token_headers: dict[str, str]) -> None:

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

    r = await client.post(f"{settings.API_V1_STR}/roles", headers=normal_user_token_headers, json=payload)
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
async def test_role_by_id(client: AsyncClient, normal_user_token_headers: dict[str, str]) -> None:

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
    r = await client.post(f"{settings.API_V1_STR}/roles", headers=normal_user_token_headers, json=payload)

    data = r.json()
    id = data["id"]
 
    
    r = await client.get(f"{settings.API_V1_STR}/roles/{id}", headers=normal_user_token_headers)
    assert 200 == r.status_code
    resp = r.json()
    assert resp
    assert "id" in resp
    assert "name" in resp
    assert role_name == resp["name"]
    assert "description" in resp
    assert "permission" in resp
    assert json.dumps(resp["permission"], sort_keys=True) == json.dumps(payload["permission"], sort_keys=True)


faker = Faker()

@pytest.mark.asyncio
async def test_bulk_insert_and_pagination(client: AsyncClient, normal_user_token_headers: dict[str, str]):
    # generate 10 dummy roles
    roles_data = []
    for _ in range(10):
        roles_data.append({
            "name": faker.word(),
            "description": faker.sentence(),
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
        })

    # insert semua role dummy
    for role in roles_data:
        resp = await client.post(f"{settings.API_V1_STR}/roles", json=role,  headers=normal_user_token_headers)
        assert resp.status_code == 201

    # test pagination → ambil 5 pertama
    resp = await client.get(f"{settings.API_V1_STR}/roles?page=1&limit=5&order_by=name&order_dir=asc", headers=normal_user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 5

    # test pagination → ambil page 2
    resp = await client.get(f"{settings.API_V1_STR}/roles?page=2&limit=5&order_by=name&order_dir=asc", headers=normal_user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) == 5


@pytest.mark.asyncio
async def test_filter_with_faker(client: AsyncClient, normal_user_token_headers: dict[str, str]):
    # generate satu role dengan keyword unik
    unique_name = "superadmin_" + faker.word()
    role_data = {
        "name": unique_name,
        "description": faker.sentence(),
     
    }

    resp = await client.post(f"{settings.API_V1_STR}/roles", json=role_data, headers=normal_user_token_headers)
    assert resp.status_code == 201

    # test filter by name
    resp = await client.get(f"{settings.API_V1_STR}/roles?name={unique_name}", headers=normal_user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert any(r["name"] == unique_name for r in data["data"])

    # test search keyword (multi-field)
    keyword = unique_name.split("_")[0]  # ambil "superadmin"
    resp = await client.get(f"{settings.API_V1_STR}/roles?search={keyword}", headers=normal_user_token_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert any(keyword in r["name"].lower() or keyword in (r["description"] or "").lower() for r in data["data"])

@pytest.mark.asyncio
async def test_delete_role(client: AsyncClient, normal_user_token_headers: dict[str, str]):
    # generate satu role dengan keyword unik
    unique_name = random_lower_string()
    role_data = {
        "name": unique_name,
        "description": faker.sentence(),
    }

    resp = await client.post(f"{settings.API_V1_STR}/roles", json=role_data, headers=normal_user_token_headers)
    assert resp.status_code == 201

    json_data = resp.json()

    id = json_data["id"]

    
    resp = await client.delete(f"{settings.API_V1_STR}/roles/{id}", headers=normal_user_token_headers)
    assert resp.status_code == 204

    #422
    resp = await client.delete(f"{settings.API_V1_STR}/roles/abc", headers=normal_user_token_headers)
    assert resp.status_code == 422

    print(id)


    resp = await client.get(f"{settings.API_V1_STR}/roles/{id}", headers=normal_user_token_headers)
    assert resp.status_code == 404
   
@pytest.mark.asyncio
async def test_update_role(client: AsyncClient, normal_user_token_headers: dict[str, str]):
    # generate satu role dengan keyword unik
    unique_name = random_lower_string()
    role_data = {
        "name": unique_name,
        "description": faker.sentence(),
    }

    resp= await client.post(f"{settings.API_V1_STR}/roles", json=role_data, headers=normal_user_token_headers)
    json_data = resp.json()

    resp = await client.get(f"{settings.API_V1_STR}/roles/{json_data['id']}", headers=normal_user_token_headers)
    assert 200 == resp.status_code
    
    json_data = resp.json()
    id = json_data["id"]

    name = faker.word()
    payload = {
            "name": name,
            "description": faker.sentence(),
            "permission": {
                "user": {
                    "can_create_user": False,
                    "can_delete_user": True,
                    "can_update_user": False,
                    "can_view_user": False
                },
                "role": {
                    "can_create_role": False,
                    "can_delete_role": True,
                    "can_update_role": True,
                    "can_view_role": False
                }
            }
        }

    resp = await client.put(f"{settings.API_V1_STR}/roles/{id}", headers=normal_user_token_headers, json=payload)
    assert resp
    json_data = resp.json()

    assert resp.status_code == 200
    assert json.dumps(json_data["permission"], sort_keys=True) == json.dumps(payload["permission"], sort_keys=True)


