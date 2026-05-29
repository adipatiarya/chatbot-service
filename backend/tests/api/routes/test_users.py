from datetime import datetime, timedelta
import random, pytest, json
import uuid

from httpx import AsyncClient
import pytest_asyncio
from app.core.config import settings
from backend.app.utils import extract_all_permissions
from tests.helpers.util import random_email, random_lower_string
from faker import Faker

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

fak = Faker()
keyword:str = None

@pytest_asyncio.fixture(scope="function")
async def test_bulk_users_insert(client: AsyncClient , superuser_token_headers: dict[str, str]) -> None:

    """ CREATE ROLE BLOCK """
    role_names = ["teacher", "student", "moderator", "guest"]
    roles_payload = []
    
    for role_name in role_names:
        perm = random.sample(extract_all_permissions(),k=random.randint(2, len(extract_all_permissions())))
        categories = {p.split("_")[2] for p in perm}
        
        actions = ["create", "view", "update", "delete"]

        # bangun permission dict
        permission_dict = {
            category: {
                f"can_{action}_{category}": f"can_{action}_{category}" in perm
                for action in actions
            }
            for category in categories
        }

         # susun payload sesuai API
        payload = {
            "name": role_name.lower(),
            "description": f"Auto-generated role {role_name}",
            "permission": permission_dict
        }
        roles_payload.append(payload)
    
    #print(json.dumps(roles_payload, indent=4))

    for rp in roles_payload:
        r = await client.post(f"{settings.API_V1_STR}/roles", headers=superuser_token_headers, json=rp)
        assert r.status_code == 201

    """ END CREATE ROLE  BLOCK """

    """ CREATE USER BLOCK """
    users_payload = []
    

    for _ in range(1, 21):
        email = fak.email()
        full_name = keyword = fak.name()
        password = random_lower_string()
        role = random.choice(role_names)
        payload = {
            'email': email,
            'full_name': full_name,
            'password': password,
            'role': role
        }
        users_payload.append(payload)
    
    #print(json.dumps(users_payload, indent=4))

    #create user
    for usr in users_payload:
        r = await client.post(f"{settings.API_V1_STR}/users", headers=superuser_token_headers, json=usr)
        assert 201 == r.status_code

    """ END CREATE USER BLOCK """

@pytest.mark.asyncio
async def test_filter_cek_total(client: AsyncClient , superuser_token_headers: dict[str, str], test_bulk_users_insert):
    
    """test filter"""
    test_limit = 5
    r = await client.get(f"{settings.API_V1_STR}/users?page=1&limit={test_limit}", headers=superuser_token_headers)
    assert 200 == r.status_code
    resp = r.json()

    required_keys = ["data", "total"]
    assert all(key in resp for key in required_keys), "Missing required keys"
    assert isinstance(resp['data'], list)
    assert isinstance(resp['total'], int)
    assert len(resp['data']) == test_limit
   

    for user in resp['data']:
        # assert semua key ada
        required_keys = ["id", "email", "full_name","is_superuser","is_active","role", "permissions"]
        assert all(key in user for key in required_keys), "Missing required keys"
        # cek tipe value
        assert isinstance(user["id"], str), "id must be uid"
        assert isinstance(user["email"], str), "email must be string"
        assert isinstance(user["is_superuser"], bool), "is_superuser must be bool"
        assert isinstance(user["is_active"], bool), "is_active must be bool"
        assert isinstance(user["role"], str), "role must be string"
        assert isinstance(user["permissions"], list), "permissions must be list"
        assert len(user["permissions"]) == len(set(user["permissions"])), "permissions must be unique"

@pytest.mark.asyncio
async def test_filter(client: AsyncClient , superuser_token_headers: dict[str, str], test_bulk_users_insert):
    
    """test filter"""
    test_limit = 5
    r = await client.get(f"{settings.API_V1_STR}/users?page=1&limit={test_limit}", headers=superuser_token_headers)
    assert 200 == r.status_code
    resp = r.json()

    required_keys = ["data", "total"]
    assert all(key in resp for key in required_keys), "Missing required keys"
    assert isinstance(resp['data'], list)
    assert isinstance(resp['total'], int)
    assert len(resp['data']) == test_limit
   

    for user in resp['data']:
        # assert semua key ada
        required_keys = ["id", "email", "full_name","is_superuser","is_active","role", "permissions"]
        assert all(key in user for key in required_keys), "Missing required keys"
        # cek tipe value
        assert isinstance(user["id"], str), "id must be uid"
        assert isinstance(user["email"], str), "email must be string"
        assert isinstance(user["is_superuser"], bool), "is_superuser must be bool"
        assert isinstance(user["is_active"], bool), "is_active must be bool"
        assert isinstance(user["role"], str), "role must be string"
        assert isinstance(user["permissions"], list), "permissions must be list"
        assert len(user["permissions"]) == len(set(user["permissions"])), "permissions must be unique"
    

    limit = 3
    r = await client.get(f"{settings.API_V1_STR}/users?page=1&limit={limit}", headers=superuser_token_headers)
    assert r.status_code == 200
    resp = r.json()
    assert len(resp["data"]) <= limit
    assert resp["total"] >= len(resp["data"])
    total_pages = (resp["total"] // limit) + (1 if resp["total"] % limit else 0)
    assert resp["total_pages"] == total_pages

    #test sort
    r = await client.get(f"{settings.API_V1_STR}/users?order_by=full_name&order_dir=asc", headers=superuser_token_headers)
    assert r.status_code == 200
    resp = r.json()
    names = [u["full_name"].lower() for u in resp["data"]]
    assert names == sorted(names)

    start = (datetime.utcnow() - timedelta(days=30)).isoformat()
    end = datetime.utcnow().isoformat()
    r = await client.get(f"{settings.API_V1_STR}/users?start_date={start}&end_date={end}", headers=superuser_token_headers)
    assert r.status_code == 200
    resp = r.json()
    for user in resp["data"]:
        created_at = datetime.fromisoformat(user["created_at"])
        assert start <= created_at.isoformat() <= end

  





