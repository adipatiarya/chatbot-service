import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime
from pydantic import EmailStr
from sqlmodel import SQLModel, Field

def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
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
# atribut untuk dikirim via api creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)

class Token(SQLModel):
    access_token: str
    token_type: str = 'bearer'
    

class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None

class TokenPayload(SQLModel):
    sub: str | None = None


class Message(SQLModel):
    message: str