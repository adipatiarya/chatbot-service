import jwt

from typing import Annotated, List
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer

from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError

from app.core.db import engine
from app.core.config import settings
from app.models.user import User
from app.generic import TokenPayload, UserPermission

from app.repositories.cruds.role_crud import RoleCrud
from app.repositories.cruds.user_crud import UserCrud
from app.repositories.cruds.permission_crud import PermissionCrud

from app.services.user_service import UserService
from app.services.role_service import RoleService

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)



SessionDep = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
token: str = Depends(reusable_oauth2)

def get_user_service(session: AsyncSession) -> UserService:
    user_repo = UserCrud(session)
    role_repo = RoleCrud(session)
    return UserService(user_repo, role_repo)

def get_role_service(session: AsyncSession) -> RoleService:
    role_repo = RoleCrud(session)
    permission_repo = PermissionCrud(session)
    return RoleService(role_repo, permission_repo)

async def get_current_user(sess: SessionDep, token: TokenDep):
   
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)

    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='could not credential'
        )
    service = get_user_service(sess)

    user = await service.user_crud.roles(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail='User not eksis')
    if not user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return service.populate_user(user)
   


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_user_superadmin(current_user: CurrentUser):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail='The user doesn\'t have enough privileges')
    return current_user


def require_permissions(required: List[str]):
    def dependency(current_user:CurrentUser):
        # pengecualian: kalau superuser, langsung lolos
        if current_user.is_superuser:
            return current_user
        
        user_permissions = current_user.permissions
        if not all(perm in user_permissions for perm in required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    return dependency
