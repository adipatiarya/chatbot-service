import uuid
from datetime import datetime
from sqlalchemy import DateTime

from sqlmodel import  Field, SQLModel as Base

from app.utils import get_datetime_utc

class PermissionBase(Base):
    name: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=255)

class Permission(PermissionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    
class PermissionCreate(PermissionBase):
   pass

class PermissionUpdate(PermissionBase):
   pass
    
class PermissionPublic(PermissionBase):
    id: uuid.UUID
    created_at: datetime | None = None

