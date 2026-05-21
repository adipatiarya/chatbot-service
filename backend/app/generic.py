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