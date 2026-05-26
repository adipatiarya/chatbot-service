import uuid

from sqlmodel import Field

from sqlmodel import  Field, Relationship, SQLModel as Base

class UserRole(Base, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True
    )
    role_id: uuid.UUID = Field(
        foreign_key="role.id", primary_key=True
    )