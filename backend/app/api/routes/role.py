import uuid

from fastapi import APIRouter
from typing import Any
from app.api.deps import CurrentUser, SessionDep, get_role_service

from app.models.role import RoleCreate, RoleUpdate
from app.api.dtos.role_dto import RolePermissionDto, RolePermissionDetail
from app.utils import all_perms, apply_permissions, extract_true_permissions

router = APIRouter(tags=["Authentication"], prefix="/roles")

@router.post("", response_model=RolePermissionDetail, status_code=201)
async def create_role(sess: SessionDep, currentUser: CurrentUser, data: RolePermissionDto):

    service = get_role_service(sess)

    role_in = RoleCreate(
        name=data.name,
        permission=extract_true_permissions(data.permission)
    )

    resp = await service.create_role(role_in)

    respon_db = [perm.name for perm in resp.permissions]

    updated_perms = apply_permissions(all_perms(), respon_db)

    role = RolePermissionDetail(
        id=resp.id,                  # server generate
        created_at=resp.created_at,     # server generate
        name=resp.name,
        description=resp.description,
        permission=updated_perms
    )
    return role 

@router.put("/{role_id}")
async def update_role(role_id: uuid.UUID, data: RoleUpdate):
    # Simulasi update ke DB
    return data