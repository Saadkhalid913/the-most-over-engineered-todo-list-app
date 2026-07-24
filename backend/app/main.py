from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.auth.deps import (
    AuthServiceDep,
    CurrentUserDep,
    OrganizationScopedServiceDep,
    TodoScopedServiceDep,
    raise_auth_http_error,
)
from app.auth.gated import ForbiddenError, UnauthenticatedError
from app.auth.middleware import AuthorizationMiddleware
from app.auth.service import InvalidCredentialsError, UsernameTakenError
from app.models import (
    AddOrganizationMember,
    Organization,
    OrganizationCreate,
    OrganizationMembership,
    Todo,
    TodoCreate,
    TodoUpdate,
    TokenResponse,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.organization_service import (
    MembershipExistsError,
    OrganizationNotFoundError,
    UserNotFoundError,
)
from app.todo_service import TodoNotFoundError

app = FastAPI(title="Todo API")

app.add_middleware(AuthorizationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/register", response_model=TokenResponse, status_code=201)
def register(body: UserRegister, auth_service: AuthServiceDep) -> TokenResponse:
    try:
        return auth_service.register(body.username, body.password)
    except UsernameTakenError:
        raise HTTPException(status_code=409, detail="Username already taken") from None


@app.post("/auth/login", response_model=TokenResponse)
def login(body: UserLogin, auth_service: AuthServiceDep) -> TokenResponse:
    try:
        return auth_service.login(body.username, body.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        ) from None


@app.get("/auth/me", response_model=UserPublic)
def me(current_user: CurrentUserDep) -> UserPublic:
    return current_user


@app.get("/organizations", response_model=list[OrganizationMembership])
def list_organizations(
    org_service: OrganizationScopedServiceDep,
) -> list[OrganizationMembership]:
    try:
        return org_service.list_memberships()
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise


@app.post("/organizations", response_model=Organization, status_code=201)
def create_organization(
    body: OrganizationCreate,
    org_service: OrganizationScopedServiceDep,
) -> Organization:
    try:
        return org_service.create_organization(body.name)
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise


@app.post(
    "/organizations/members",
    response_model=OrganizationMembership,
    status_code=201,
)
def add_organization_member(
    body: AddOrganizationMember,
    org_service: OrganizationScopedServiceDep,
) -> OrganizationMembership:
    try:
        return org_service.add_member(body.username, body.role)
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found") from None
    except MembershipExistsError:
        raise HTTPException(
            status_code=409, detail="User is already a member"
        ) from None
    except OrganizationNotFoundError:
        raise HTTPException(status_code=404, detail="Organization not found") from None


@app.get("/todos", response_model=list[Todo])
def list_todos(todo_service: TodoScopedServiceDep) -> list[Todo]:
    try:
        return todo_service.list_todos()
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: UUID, todo_service: TodoScopedServiceDep) -> Todo:
    try:
        return todo_service.get_todo(todo_id)
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(body: TodoCreate, todo_service: TodoScopedServiceDep) -> Todo:
    try:
        return todo_service.create_todo(body.text)
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(
    todo_id: UUID,
    body: TodoUpdate,
    todo_service: TodoScopedServiceDep,
) -> Todo:
    try:
        return todo_service.update_todo(
            todo_id,
            body.model_dump(exclude_unset=True),
        )
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: UUID, todo_service: TodoScopedServiceDep) -> None:
    try:
        todo_service.delete_todo(todo_id)
    except (UnauthenticatedError, ForbiddenError) as exc:
        raise_auth_http_error(exc)
        raise
    except TodoNotFoundError:
        raise HTTPException(status_code=404, detail="Todo not found") from None
