import { clearToken, getToken, setToken } from "./auth";
import {
  clearOrganizationId,
  getOrganizationId,
  setOrganizationId,
} from "./organization";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
export const ORG_HEADER = "X-Organization-Id";

export type Todo = {
  id: string;
  text: string;
  done: boolean;
  organization_id: string;
  user_id: string;
};

export type User = {
  id: string;
  username: string;
};

export type Role = "viewer" | "editor";

export type OrganizationMembership = {
  organization_id: string;
  organization_name: string;
  user_id: string;
  role: Role;
};

export type Organization = {
  id: string;
  name: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init?: RequestInit,
  options?: { auth?: boolean; org?: boolean },
): Promise<T> {
  const headers = new Headers(init?.headers);
  if (!headers.has("Content-Type") && init?.body) {
    headers.set("Content-Type", "application/json");
  }

  const useAuth = options?.auth !== false;
  if (useAuth) {
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const useOrg = options?.org !== false && useAuth;
  if (useOrg) {
    const orgId = getOrganizationId();
    if (orgId) {
      headers.set(ORG_HEADER, orgId);
    }
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });

  if (res.status === 401 && useAuth) {
    clearToken();
    clearOrganizationId();
  }

  if (!res.ok) {
    const detail = await res.text();
    let message = detail || `Request failed: ${res.status}`;
    try {
      const parsed = JSON.parse(detail) as { detail?: string };
      if (parsed.detail) message = parsed.detail;
    } catch {
      // keep raw text
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export async function register(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const token = await request<TokenResponse>(
    "/auth/register",
    {
      method: "POST",
      body: JSON.stringify({ username, password }),
    },
    { auth: false, org: false },
  );
  setToken(token.access_token);
  return token;
}

export async function login(
  username: string,
  password: string,
): Promise<TokenResponse> {
  const token = await request<TokenResponse>(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ username, password }),
    },
    { auth: false, org: false },
  );
  setToken(token.access_token);
  return token;
}

export function logout(): void {
  clearToken();
  clearOrganizationId();
}

export function getMe() {
  return request<User>("/auth/me", undefined, { org: false });
}

export function listOrganizations() {
  return request<OrganizationMembership[]>("/organizations", undefined, {
    org: false,
  });
}

export function createOrganization(name: string) {
  return request<Organization>(
    "/organizations",
    {
      method: "POST",
      body: JSON.stringify({ name }),
    },
    { org: false },
  );
}

export function addOrganizationMember(username: string, role: Role) {
  return request<OrganizationMembership>("/organizations/members", {
    method: "POST",
    body: JSON.stringify({ username, role }),
  });
}

export function selectOrganization(organizationId: string) {
  setOrganizationId(organizationId);
}

export function listTodos() {
  return request<Todo[]>("/todos");
}

export function createTodo(text: string) {
  return request<Todo>("/todos", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function updateTodo(
  id: string,
  patch: { text?: string; done?: boolean },
) {
  return request<Todo>(`/todos/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function deleteTodo(id: string) {
  return request<void>(`/todos/${id}`, { method: "DELETE" });
}
