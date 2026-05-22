from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import  SessionDep, get_current_user_superadmin
from app.models import UserCreate, UserPublic
from app import crud

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", dependencies=[Depends(get_current_user_superadmin)], response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> None:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the systems."
        )
    user = crud.create_user(session=session, user_create=user_in)
    return user
    
    