from uuid import UUID

from app.auth.context import AuthorizationContext
from app.auth.gated import AuthGatedService
from app.models import Todo
from app.todo_service import TodoService


class TodoScopedService(AuthGatedService):
    """Authorization-scoped facade over TodoService."""

    def __init__(self, auth: AuthorizationContext, todos: TodoService) -> None:
        super().__init__(auth)
        self._todos = todos

    def list_todos(self) -> list[Todo]:
        self.require_viewer()
        return self._todos.list_todos(self.organization_id)

    def get_todo(self, todo_id: UUID) -> Todo:
        self.require_viewer()
        return self._todos.get_todo(todo_id, self.organization_id)

    def create_todo(self, text: str) -> Todo:
        self.require_editor()
        return self._todos.create_todo(
            text=text,
            organization_id=self.organization_id,
            user_id=self.actor_id,
        )

    def update_todo(self, todo_id: UUID, updates: dict[str, object]) -> Todo:
        self.require_editor()
        return self._todos.update_todo(todo_id, self.organization_id, updates)

    def delete_todo(self, todo_id: UUID) -> None:
        self.require_editor()
        self._todos.delete_todo(todo_id, self.organization_id)
