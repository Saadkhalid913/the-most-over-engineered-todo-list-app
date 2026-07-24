from uuid import UUID

from pydantic import BaseModel, Field

from app.auth.context import Role


class Todo(BaseModel):
    id: UUID
    text: str
    done: bool
    organization_id: UUID
    user_id: UUID


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


class Organization(BaseModel):
    id: UUID
    name: str


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class OrganizationMembership(BaseModel):
    organization_id: UUID
    organization_name: str
    user_id: UUID
    role: Role


class AddOrganizationMember(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    role: Role = Role.VIEWER
