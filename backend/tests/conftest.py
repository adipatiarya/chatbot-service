from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import User, Project
from tests.helpers.user import authentication_token_from_email
from tests.helpers.util import get_superuser_token_headers

#TEST MODE

@pytest.fixture(scope="session", autouse=True)
def sess() -> Generator[Session, None, None]:
    with Session(engine) as session:
        init_db(session)
        yield session
        session.exec(delete(User))
        session.exec(delete(Project))
        session.commit()

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client=client)

@pytest.fixture()
def normal_user_token_headers(client: TestClient, sess: Session):
    return authentication_token_from_email( 
        client=client, email=settings.EMAIL_TEST_USER, db=sess
    )
    