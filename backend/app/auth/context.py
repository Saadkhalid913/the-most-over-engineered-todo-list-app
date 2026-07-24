from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    VIEWER = "viewer"
    EDITOR = "editor"


ORG_HEADER = "X-Organization-Id"


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """Who the actor is and what access they have in the active tenant."""

    user_id: UUID | None = None
    username: str | None = None
    organization_id: UUID | None = None
    role: Role | None = None
    authenticated: bool = False

    @classmethod
    def anonymous(cls) -> "AuthorizationContext":
        return cls()

    @property
    def is_authenticated(self) -> bool:
        return self.authenticated and self.user_id is not None

    @property
    def has_organization(self) -> bool:
        return self.organization_id is not None and self.role is not None
