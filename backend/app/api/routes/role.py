from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Path, Query, status
from app.api.deps import CurrentUser, SessionDep, get_role_service

from app.models.role import RoleCreate, RolePublic, RoleUpdate

from app.api.dtos.generic import DataList

from app.api.dtos.role_dto import RolePermissionDto, RolePermissionDetail
from app.utils import all_perms, apply_permissions, extract_true_permissions

router = APIRouter(tags=["Role Permissions"], prefix="/roles")

@router.post("", 
    response_model=RolePermissionDetail,
    status_code=status.HTTP_201_CREATED,
    description="Membuat role baru dengan daftar permission yang diberikan."
)
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


@router.get(
    "",
    response_model=DataList[RolePublic],
    summary="List roles with full query options",
    description="Daftar role dengan filter generic, multi-field search, pagination, sorting ASC/DESC, dan filter tanggal created_at."
)
async def list_roles(
    sess: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    name: str | None = Query(None, description="Filter by role name"),
    description: str | None = Query(None, description="Filter by role description"),
    search: str | None = Query(None, description="Search keyword in name/description"),
    order_by: str = Query("created_at", description="Kolom untuk sorting"),
    order_dir: str = Query("asc", description="Arah sorting: asc/desc"),
    start_date: datetime | None = Query(None, description="Filter created_at >= start_date"),
    end_date: datetime | None = Query(None, description="Filter created_at <= end_date"),
):
    service = get_role_service(sess)

    # kumpulkan filter spesifik
    filters = {}
    if name:
        filters["name"] = name
    if description:
        filters["description"] = description

    # panggil repository dengan semua parameter
    list_data = await service.role_crud.list_filtered(
        page=page,
        limit=limit,
        filters=filters,
        search=search,
        order_by=order_by,
        order_dir=order_dir,
        start_date=start_date,
        end_date=end_date
    )

    roles = [RolePublic.model_validate(obj) for obj in list_data]

    return DataList[RolePublic](
        count=len(roles),
        data=roles
    )


@router.get("/{role_id}", response_model=RolePermissionDetail,  description="Informasi detail tentang role dan permissionnya")
async def  get_role(sess: SessionDep, role_id: uuid.UUID = Path(..., description="UUID role")):
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

@router.put("/{role_id}",summary="Update role",description="Update data role berdasarkan ID")
async def update_role(sess: SessionDep,  role_id: uuid.UUID = Path(..., description="UUID role")):
    service = get_role_service(sess)
    role = await service.role_crud.get_by_name_or_id(role_id)
    if not role:
         raise HTTPException(status_code=404, detail="Role not found")
    return {
        'ok':'ok'
    }
        

@router.delete("/{role_id}",summary="Delete role",description="Delete data role berdasarkan ID", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(sess: SessionDep,  role_id: uuid.UUID = Path(..., description="UUID role")):
    service = get_role_service(sess)
    role = await service.role_crud.get_by_name_or_id(role_id)
    if not role:
         raise HTTPException(status_code=404, detail="Role not found")
    await service.role_crud.delete(role)