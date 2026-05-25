import uuid

from sqlmodel import Field

from app.models import Base

class UserRole(Base, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True
    )
    role_id: uuid.UUID = Field(
        foreign_key="role.id", primary_key=True
    )