from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.auth.deps import AuthServiceDep, CurrentUserDep, get_db
from app.auth.service import InvalidCredentialsError, UsernameTakenError
from app.models import (
    Todo,
    TodoCreate,
    TodoUpdate,
    TokenResponse,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.repositories.todo_repository import TodoRepository
from app.todo_service import TodoNotFoundError, TodoService

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_todo_service(session: Annotated[Session, Depends(get_db)]) -> TodoService:
    return TodoService(TodoRepository(session))


TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/register", response_model=TokenResponse, status_code=201)
def register(body: UserRegister, auth_service: AuthServiceDep) -> TokenResponse:
    try:
        return auth_service.register(body.username, body.password)
    except UsernameTakenError:
        raise HTTPException(status_code=409, detail="Username already taken") from None


@app.post("/auth/login", response_model=TokenResponse)
def login(body: UserLogin, auth_service: AuthServiceDep) -> TokenResponse:
    try:
        return auth_service.login(body.username, body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        ) from None


@app.get("/auth/me", response_model=UserPublic)
def me(current_user: CurrentUserDep) -> UserPublic:
    return current_user


@app.get("/todos", response_model=list[Todo])
def list_todos(
    todo_service: TodoServiceDep,
    current_user: CurrentUserDep,
) -> list[Todo]:
    return todo_service.list_todos(current_user.id)


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(
    todo_id: UUID,
    todo_service: TodoServiceDep,
    current_user: CurrentUserDep,
) -> Todo:
    try:
        return todo_service.get_todo(todo_id, current_user.id)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(
    body: TodoCreate,
    todo_service: TodoServiceDep,
    current_user: CurrentUserDep,
) -> Todo:
    return todo_service.create_todo(body.text, current_user.id)


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: UUID,
    body: TodoUpdate,
    todo_service: TodoServiceDep,
    current_user: CurrentUserDep,
) -> Todo:
    try:
        return todo_service.update_todo(
            todo_id,
            current_user.id,
            body.model_dump(exclude_unset=True),
        )
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(
    todo_id: UUID,
    todo_service: TodoServiceDep,
    current_user: CurrentUserDep,
) -> None:
    try:
        todo_service.delete_todo(todo_id, current_user.id)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None
