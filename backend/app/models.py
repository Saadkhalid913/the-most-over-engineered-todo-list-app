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
