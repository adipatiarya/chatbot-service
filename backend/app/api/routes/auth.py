from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, get_user_service
from app.api.deps import SessionDep
from app.core.config import settings
from app.generic import Message, NewPassword, Token
from app.models.user import UserPublic, UserUpdate
from app.utils import (
    generate_password_reset_token, 
    generate_reset_password_email, 
    verify_password_reset_token
)

from app.services.email_service import EmailService

router = APIRouter(tags=["Authentication"], prefix="/auth")


@router.get("/me", response_model=UserPublic)
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

@router.post("/password-recovery/{email}")
async def password_recovery(email: str, sess: SessionDep)-> Message:
    service = get_user_service(sess)
    user = await service.user_crud.get_by_email(email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
        EmailService(user.email, email_data.subject, email_data.html_content).send()


    return Message(message="If that email is registered, we sent a password recovery link")

@router.post("/reset-password")
async def reset_password(sess:SessionDep, body: NewPassword):
    service = get_user_service(sess)
  
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = await service.user_crud.get_by_email(email)
    
    if not user:
        # Jangan di proses jika usernya tidak ada
        raise HTTPException(status_code=400, detail="Invalid token")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user_un_update = UserUpdate(password=body.new_password)

    await service.update_user(user, user_un_update)
    return {
        "message":"Password updated successfully"
    }