from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

#from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import User
#from tests.utils.user import authentication_token_from_email
#from tests.utils.user import get_superuser_token_headers

#TEST MODE

@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        session.exec(delete(User))
        session.commit()

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c

@pytest.fixture()
def superuser_token_headers():
    pass

@pytest.fixture()
def normal_user_token_headers():
    pass