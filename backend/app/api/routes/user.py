import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import  CurrentUser, SessionDep, authorize
from app.models.user import UserCreate, UserPublic, User
from app import crud
from app.generic import UserPermission

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/", 
             dependencies=[Depends(authorize(permissions=[UserPermission.USER_CREATE]))], 
             response_model=UserPublic,
             status_code=status.HTTP_201_CREATED
             )
def create_user(*, session: SessionDep, user_in: UserCreate, current_user: CurrentUser) -> None:
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

@router.get("/{user_id}", dependencies=[Depends(authorize(permissions=[UserPermission.USER_READ]))], response_model=UserPublic, response_model_exclude={"owner","is_superuser"})
def get_user_by_id(user_id:uuid.UUID, sess: SessionDep):
    """
     Get a specific user by id
    """
    user = sess.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail= "User not exist"
        )
    
    return  user