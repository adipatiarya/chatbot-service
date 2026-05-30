from typing import TYPE_CHECKING, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from sqlalchemy import DateTime

from sqlmodel import  Field, Relationship, SQLModel as Base

from app.utils import get_datetime_utc
from app.models.user_role import UserRole
from app.models.role_permision import RolePermission

if TYPE_CHECKING:
    from .user import User
    from .permission import Permission

class RoleBase(Base):
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class Role(RoleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
     # relasi ke user melalui tabel penghubung
    users: list["User"] = Relationship(
        back_populates="roles", link_model=UserRole
    )
    # relasi ke permissions melalui tabel penghubung
    permissions: list["Permission"] = Relationship(
        back_populates="roles", link_model=RolePermission
    )
    
# API schemas (BaseModel)
class RoleCreate(BaseModel):
    name: str
    description: str | None = None
    permission_strs: list[str] = Field(default_factory=list)

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=128)
    description: Optional[str] = None
    permission_strs: list[str] = Field(default_factory=list)

class  RolePublic(BaseModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    users: list[str] = []
    permissions: list[str] = []
    total_user: int = 0
    total_permission: int = 0

    