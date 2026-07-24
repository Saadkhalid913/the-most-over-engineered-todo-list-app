from uuid import UUID

from app.models import Todo
from app.repositories.todo_repository import TodoRepository


class TodoNotFoundError(Exception):
    """Raised when a todo id is not present in the given organization."""


class TodoService:
    """Domain operations for todos; persistence is delegated to a repository."""

    def __init__(self, repository: TodoRepository) -> None:
        self._repository = repository

    def list_todos(self, organization_id: UUID) -> list[Todo]:
        return self._repository.list_todos(organization_id)

    def get_todo(self, todo_id: UUID, organization_id: UUID) -> Todo:
        todo = self._repository.get_todo(todo_id, organization_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    def create_todo(
        self,
        *,
        text: str,
        organization_id: UUID,
        user_id: UUID,
    ) -> Todo:
        return self._repository.create_todo(
            text=text,
            organization_id=organization_id,
            user_id=user_id,
        )

    def update_todo(
        self,
        todo_id: UUID,
        organization_id: UUID,
        updates: dict[str, object],
    ) -> Todo:
        todo = self._repository.update_todo(todo_id, organization_id, updates)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    def delete_todo(self, todo_id: UUID, organization_id: UUID) -> None:
        if not self._repository.delete_todo(todo_id, organization_id):
            raise TodoNotFoundError(todo_id)
