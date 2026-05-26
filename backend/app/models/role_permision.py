from sqlmodel import SQLModel, Field
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

class RolePermission(SQLModel, table=True):
    role_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True
        )
    )
    permission_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True), ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True
        )
    )

