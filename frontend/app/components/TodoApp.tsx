"use client";

import { FormEvent, useEffect, useState } from "react";
import {
  createTodo,
  deleteTodo,
  listTodos,
  type Todo,
  updateTodo,
} from "../../lib/api";

export default function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

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
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = text.trim();
    if (!value) return;

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

  return (
    <main className="mx-auto flex w-full max-w-lg flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold tracking-tight">Todo</h1>
        <p className="text-sm text-zinc-500">
          Add, complete, and delete items against the API.
        </p>
      </header>

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
                disabled={busyId === todo.id}
                className="size-4 accent-zinc-900"
                aria-label={`Mark "${todo.text}" as ${todo.done ? "not done" : "done"}`}
              />
              <span
                className={`min-w-0 flex-1 ${todo.done ? "text-zinc-400 line-through" : ""}`}
              >
                {todo.text}
              </span>
              <button
                type="button"
                onClick={() => onDelete(todo.id)}
                disabled={busyId === todo.id}
                className="text-zinc-500 hover:text-zinc-900 disabled:opacity-50 dark:hover:text-zinc-100"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
