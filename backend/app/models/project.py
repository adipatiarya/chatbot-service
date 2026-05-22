
from datetime import datetime
import uuid
from sqlalchemy import DateTime

from sqlmodel import Field, Relationship, SQLModel

from app.utils import get_datetime_utc
from .user import User



class ProjectBase(SQLModel):
    name: str = Field(unique=True, min_length=5, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="projects")

class ProjectCreate(ProjectBase):
    pass

class ProjectPublic(ProjectBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    created_by: str

class ProjectPublics(SQLModel):
    data: list[ProjectPublic]
    count: int

__all__ = ["ProjectBase", "Project", "ProjectCreate", "ProjectPublic"]