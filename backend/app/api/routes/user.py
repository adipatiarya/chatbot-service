from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import  CurrentUser, SessionDep, get_current_user_superadmin

from fastapi import Request, Path

from app.utils import logger
from app.models import UserCreate, UserPublic
from backend.app import crud

router = APIRouter(prefix="/users", tags=["User"])



@router.get("/me")
def users_me(current_user: CurrentUser) -> None:
    return current_user

def may_depend():
    return 'xx'

async def test_depend(req: Request):
    js = await req.json()
    print(f"HASILNYA {js}")

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
    
    