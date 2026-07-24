from app.auth.context import AuthorizationContext, Role
from app.auth.gated import AuthGatedService, ForbiddenError
from app.models import Organization, OrganizationMembership
from app.organization_service import OrganizationService


class OrganizationScopedService(AuthGatedService):
    """Authorization-scoped facade over OrganizationService."""

    def __init__(
        self,
        auth: AuthorizationContext,
        organizations: OrganizationService,
    ) -> None:
        super().__init__(auth)
        self._organizations = organizations

    def list_memberships(self) -> list[OrganizationMembership]:
        self.require_authenticated()
        return self._organizations.list_memberships_for_user(self.actor_id)

    def create_organization(self, name: str) -> Organization:
        self.require_authenticated()
        return self._organizations.create_organization(
            name=name,
            owner_user_id=self.actor_id,
            owner_role=Role.EDITOR,
        )

    def add_member(self, username: str, role: Role) -> OrganizationMembership:
        self.require_editor()
        # Editors may grant viewer access only — prevents unbounded editor minting.
        if role is not Role.VIEWER:
            raise ForbiddenError("Editors may only add members with the viewer role")
        return self._organizations.add_member(
            organization_id=self.organization_id,
            username=username,
            role=role,
        )
