from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, EmailStr

from app.api.deps import  CurrentUser, SessionDep, get_user_service
from app.models.user import UserCreate, UserPublic

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
    
