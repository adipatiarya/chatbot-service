from datetime import datetime
from typing import Optional
import uuid
from fastapi import APIRouter, HTTPException, Path, Query, status

from app.api.deps import  CurrentUser, SessionDep, get_user_service
from app.models.user import User, UserCreate, UserPublic
from app.api.dtos.generic import  Paginated

router = APIRouter(prefix="/users", tags=["User"])

@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_user(*, session: SessionDep, user_in: UserCreate, current_user: CurrentUser) -> None:
    """
    Create new user.
    """
    service = get_user_service(session)

    user = await service.user_crud.get_by_email(user_in.email)
    if user:
        raise HTTPException(status_code=400, detail=f'Email {user_in.email} ini sudah digunakan.')
    
    user =  await service.create_user(user_in)
    return service.populate_user(user)


@router.get("/{user_id}", response_model=UserPublic)
async def get_user_id(*, session: SessionDep, user_id: uuid.UUID  = Path(..., description="UUID user")) -> None:
    """
    Create new user.
    """
    service = get_user_service(session)

    user = await service.user_crud.roles(user_id)

    if not user:
        raise HTTPException(status_code=400, detail=f'User id tidak ditemukan')
    
    return service.populate_user(user)
    
@router.get(
    "",
    response_model=Paginated[UserPublic],
    summary="List users with full query options",
    description="Daftar user dengan filter generic, multi-field search, pagination, sorting ASC/DESC, dan filter tanggal created_at."
)
async def list_user(
    sess: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    role: Optional[str] = None,                # <--- tambahan parameter
    permission: Optional[str] = None,          # <--- tambahan parameter
    order_by: str = "created_at",
    order_dir: str = "asc",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    service = get_user_service(sess)


     # siapkan dict filters
    filters = {}
    if role:
        filters["role"] = role
    if permission:
        filters["permission"] = permission

    list_user = await service.user_crud.filtered(
        page=page,
        limit=limit,
        filters=filters,
        search=search,
        order_by=order_by,
        order_dir=order_dir,
        start_date=start_date,
        end_date=end_date,
    )
    return list_user

