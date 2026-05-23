from fastapi.testclient import TestClient
from sqlmodel import Session

from app.utils import logger
from app.core.config import settings
from app import crud
from app.models import UserCreate

from tests.helpers.util import random_email, random_lower_string


def test_create_user_new_email(client: TestClient, superuser_token_headers: dict[str, str], sess: Session) -> None:

    username = random_email()
    password = random_lower_string()

    data = {"email":username, "password":password}

    r = client.post(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data)
    assert 201 == r.status_code
    created_user = r.json()
    user = crud.get_user_by_email(session=sess, email=username)
 
    assert user
    assert user.email == created_user["email"]
   


def test_get_existing_user_as_superuser(
        client: TestClient, 
        superuser_token_headers: dict[str, str], 
        sess: Session) -> None:
    
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    user_id = user.id
    r = client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=superuser_token_headers)
    
    user = r.json()
    assert user
    assert 200 == r.status_code


def test_get_non_existing_user_as_superuser() -> None:

    pass

def test_get_existing_user_curent_user() -> None:

    pass

def test_get_existing_user_permissions_error() -> None:
    pass

def test_get_non_existing_user_permissions_error() -> None:
    pass

def  test_create_user_existing_username() -> None:
    pass

def test_create_user_by_normal_user(client: TestClient, normal_user_token_headers: dict[str, str]) -> None:
    
    username = random_email()
    password = random_lower_string()

    data = {"email":username, "password":password}

    r = client.post(f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers, json=data)
    assert 201 == r.status_code

def  test_retrieve_users() -> None:
    pass

def test_update_user_me() -> None:
    pass

def test_update_password_me() -> None:
    pass

def test_update_password_me_incorrect_password()-> None:
    pass

def test_update_user_me_email_exists()->None:
    pass

def test_delete_user_me()->None:
    pass

def test_delete_user_me_as_superuser()->None:
    pass

def test_delete_user_super_user()->None:
    pass

def test_delete_user_not_found()->None:
    pass

def test_delete_user_current_super_user_error()->None:
    pass

def  test_delete_user_without_privileges()->None:
    pass