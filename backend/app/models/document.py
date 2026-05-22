import uuid
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column,Text, DateTime
from pgvector.sqlalchemy import Vector
from typing import Optional
from .project import Project

from app.utils import get_datetime_utc

class DocumentBase(SQLModel):
    content: str = Field(sa_column=Column(Text)) 
    embedding: Optional[list[float]] = Field(
        default=None,
        sa_column=Column(Vector(768), nullable=True)
    )

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    content: str = Field(sa_column=Column(Text)) 

class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(
        foreign_key="project.id", nullable=False, ondelete="CASCADE"
    )
    project: Project | None = Relationship(back_populates="documents")
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    deleted_at: datetime | None = None


__all__ = ["DocumentBase","DocumentCreate","DocumentUpdate","Document"]