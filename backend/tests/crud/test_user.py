from tests.helpers.util import random_email, random_lower_string
from app.models import UserCreate
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
