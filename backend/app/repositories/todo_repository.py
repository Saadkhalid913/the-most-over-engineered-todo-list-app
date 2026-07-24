from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TodoRow
from app.models import Todo


class TodoRepository:
    """SQLAlchemy-backed persistence for todos scoped to a user."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_todos(self, user_id: UUID) -> list[Todo]:
        rows = self._session.scalars(
            select(TodoRow).where(TodoRow.user_id == str(user_id))
        ).all()
        return [self._to_todo(row) for row in rows]

    def get_todo(self, todo_id: UUID, user_id: UUID) -> Todo | None:
        row = self._session.get(TodoRow, str(todo_id))
        if row is None or row.user_id != str(user_id):
            return None
        return self._to_todo(row)

    def create_todo(self, text: str, user_id: UUID) -> Todo:
        row = TodoRow(id=str(uuid4()), user_id=str(user_id), text=text, done=False)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return self._to_todo(row)

    def update_todo(
        self,
        todo_id: UUID,
        user_id: UUID,
        updates: dict[str, object],
    ) -> Todo | None:
        row = self._session.get(TodoRow, str(todo_id))
        if row is None or row.user_id != str(user_id):
            return None
        if not updates:
            return self._to_todo(row)

        if "text" in updates:
            row.text = str(updates["text"])
        if "done" in updates:
            row.done = bool(updates["done"])

        self._session.commit()
        self._session.refresh(row)
        return self._to_todo(row)

    def delete_todo(self, todo_id: UUID, user_id: UUID) -> bool:
        row = self._session.get(TodoRow, str(todo_id))
        if row is None or row.user_id != str(user_id):
            return False
        self._session.delete(row)
        self._session.commit()
        return True

    @staticmethod
    def _to_todo(row: TodoRow) -> Todo:
        return Todo(id=UUID(row.id), text=row.text, done=row.done)
