from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, get_user_service
from app.api.deps import SessionDep
from app.core.config import settings
from app.generic import Token
from app.models.user import UserPublic 
router = APIRouter(tags=["Authentication"], prefix="/auth")


@router.get("/me", response_model=UserPublic, response_model_exclude={"roles"})
async def users_me(current_user: CurrentUser) -> None:
    return current_user


@router.post("/access-token")
async def login_access_token(sess: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()])->Token:
    service = get_user_service(sess)
    user = await service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect email and password')
    elif not user.is_active:
        raise HTTPException(status_code=400, detail='User inactive')
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=service.create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
    )
