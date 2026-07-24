"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  ApiError,
  createTodo,
  deleteTodo,
  getMe,
  listOrganizations,
  listTodos,
  login,
  logout,
  register,
  selectOrganization,
  type OrganizationMembership,
  type Todo,
  type User,
  updateTodo,
} from "../../lib/api";
import { isLoggedIn } from "../../lib/auth";
import { getOrganizationId } from "../../lib/organization";

export default function TodoApp() {
  const [user, setUser] = useState<User | null>(null);
  const [memberships, setMemberships] = useState<OrganizationMembership[]>([]);
  const [activeOrgId, setActiveOrgId] = useState<string | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [authBusy, setAuthBusy] = useState(false);

  const activeMembership = useMemo(
    () => memberships.find((m) => m.organization_id === activeOrgId) ?? null,
    [memberships, activeOrgId],
  );
  const canEdit = activeMembership?.role === "editor";

  async function loadMembershipsAndSelectOrg() {
    const orgs = await listOrganizations();
    setMemberships(orgs);

    const saved = getOrganizationId();
    const selected =
      orgs.find((m) => m.organization_id === saved)?.organization_id ??
      orgs[0]?.organization_id ??
      null;

    if (selected) {
      selectOrganization(selected);
      setActiveOrgId(selected);
    } else {
      setActiveOrgId(null);
    }

    return selected;
  }

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      if (!isLoggedIn()) {
        if (!cancelled) {
          setAuthChecked(true);
        }
        return;
      }

      try {
        const me = await getMe();
        if (cancelled) return;
        setUser(me);
        await loadMembershipsAndSelectOrg();
        if (!cancelled) setError(null);
      } catch {
        if (!cancelled) {
          setUser(null);
          setMemberships([]);
          setActiveOrgId(null);
        }
      } finally {
        if (!cancelled) {
          setAuthChecked(true);
        }
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!user || !activeOrgId) {
      setTodos([]);
      return;
    }

    let cancelled = false;
    setLoading(true);

    listTodos()
      .then((data) => {
        if (!cancelled) {
          setTodos(data);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load todos");
          if (err instanceof ApiError && err.status === 401) {
            setUser(null);
          }
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [user, activeOrgId]);

  async function onAuthSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthBusy(true);
    setError(null);
    try {
      if (authMode === "register") {
        await register(username.trim(), password);
      } else {
        await login(username.trim(), password);
      }
      const me = await getMe();
      setUser(me);
      await loadMembershipsAndSelectOrg();
      setPassword("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    } finally {
      setAuthBusy(false);
    }
  }

  function onLogout() {
    logout();
    setUser(null);
    setMemberships([]);
    setActiveOrgId(null);
    setTodos([]);
    setError(null);
  }

  function onOrgChange(organizationId: string) {
    selectOrganization(organizationId);
    setActiveOrgId(organizationId);
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = text.trim();
    if (!value || !canEdit) return;

    setError(null);
    try {
      const todo = await createTodo(value);
      setTodos((prev) => [...prev, todo]);
      setText("");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create todo");
    }
  }

  async function onToggle(todo: Todo) {
    if (!canEdit) return;
    setBusyId(todo.id);
    setError(null);
    try {
      const updated = await updateTodo(todo.id, { done: !todo.done });
      setTodos((prev) => prev.map((t) => (t.id === todo.id ? updated : t)));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to update todo");
    } finally {
      setBusyId(null);
    }
  }

  async function onDelete(id: string) {
    if (!canEdit) return;
    setBusyId(id);
    setError(null);
    try {
      await deleteTodo(id);
      setTodos((prev) => prev.filter((t) => t.id !== id));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to delete todo");
    } finally {
      setBusyId(null);
    }
  }

  if (!authChecked) {
    return (
      <main className="mx-auto flex w-full max-w-lg flex-col gap-8 px-6 py-16">
        <p className="text-sm text-zinc-500">Loading…</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="mx-auto flex w-full max-w-lg flex-col gap-8 px-6 py-16">
        <header className="space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight">Todo</h1>
          <p className="text-sm text-zinc-500">
            {authMode === "login"
              ? "Sign in to manage your todos."
              : "Create an account to get started."}
          </p>
        </header>

        <form onSubmit={onAuthSubmit} className="flex flex-col gap-3">
          <input
            type="text"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            className="border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-zinc-900 dark:border-zinc-700 dark:focus:border-zinc-100"
            required
            minLength={authMode === "register" ? 3 : 1}
          />
          <input
            type="password"
            autoComplete={
              authMode === "login" ? "current-password" : "new-password"
            }
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            className="border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-zinc-900 dark:border-zinc-700 dark:focus:border-zinc-100"
            required
            minLength={authMode === "register" ? 8 : 1}
          />
          <button
            type="submit"
            disabled={authBusy || !username.trim() || !password}
            className="bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
          >
            {authBusy
              ? "Please wait…"
              : authMode === "login"
                ? "Sign in"
                : "Create account"}
          </button>
        </form>

        {error ? (
          <p className="text-sm text-red-600 dark:text-red-400" role="alert">
            {error}
          </p>
        ) : null}

        <p className="text-sm text-zinc-500">
          {authMode === "login" ? (
            <>
              No account?{" "}
              <button
                type="button"
                className="underline"
                onClick={() => {
                  setAuthMode("register");
                  setError(null);
                }}
              >
                Register
              </button>
            </>
          ) : (
            <>
              Already registered?{" "}
              <button
                type="button"
                className="underline"
                onClick={() => {
                  setAuthMode("login");
                  setError(null);
                }}
              >
                Sign in
              </button>
            </>
          )}
        </p>
      </main>
    );
  }

  return (
    <main className="mx-auto flex w-full max-w-lg flex-col gap-8 px-6 py-16">
      <header className="flex items-start justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-3xl font-semibold tracking-tight">Todo</h1>
          <p className="text-sm text-zinc-500">Signed in as {user.username}</p>
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-zinc-100"
        >
          Log out
        </button>
      </header>

      {memberships.length > 0 ? (
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-zinc-500">Organization</span>
          <select
            value={activeOrgId ?? ""}
            onChange={(e) => onOrgChange(e.target.value)}
            className="border border-zinc-300 bg-transparent px-3 py-2 outline-none focus:border-zinc-900 dark:border-zinc-700 dark:focus:border-zinc-100"
          >
            {memberships.map((membership) => (
              <option
                key={membership.organization_id}
                value={membership.organization_id}
              >
                {membership.organization_name} ({membership.role})
              </option>
            ))}
          </select>
        </label>
      ) : null}

      {canEdit ? (
        <form onSubmit={onSubmit} className="flex gap-2">
          <input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="What needs doing?"
            className="min-w-0 flex-1 border border-zinc-300 bg-transparent px-3 py-2 text-sm outline-none focus:border-zinc-900 dark:border-zinc-700 dark:focus:border-zinc-100"
          />
          <button
            type="submit"
            className="bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900"
            disabled={!text.trim()}
          >
            Add
          </button>
        </form>
      ) : (
        <p className="text-sm text-zinc-500">
          You have viewer access in this organization.
        </p>
      )}

      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <p className="text-sm text-zinc-500">Loading…</p>
      ) : todos.length === 0 ? (
        <p className="text-sm text-zinc-500">No todos yet.</p>
      ) : (
        <ul className="divide-y divide-zinc-200 border-y border-zinc-200 dark:divide-zinc-800 dark:border-zinc-800">
          {todos.map((todo) => (
            <li key={todo.id} className="flex items-center gap-3 py-3 text-sm">
              <input
                type="checkbox"
                checked={todo.done}
                onChange={() => onToggle(todo)}
                disabled={!canEdit || busyId === todo.id}
                className="size-4 accent-zinc-900"
                aria-label={`Mark "${todo.text}" as ${todo.done ? "not done" : "done"}`}
              />
              <span
                className={`min-w-0 flex-1 ${todo.done ? "text-zinc-400 line-through" : ""}`}
              >
                {todo.text}
              </span>
              {canEdit ? (
                <button
                  type="button"
                  onClick={() => onDelete(todo.id)}
                  disabled={busyId === todo.id}
                  className="text-zinc-500 hover:text-zinc-900 disabled:opacity-50 dark:hover:text-zinc-100"
                >
                  Delete
                </button>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
