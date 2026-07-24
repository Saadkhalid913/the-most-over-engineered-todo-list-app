from collections.abc import Generator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Todo, TodoCreate, TodoUpdate
from app.repositories.todo_repository import TodoRepository
from app.todo_service import TodoNotFoundError, TodoService

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_todo_service(session: Annotated[Session, Depends(get_db)]) -> TodoService:
    return TodoService(TodoRepository(session))


TodoServiceDep = Annotated[TodoService, Depends(get_todo_service)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos", response_model=list[Todo])
def list_todos(todo_service: TodoServiceDep) -> list[Todo]:
    return todo_service.list_todos()


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: UUID, todo_service: TodoServiceDep) -> Todo:
    try:
        return todo_service.get_todo(todo_id)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate, todo_service: TodoServiceDep) -> Todo:
    return todo_service.create_todo(body.text)


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: UUID,
    body: TodoUpdate,
    todo_service: TodoServiceDep,
) -> Todo:
    try:
        return todo_service.update_todo(
            todo_id,
            body.model_dump(exclude_unset=True),
        )
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: UUID, todo_service: TodoServiceDep) -> None:
    try:
        todo_service.delete_todo(todo_id)
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None
