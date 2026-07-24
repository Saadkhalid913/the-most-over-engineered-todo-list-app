import { clearToken, getToken, setToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Todo = {
  id: string;
  text: string;
  done: boolean;
};

export type User = {
  id: string;
  username: string;
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
  options?: { auth?: boolean },
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

  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
  });

  if (res.status === 401 && useAuth) {
    clearToken();
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
    { auth: false },
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
    { auth: false },
  );
  setToken(token.access_token);
  return token;
}

export function logout(): void {
  clearToken();
}

export function getMe() {
  return request<User>("/auth/me");
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
