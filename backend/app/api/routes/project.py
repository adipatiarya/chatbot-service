from typing import Any
from fastapi import APIRouter, status

from app.api.deps import  CurrentUser, SessionDep
from app.models.project import ProjectCreate, ProjectPublic, Project

from app.repo.embeded.embed import get_embedding

router = APIRouter(prefix="/projects", tags=["Project"])


@router.post("/", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
def create_project(*, sess:SessionDep, current_user:CurrentUser, project_in:ProjectCreate) -> Any:
    """
     Create Project
    """
    project = Project.model_validate(project_in, update={"owner_id": current_user.id})
    sess.add(project)
    sess.commit()
    sess.refresh(project)
    return ProjectPublic(**project.model_dump(), created_by=project.owner.email)

 