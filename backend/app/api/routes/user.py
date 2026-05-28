from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
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
        raise HTTPException(status_code=400, detail='Terjadi kesalahan')
    
    user =  await service.create_user(user_in)
    return service.populate_user(user)



    
