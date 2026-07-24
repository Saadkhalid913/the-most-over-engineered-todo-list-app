from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.context import Role
from app.db.models import OrganizationMembershipRow, OrganizationRow
from app.models import Organization, OrganizationMembership


class OrganizationRepository:
    """Persistence for organizations and memberships."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_organization(self, name: str) -> Organization:
        row = OrganizationRow(id=str(uuid4()), name=name)
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return Organization(id=UUID(row.id), name=row.name)

    def get_organization(self, organization_id: UUID) -> Organization | None:
        row = self._session.get(OrganizationRow, str(organization_id))
        if row is None:
            return None
        return Organization(id=UUID(row.id), name=row.name)

    def add_membership(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
        role: Role,
    ) -> OrganizationMembership:
        org = self.get_organization(organization_id)
        if org is None:
            raise ValueError("organization not found")

        row = OrganizationMembershipRow(
            id=str(uuid4()),
            organization_id=str(organization_id),
            user_id=str(user_id),
            role=role.value,
        )
        self._session.add(row)
        self._session.commit()
        return OrganizationMembership(
            organization_id=organization_id,
            organization_name=org.name,
            user_id=user_id,
            role=role,
        )

    def get_membership(
        self,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationMembership | None:
        row = self._session.scalars(
            select(OrganizationMembershipRow).where(
                OrganizationMembershipRow.organization_id == str(organization_id),
                OrganizationMembershipRow.user_id == str(user_id),
            )
        ).first()
        if row is None:
            return None

        org = self.get_organization(organization_id)
        if org is None:
            return None

        return OrganizationMembership(
            organization_id=organization_id,
            organization_name=org.name,
            user_id=user_id,
            role=Role(row.role),
        )

    def list_memberships_for_user(self, user_id: UUID) -> list[OrganizationMembership]:
        rows = self._session.scalars(
            select(OrganizationMembershipRow).where(
                OrganizationMembershipRow.user_id == str(user_id)
            )
        ).all()
        memberships: list[OrganizationMembership] = []
        for row in rows:
            org = self.get_organization(UUID(row.organization_id))
            if org is None:
                continue
            memberships.append(
                OrganizationMembership(
                    organization_id=UUID(row.organization_id),
                    organization_name=org.name,
                    user_id=UUID(row.user_id),
                    role=Role(row.role),
                )
            )
        return memberships
