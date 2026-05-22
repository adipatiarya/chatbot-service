from typing import Generator

from fastapi.testclient import TestClient
from contextlib import contextmanager
from sqlmodel import Session

from app.utils import logger
from app.core.config import settings
from app import crud
from tests.helpers.util import random_email, random_lower_string



@contextmanager
def hello(world: str) -> Generator[None,None, None]:
    logger.info(f"Hello {world}")
    yield
    logger.info(f'God bay {world}')



def test_create_user_new_email(client: TestClient, superuser_token_headers: dict[str, str], sess: Session) -> None:

    with (
        hello("world"),
        hello("budy"),
        hello("cici")
    ):
     username = random_email()
     password = random_lower_string()

     data = {"email":username, "password":password}

     r = client.post(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers, json=data)
     assert 200 <= r.status_code < 300
     created_user = r.json()
     logger.info(created_user)
     user = crud.get_user_by_email(session=sess, email=username)
     assert user
     assert user.email == created_user["email"]
     

def test_get_existing_user_as_superuser() -> None:

    pass

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

def test_create_user_by_normal_user() -> None:
    pass

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