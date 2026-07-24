from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


class Todo(BaseModel):
    id: UUID
    text: str
    done: bool


class TodoCreate(BaseModel):
    text: str = Field(min_length=1)


class TodoUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1)
    done: bool | None = None


todos: dict[UUID, Todo] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/todos", response_model=list[Todo])
def list_todos() -> list[Todo]:
    return list(todos.values())


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: UUID) -> Todo:
    todo = todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate) -> Todo:
    todo = Todo(id=uuid4(), text=body.text, done=False)
    todos[todo.id] = todo
    return todo


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: UUID, body: TodoUpdate) -> Todo:
    todo = todos.get(todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        return todo

    updated = todo.model_copy(update=updates)
    todos[todo_id] = updated
    return updated


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: UUID) -> None:
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="Todo not found")
    del todos[todo_id]
