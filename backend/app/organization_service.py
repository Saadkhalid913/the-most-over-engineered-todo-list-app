from uuid import UUID

from app.auth.context import Role
from app.models import Organization, OrganizationMembership
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository


class OrganizationNotFoundError(Exception):
    """Raised when an organization does not exist."""


class MembershipExistsError(Exception):
    """Raised when the user is already a member of the organization."""


class UserNotFoundError(Exception):
    """Raised when a username cannot be resolved."""


class OrganizationService:
    """Domain operations for organizations and memberships (no auth coupling)."""

    def __init__(
        self,
        organizations: OrganizationRepository,
        users: UserRepository,
    ) -> None:
        self._organizations = organizations
        self._users = users

    def create_organization(
        self,
        *,
        name: str,
        owner_user_id: UUID,
        owner_role: Role = Role.EDITOR,
    ) -> Organization:
        organization = self._organizations.create_organization(name)
        self._organizations.add_membership(
            organization_id=organization.id,
            user_id=owner_user_id,
            role=owner_role,
        )
        return organization

    def list_memberships_for_user(
        self,
        user_id: UUID,
    ) -> list[OrganizationMembership]:
        return self._organizations.list_memberships_for_user(user_id)

    def get_membership(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMembership | None:
        return self._organizations.get_membership(organization_id, user_id)

    def add_member(
        self,
        *,
        organization_id: UUID,
        username: str,
        role: Role,
    ) -> OrganizationMembership:
        if self._organizations.get_organization(organization_id) is None:
            raise OrganizationNotFoundError(organization_id)

        user_row = self._users.get_by_username(username)
        if user_row is None:
            raise UserNotFoundError(username)

        user_id = UUID(user_row.id)
        if self._organizations.get_membership(organization_id, user_id) is not None:
            raise MembershipExistsError(username)

        return self._organizations.add_membership(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )
