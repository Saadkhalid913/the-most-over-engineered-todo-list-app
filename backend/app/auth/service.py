from uuid import UUID

from app.auth.jwt import create_access_token
from app.auth.passwords import hash_password, verify_password
from app.models import TokenResponse, UserPublic
from app.organization_service import OrganizationService
from app.repositories.user_repository import UserRepository


class AuthError(Exception):
    """Raised for invalid credentials or auth conflicts."""


class UsernameTakenError(AuthError):
    """Raised when registering an existing username."""


class InvalidCredentialsError(AuthError):
    """Raised when login username/password do not match."""


class AuthService:
    """Register/login users and issue access tokens."""

    def __init__(
        self,
        repository: UserRepository,
        organizations: OrganizationService,
    ) -> None:
        self._repository = repository
        self._organizations = organizations

    def register(self, username: str, password: str) -> TokenResponse:
        if self._repository.get_by_username(username) is not None:
            raise UsernameTakenError(username)

        user = self._repository.create_user(username, hash_password(password))
        self._organizations.create_organization(
            name=f"{user.username}'s workspace",
            owner_user_id=user.id,
        )
        return self._token_for(user)

    def login(self, username: str, password: str) -> TokenResponse:
        row = self._repository.get_by_username(username)
        if row is None or not verify_password(password, row.password_hash):
            raise InvalidCredentialsError()

        user = UserPublic(id=UUID(row.id), username=row.username)
        return self._token_for(user)

    def get_user(self, user_id: UUID) -> UserPublic | None:
        return self._repository.get_by_id(user_id)

    @staticmethod
    def _token_for(user: UserPublic) -> TokenResponse:
        token = create_access_token(user_id=user.id, username=user.username)
        return TokenResponse(access_token=token, token_type="bearer")
