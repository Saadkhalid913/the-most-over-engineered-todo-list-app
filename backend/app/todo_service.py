from uuid import UUID, uuid4

from app.models import Todo


class TodoNotFoundError(Exception):
    """Raised when a todo id is not present in the store."""


class TodoService:
    """In-memory create/read/update/delete for todos."""

    def __init__(self) -> None:
        self._todos: dict[UUID, Todo] = {}

    def list_todos(self) -> list[Todo]:
        return list(self._todos.values())

    def get_todo(self, todo_id: UUID) -> Todo:
        todo = self._todos.get(todo_id)
        if todo is None:
            raise TodoNotFoundError(todo_id)
        return todo

    def create_todo(self, text: str) -> Todo:
        todo = Todo(id=uuid4(), text=text, done=False)
        self._todos[todo.id] = todo
        return todo

    def update_todo(self, todo_id: UUID, updates: dict[str, object]) -> Todo:
        todo = self.get_todo(todo_id)
        if not updates:
            return todo

        updated = todo.model_copy(update=updates)
        self._todos[todo_id] = updated
        return updated

    def delete_todo(self, todo_id: UUID) -> None:
        if todo_id not in self._todos:
            raise TodoNotFoundError(todo_id)
        del self._todos[todo_id]
