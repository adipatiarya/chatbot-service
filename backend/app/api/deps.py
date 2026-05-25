import jwt

from collections.abc import Generator
from typing import Annotated, List
from sqlmodel import Session

from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer

from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError

from app.core.db import engine
from app.core.config import settings
from app.models.user import User
from app.core import security
from app.generic import TokenPayload, UserPermission

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as sess:
        yield sess

        
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)



SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
token: str = Depends(reusable_oauth2)

def get_current_user(sess: SessionDep, token: TokenDep):
   
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)

    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='could not credential'
        )
    
    user = sess.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail='User not eksis')
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    
    return user
   


CurrentUser = Annotated[User, Depends(get_current_user)]


def authorize(*, permissions:List[UserPermission]) -> bool:
     def dependency(curren_user: CurrentUser):
         
         """"
          jika super user permission tidak berlaku
          default aktive semua
         """
         if curren_user.is_superuser:
             return curren_user
         """
         baru test. jangan lupa ini harus ambil dari object user asli
         required = current_user.permissions
         """
         user_permissi_dummy = [
             UserPermission.USER_CREATE,
             UserPermission.USER_READ,
             UserPermission.USER_UPDATE, 
             UserPermission.USER_DELETE,
          ] #jangan lupa di ganti

         if not any(perm in  user_permissi_dummy for perm in permissions):
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing one of required permissions: {permissions}"
            )
         
         return curren_user
     return dependency


def get_current_user_superadmin(current_user: CurrentUser):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='The user doesn\'t have enough privileges')
    return current_user