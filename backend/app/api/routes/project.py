from typing import Any
from fastapi import APIRouter

from app.api.deps import  CurrentUser, SessionDep
from app.models.project import ProjectCreate, ProjectPublic, Project

from app.repo.embeded.embed import get_embedding

router = APIRouter(prefix="/projects", tags=["Project"])


@router.post("/", response_model=ProjectPublic, status_code=201)
def create_project(*, sess:SessionDep, current_user:CurrentUser, project_in:ProjectCreate) -> Any:
    """
     Create Project
    """
    project = Project.model_validate(project_in, update={"owner_id": current_user.id})
    sess.add(project)
    sess.commit()
    sess.refresh(project)
    return ProjectPublic(**project.model_dump(), created_by=project.owner.email)

@router.get("/embed-test")
def embed_test():
    data = get_embedding("mantap")
    return data  