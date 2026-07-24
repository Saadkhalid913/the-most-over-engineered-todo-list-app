from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import UserRow
from app.models import UserPublic


class UserRepository:
    """SQLAlchemy-backed persistence for users."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> UserPublic | None:
        row = self._session.get(UserRow, str(user_id))
        if row is None:
            return None
        return self._to_user(row)

    def get_by_username(self, username: str) -> UserRow | None:
        return self._session.scalars(
            select(UserRow).where(UserRow.username == username)
        ).first()

    def create_user(self, username: str, password_hash: str) -> UserPublic:
        row = UserRow(
            id=str(uuid4()),
            username=username,
            password_hash=password_hash,
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return self._to_user(row)

    @staticmethod
    def _to_user(row: UserRow) -> UserPublic:
        return UserPublic(id=UUID(row.id), username=row.username)
