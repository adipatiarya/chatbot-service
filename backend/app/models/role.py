from typing import TYPE_CHECKING
import uuid
from datetime import datetime
from sqlalchemy import DateTime

from sqlmodel import  Field, Relationship, SQLModel as Base

from app.utils import get_datetime_utc
from app.models.user_role import UserRole

if TYPE_CHECKING:
    from .user import User

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
    
class RoleCreate(RoleBase):
   pass

class RoleUpdate(RoleBase):
   pass
    
class RolePublic(RoleBase):
    id: uuid.UUID
    created_at: datetime | None = None

