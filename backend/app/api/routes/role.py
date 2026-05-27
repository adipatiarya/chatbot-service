import uuid

from fastapi import APIRouter
from typing import Any
from app.api.deps import CurrentUser, SessionDep, get_role_service
from app.models.role import RoleCreate, RoleUpdate

router = APIRouter(tags=["Authentication"], prefix="/roles")

from typing import Dict
from pydantic import BaseModel
from datetime import datetime

def all_perms() -> Dict[str, Dict[str, bool]]:
    actions = ["create", "view", "update", "delete"]
    resources = ["user", "role"]
    return {
        resource: {f"can_{action}_{resource}": False for action in actions}
        for resource in resources
    }

def apply_permissions(base: Dict[str, Dict[str, bool]], allowed: list[str]) -> Dict[str, Dict[str, bool]]:
    for _, perms in base.items():
        for perm_name in perms.keys():
            if perm_name in allowed:
                perms[perm_name] = True
    return base

class RolePermissionCreate(BaseModel):
    name: str
    description: Any | None = None
    permission: Dict[str, Dict[str, bool]] = all_perms()

class RolePermissionDetail(BaseModel):
    id: uuid.UUID
    created_at: datetime
    name: str
    description: Any | None = None
    permission: Dict[str, Dict[str, bool]] = all_perms()


def extract_true_permissions(permission_dict: dict[str, dict[str, bool]]) -> list[str]:
    result = []
    for _, perms in permission_dict.items():
        for perm_name, value in perms.items():
            if value:  # hanya ambil yang True
                result.append(perm_name)
    return result

@router.post("", response_model=RolePermissionDetail)
async def create_role(sess: SessionDep, data: RolePermissionCreate):

    datax = extract_true_permissions(data.permission)
    
    service = get_role_service(sess)

    role_in = RoleCreate(
        name=data.name,
        permission=datax
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