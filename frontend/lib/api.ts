const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Todo = {
  id: string;
  text: string;
  done: boolean;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || `Request failed: ${res.status}`);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
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

export function updateTodo(id: string, patch: { text?: string; done?: boolean }) {
  return request<Todo>(`/todos/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function deleteTodo(id: string) {
  return request<void>(`/todos/${id}`, { method: "DELETE" });
}
