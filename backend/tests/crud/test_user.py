from fastapi.encoders import jsonable_encoder
from tests.helpers.util import random_email, random_lower_string
from app.models import UserCreate, User, UserUpdate
from app.core.security import verify_password
from sqlmodel import Session
from app import crud


def test_create_user(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")

def test_authenticate_user(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    authenticate_user = crud.authenticate(session=sess, email=email, password=password)

    assert authenticate_user
    assert user.email == authenticate_user.email

def test_not_authenticate_user(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud.authenticate(session=sess, email=email, password=password)
    assert user is None

def test_check_user_is_active_inactive(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_active=False)
    user = crud.create_user(session=sess, user_create=user_in)
    assert user.is_active is False

def test_check_user_is_superuser(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password, is_superuser=True)
    user = crud.create_user(session=sess, user_create=user_in)
    assert user.is_superuser is True

def test_check_user_is_normal_user(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    assert user.is_superuser is False

def test_get_user(sess: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    user_2 = sess.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)

def test_update_user(sess: Session) -> None :
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    new_password = random_lower_string()
    user_in_update = UserUpdate(password=new_password, is_superuser=True)
    if user.id is not None:
        crud.update_user(session= sess, db_user=user, user_in=user_in_update)
    user_2 = sess.get(User, user.id)
    assert user_2
    assert user.email == user_2.email
    verified, _ = verify_password(plain_password= new_password, hashed_password=user_2.hashed_password)
    assert verified