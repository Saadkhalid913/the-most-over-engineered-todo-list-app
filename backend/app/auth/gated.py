from uuid import UUID

from app.auth.context import ORG_HEADER, AuthorizationContext, Role


class UnauthenticatedError(Exception):
    """Raised when an authenticated actor is required."""


class ForbiddenError(Exception):
    """Raised when the actor lacks the required organization/role."""


class AuthGatedService:
    """Base for scoped services that read the request authorization context."""

    def __init__(self, auth: AuthorizationContext) -> None:
        self._auth = auth

    @property
    def auth(self) -> AuthorizationContext:
        return self._auth

    @property
    def actor_id(self) -> UUID:
        self.require_authenticated()
        assert self._auth.user_id is not None
        return self._auth.user_id

    @property
    def actor_username(self) -> str:
        self.require_authenticated()
        assert self._auth.username is not None
        return self._auth.username

    @property
    def organization_id(self) -> UUID:
        self.require_organization()
        assert self._auth.organization_id is not None
        return self._auth.organization_id

    @property
    def role(self) -> Role:
        self.require_organization()
        assert self._auth.role is not None
        return self._auth.role

    def require_authenticated(self) -> None:
        if not self._auth.is_authenticated:
            raise UnauthenticatedError("Authentication required")

    def require_organization(self) -> None:
        self.require_authenticated()
        if not self._auth.has_organization:
            raise ForbiddenError(f"Active organization required via {ORG_HEADER}")

    def require_role(self, *roles: Role) -> None:
        self.require_organization()
        if self._auth.role not in roles:
            allowed = ", ".join(role.value for role in roles)
            raise ForbiddenError(f"Requires one of roles: {allowed}")

    def require_viewer(self) -> None:
        self.require_role(Role.VIEWER, Role.EDITOR)

    def require_editor(self) -> None:
        self.require_role(Role.EDITOR)
