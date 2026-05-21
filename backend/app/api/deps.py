import jwt

from collections.abc import Generator
from typing import Annotated
from sqlmodel import Session

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException,status

from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError

from app.core.db import engine
from app.core.config import settings
from app.models import User
from app.core import security
from app.generic import TokenPayload

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


def get_current_user_superadmin(current_user: CurrentUser):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='The user doesn\'t have enough privileges')
    return current_user

