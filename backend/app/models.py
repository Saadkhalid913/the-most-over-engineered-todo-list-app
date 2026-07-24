from uuid import UUID

from pydantic import BaseModel, Field


class Todo(BaseModel):
    id: UUID
    text: str
    done: bool


class TodoCreate(BaseModel):
    text: str = Field(min_length=1)


class TodoUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    done: bool | None = None


class UserPublic(BaseModel):
    id: UUID
    username: str


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
