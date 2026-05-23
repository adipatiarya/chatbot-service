import uuid
from datetime import datetime
from sqlalchemy import DateTime
from pydantic import EmailStr, computed_field
from sqlmodel import Relationship, SQLModel, Field

from typing import TYPE_CHECKING, Optional

from app.utils import get_datetime_utc

if TYPE_CHECKING:
    from .project import Project


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    
# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
 
    projects: list["Project"] = Relationship(back_populates="owner", cascade_delete=True)

    owner_id: Optional[uuid.UUID ] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(
        sa_relationship_kwargs={"remote_side": "User.id"},
    )
    
# atribut untuk dikirim via api creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    owner_id: uuid.UUID | None = None
    owner: Optional["User"] = None
    projects: list["Project"] = Field(default_factory=list)

    @computed_field
    @property
    def created_by(self) -> str | None:
        return self.owner.email if self.owner else None
    

__all__ = ["UserBase", "User", "UserCreate", "UserUpdate", "UserPublic"]