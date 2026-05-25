from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm


from app import crud
from app.models.user import UserPublic, UserUpdate
from app.generic import Token, Message, NewPassword

from app.api.deps import SessionDep, CurrentUser
from app.core.config import settings
from app.core.security import create_access_token
from app.utils import (
    generate_password_reset_token, 
    generate_reset_password_email,
    verify_password_reset_token,
)
from app.repo.email import send_email

router = APIRouter(tags=["Authentication"], prefix="/auth")

@router.get("/me")
def users_me(current_user: CurrentUser) -> None:
    return current_user

@router.post("/access-token")
def login_access_token(sess:SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:

    user = crud.authenticate(session=sess, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect email and password')
    elif not user.is_active:
        raise HTTPException(status_code=400, detail='User inactive')
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return Token(
        access_token=create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
    )

@router.post("/password-recovery/{email}")
def password_recovery(email: str, sess: SessionDep)-> Message:
    
    user = crud.get_user_by_email(session=sess, email=email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content
        )

    return Message(message="If that email is registered, we sent a password recovery link")

@router.post("/test-token", response_model=UserPublic)
def login_test_token(current_user: CurrentUser):
    return current_user

@router.post("/reset-password")
def reset_password(sess:SessionDep, body: NewPassword):
   
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=sess, email=email)
    if not user:
        # Jangan di proses jika usernya tidak ada
        raise HTTPException(status_code=400, detail="Invalid token")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user_un_update = UserUpdate(password=body.new_password)

    crud.update_user(
        session=sess,
        db_user=user,
        user_in=user_un_update
    )
    return {
        "message":"Password updated successfully"
    }