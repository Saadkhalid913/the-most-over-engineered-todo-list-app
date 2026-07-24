from uuid import UUID

import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.auth.context import ORG_HEADER, AuthorizationContext, Role
from app.auth.jwt import decode_access_token
from app.db.session import SessionLocal
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.user_repository import UserRepository


class InvalidAccessTokenError(Exception):
    """Raised when a Bearer token is present but invalid or unknown."""


def build_authorization_context(
    *,
    token: str | None,
    organization_id_header: str | None,
) -> AuthorizationContext:
    if not token:
        return AuthorizationContext.anonymous()

    session = SessionLocal()
    try:
        try:
            payload = decode_access_token(token)
            user_id = UUID(str(payload["sub"]))
            username = str(payload.get("username") or "")
        except (jwt.PyJWTError, KeyError, ValueError, TypeError) as exc:
            raise InvalidAccessTokenError("Invalid or expired token") from exc

        user = UserRepository(session).get_by_id(user_id)
        if user is None:
            raise InvalidAccessTokenError("Invalid or expired token")

        organization_id: UUID | None = None
        role: Role | None = None
        if organization_id_header:
            try:
                requested_org_id = UUID(organization_id_header)
            except ValueError:
                requested_org_id = None

            if requested_org_id is not None:
                membership = OrganizationRepository(session).get_membership(
                    requested_org_id,
                    user.id,
                )
                if membership is not None:
                    organization_id = membership.organization_id
                    role = membership.role

        return AuthorizationContext(
            user_id=user.id,
            username=user.username or username,
            organization_id=organization_id,
            role=role,
            authenticated=True,
        )
    finally:
        session.close()


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """Attach an AuthorizationContext to every request for DI into scoped services."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        token: str | None = None
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip() or None
            if token is None:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"},
                    headers={"WWW-Authenticate": "Bearer"},
                )

        try:
            request.state.authorization = build_authorization_context(
                token=token,
                organization_id_header=request.headers.get(ORG_HEADER),
            )
        except InvalidAccessTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
