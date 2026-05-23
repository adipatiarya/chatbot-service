from enum import Enum

from sqlmodel import SQLModel

class TokenPayload(SQLModel):
    sub: str | None = None


class Message(SQLModel):
    message: str

class NewPassword(SQLModel):
    token: str
    new_password: str

class Token(SQLModel):
    access_token: str
    token_type: str = 'bearer'

class UserPermission(str, Enum):
    USER_CREATE = 'user_create'
    USER_READ = 'user_read'
    USER_UPDATE = 'user_update'
    USER_DELETE = 'user_delete'