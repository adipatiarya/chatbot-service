from tests.helpers.util import random_email, random_lower_string
from app.models import UserCreate
from sqlmodel import Session
from app import crud


def test_create_user(sess: Session):
    email = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=email, password=password)
    user = crud.create_user(session=sess, user_create=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")
    