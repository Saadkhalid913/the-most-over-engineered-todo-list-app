from uuid import UUID

from app.models import Todo
from app.repositories.todo_repository import TodoRepository


class TodoNotFoundError(Exception):
    """Raised when a todo id is not present in the store."""


class TodoService:
    """Domain operations for todos; persistence is delegated to a repository."""

    def __init__(self, repository: TodoRepository) -> None:
        self._repository = repository

    def list_todos(self) -> list[Todo]:
        return self._repository.list_todos()

    def get_todo(self, todo_id: UUID) -> Todo:
        todo = self._repository.get_todo(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    def create_todo(self, text: str) -> Todo:
        return self._repository.create_todo(text)

    def update_todo(self, todo_id: UUID, updates: dict[str, object]) -> Todo:
        todo = self._repository.update_todo(todo_id, updates)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    def delete_todo(self, todo_id: UUID) -> None:
        if not self._repository.delete_todo(todo_id):
            raise TodoNotFoundError(todo_id)
