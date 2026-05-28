import uuid

from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep, get_role_service

from app.models.role import RoleCreate
from app.api.dtos.role_dto import RolePermissionDto, RolePermissionDetail
from app.utils import all_perms, apply_permissions, extract_true_permissions

router = APIRouter(tags=["Authentication"], prefix="/roles")

@router.post("", response_model=RolePermissionDetail, status_code=201)
async def create_role(sess: SessionDep, currentUser: CurrentUser, data: RolePermissionDto):

    service = get_role_service(sess)

    role_in = RoleCreate(
        name=data.name,
        permission_strs=extract_true_permissions(data.permission)
    )

    resp = await service.create_role(role_in)

    role = RolePermissionDetail(
        id=resp.id,                  # server generate
        created_at=resp.created_at,     # server generate
        name=resp.name,
        description=resp.description,
        permission= apply_permissions(all_perms(), [perm.name for perm in resp.permissions] )
    )
    return role 

@router.get("/{role_id}", response_model=RolePermissionDetail)
async def  get_role(sess: SessionDep, role_id: uuid.UUID):
    # Simulasi update ke DB
    service = get_role_service(sess)

    resp = await service.role_crud.get_by_name_or_id(role_id)
 
    role = RolePermissionDetail(
        id=resp.id,                  # server generate
        created_at=resp.created_at,     # server generate
        name=resp.name,
        description=resp.description,
        permission = apply_permissions(all_perms(), [perm.name for perm in resp.permissions] )
    )
    return role 
