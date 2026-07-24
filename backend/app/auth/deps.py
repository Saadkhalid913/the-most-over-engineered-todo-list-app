from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth.context import AuthorizationContext
from app.auth.gated import ForbiddenError, UnauthenticatedError
from app.auth.service import AuthService
from app.db.session import SessionLocal
from app.models import UserPublic
from app.organization_service import OrganizationService
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.todo_repository import TodoRepository
from app.repositories.user_repository import UserRepository
from app.scoped.organization_scoped_service import OrganizationScopedService
from app.scoped.todo_scoped_service import TodoScopedService
from app.todo_service import TodoService


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_authorization_context(request: Request) -> AuthorizationContext:
    auth = getattr(request.state, "authorization", None)
    if isinstance(auth, AuthorizationContext):
        return auth
    return AuthorizationContext.anonymous()


AuthorizationContextDep = Annotated[
    AuthorizationContext,
    Depends(get_authorization_context),
]


def get_auth_service(session: Annotated[Session, Depends(get_db)]) -> AuthService:
    return AuthService(
        UserRepository(session),
        OrganizationService(
            OrganizationRepository(session),
            UserRepository(session),
        ),
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(auth: AuthorizationContextDep) -> UserPublic:
    if not auth.is_authenticated or auth.user_id is None or auth.username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserPublic(id=auth.user_id, username=auth.username)


CurrentUserDep = Annotated[UserPublic, Depends(get_current_user)]


def get_todo_scoped_service(
    auth: AuthorizationContextDep,
    session: Annotated[Session, Depends(get_db)],
) -> TodoScopedService:
    return TodoScopedService(auth, TodoService(TodoRepository(session)))


TodoScopedServiceDep = Annotated[TodoScopedService, Depends(get_todo_scoped_service)]


def get_organization_scoped_service(
    auth: AuthorizationContextDep,
    session: Annotated[Session, Depends(get_db)],
) -> OrganizationScopedService:
    return OrganizationScopedService(
        auth,
        OrganizationService(
            OrganizationRepository(session),
            UserRepository(session),
        ),
    )


OrganizationScopedServiceDep = Annotated[
    OrganizationScopedService,
    Depends(get_organization_scoped_service),
]


def raise_auth_http_error(exc: Exception) -> None:
    if isinstance(exc, UnauthenticatedError):
        raise HTTPException(
            status_code=401,
            detail=str(exc) or "Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    if isinstance(exc, ForbiddenError):
        raise HTTPException(status_code=403, detail=str(exc)) from None
    raise exc
