from fastapi.testclient import TestClient
from app.core.config import settings

def test_create_project(client: TestClient, superuser_token_headers:dict[str,str]) -> None:
    
    #data to test
    data = {"name":"project1", "description":"project one"}
    response = client.post(f"{settings.API_V1_STR}/projects", headers=superuser_token_headers, json=data)
    assert 201 == response.status_code

    project = response.json()
    assert project
    
    assert project["name"] == data["name"]
    assert project["description"] == data["description"]
    assert "owner_id" in project
    assert "created_by" in project
    assert "created_at" in project
    assert project["created_by"] == settings.FIRST_SUPERUSER

