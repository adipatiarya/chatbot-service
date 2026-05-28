from typing import TYPE_CHECKING, List, Any, Optional
import uuid
from datetime import datetime
from sqlalchemy import DateTime
from pydantic import BaseModel, EmailStr, computed_field
from sqlmodel import  Field, Relationship

from sqlmodel import  Field, Relationship, SQLModel as Base
from app.utils import get_datetime_utc
from app.models.user_role import UserRole

if TYPE_CHECKING:
    from .role import Role
    
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
    roles: list["Role"] = Relationship(
        back_populates="users", link_model=UserRole
    )
    
# atribut untuk dikirim via api creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(min_length=2, max_length=128)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, min_length=2, max_length=128)

class  UserPublic(BaseModel):
    id: uuid.UUID
    email: EmailStr
    is_superuser: bool = False 
    full_name: str | None = None
    role: str | None = None
    permissions: list[str] = []
