
from datetime import datetime
import uuid
from sqlalchemy import DateTime

from sqlmodel import Field, Relationship, SQLModel
from .user import User, get_datetime_utc


class ProjectBase(SQLModel):
    name: str = Field(unique=True, min_length=10, max_length=255)
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

__all__ = ["ProjectBase", "Project"]