import uuid
from datetime import datetime
from sqlalchemy import DateTime
from pydantic import EmailStr
from sqlmodel import  Field, Relationship

from app.models import Base
from app.utils import get_datetime_utc


class UserRoleLink(Base, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True
    )
    role_id: uuid.UUID = Field(
        foreign_key="role.id", primary_key=True
    )
    
    
# Association table untuk user-role

# Shared properties
class RoleBase(Base):
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=255)
# Database model, database table inferred from class name
class Role(RoleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
     # relasi ke user melalui tabel penghubung
    users: list["User"] = Relationship(
        back_populates="roles", link_model=UserRoleLink
    )
    
# atribut untuk dikirim via api creation
class RoleCreate(RoleBase):
   pass

class RoleUpdate(RoleBase):
   pass
    
class RolePublic(RoleBase):
    id: uuid.UUID
    created_at: datetime | None = None



# Shared properties
class UserBase(Base):
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
     # relasi ke role melalui tabel penghubung
    roles: list[Role] = Relationship(
        back_populates="users", link_model=UserRoleLink
    )
    
# atribut untuk dikirim via api creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role_id: uuid.UUID

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None
    
