from sqlmodel import Session

from app.utils import logger
from fastapi.testclient import TestClient
from app.core.config import settings
from app import crud

def test_create_project(client: TestClient, normal_user_token_headers: dict[str, str], sess: Session, superuser_token_headers: dict[str, str]) -> None:
    
    #data to test EMAIL_TEST_USER membuat project
    data = {"name":"project1", "description":"project one"}

    response = client.post(f"{settings.API_V1_STR}/projects", headers= normal_user_token_headers, json=data)
    assert 201 == response.status_code

    project = response.json()

    assert project
    
    assert project["name"] == data["name"]
    assert project["description"] == data["description"]
    assert "owner_id" in project
    assert "created_by" in project
    assert "created_at" in project
    assert project["created_by"] == settings.EMAIL_TEST_USER

    
    user = crud.get_user_by_email(session=sess, email=settings.EMAIL_TEST_USER)

    r = client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=superuser_token_headers)

    data = r.json()
    assert "projects" in data
    assert 1 == len(data['projects'])
   




