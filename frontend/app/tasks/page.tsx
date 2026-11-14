"use client";

import { useState, type FormEvent } from "react";
import { Plus, Clock, CalendarDays } from "lucide-react";
import { api, ApiError } from "@/lib/api-client";
import { useApiData } from "@/lib/use-api-data";
import type { Task } from "@/lib/types";
import { ErrorBanner, LoadingRow } from "@/components/StatusMessages";

// "2026-10-30" → a local date. (new Date("2026-10-30") would read it as UTC
// and show the day before in California.)
function parseDay(day: string) {
  const [y, m, d] = day.split("-").map(Number);
  return new Date(y, m - 1, d);
}

function dueLabel(due: string | null) {
  if (!due) return null;
  const date = parseDay(due);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Math.round((date.getTime() - today.getTime()) / 86_400_000);
  const text = date.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });
  if (days < 0) return { text: `Overdue · ${text}`, tone: "text-red-600" };
  if (days === 0) return { text: "Due today", tone: "text-amber-700" };
  return { text: `Due ${text}`, tone: "text-stone-500" };
}

// Undated tasks go last; otherwise earliest due date first
function byDueDate(a: Task, b: Task) {
  if (!a.due_date) return 1;
  if (!b.due_date) return -1;
  return a.due_date.localeCompare(b.due_date);
}

export default function TasksPage() {
  const tasks = useApiData(api.listTasks);

  // Form fields
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [duration, setDuration] = useState("");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Marking complete
  const [completingId, setCompletingId] = useState<number | null>(null);
  const [rowError, setRowError] = useState<string | null>(null);

  async function handleAdd(event: FormEvent) {
    event.preventDefault(); // stop the browser from reloading the page
    if (!title.trim()) {
      setFormError("Give the task a title.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await api.createTask({
        title: title.trim(),
        due_date: dueDate || null,
        // Only send a duration if one was typed
        ...(duration ? { duration_minutes: Number(duration) } : {}),
      });
      setTitle("");
      setDueDate("");
      setDuration("");
      tasks.reload();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Couldn't save the task.");
    } finally {
      setSaving(false);
    }
  }

  async function handleComplete(task: Task) {
    setCompletingId(task.id);
    setRowError(null);
    try {
      await api.completeTask(task.id); // PATCH /tasks/{id} { status: "done" }
      tasks.reload();
    } catch (err) {
      setRowError(err instanceof ApiError ? err.message : "Couldn't update the task.");
    } finally {
      setCompletingId(null);
    }
  }

  const all = tasks.data ?? [];
  const todo = all.filter((t) => t.status !== "done").sort(byDueDate);
  const done = all.filter((t) => t.status === "done");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight text-stone-900">Tasks</h1>
        <p className="mt-1 text-stone-500">What&apos;s on your plate. Delphi uses due dates to plan your Today.</p>
      </header>

      {/* Add a task */}
      <form onSubmit={handleAdd} className="rounded-2xl border border-stone-200 bg-white p-5">
        <div className="grid gap-3 sm:grid-cols-[1fr_160px_130px_auto]">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Add a task, e.g. Calculus problem set"
            maxLength={200}
            className="rounded-lg border border-stone-200 px-3 py-2 text-sm outline-none focus:border-delphi"
            aria-label="Task title"
          />
          <input
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="rounded-lg border border-stone-200 px-3 py-2 text-sm text-stone-600 outline-none focus:border-delphi"
            aria-label="Due date"
          />
          <input
            type="number"
            min={1}
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            placeholder="Minutes"
            className="rounded-lg border border-stone-200 px-3 py-2 text-sm outline-none focus:border-delphi"
            aria-label="Duration in minutes"
          />
          <button
            type="submit"
            disabled={saving}
            className="flex items-center justify-center gap-1.5 rounded-lg bg-delphi px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
          >
            <Plus className="h-4 w-4" />
            {saving ? "Adding…" : "Add"}
          </button>
        </div>
        {formError && <p className="mt-3 text-sm text-red-600">{formError}</p>}
      </form>

      {rowError && <ErrorBanner message={rowError} />}

      {/* Task list */}
      <section className="rounded-2xl border border-stone-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">To do</h2>
          {tasks.status === "loading" && tasks.data && <span className="text-xs text-stone-400">Refreshing…</span>}
        </div>

        {tasks.status === "loading" && !tasks.data && <LoadingRow label="Loading tasks…" />}
        {tasks.status === "error" && (
          <div className="mt-3">
            <ErrorBanner message={tasks.error.message} onRetry={tasks.reload} />
          </div>
        )}

        {tasks.data && todo.length === 0 && (
          <p className="py-6 text-sm text-stone-500">Nothing to do. Add a task above to get study suggestions.</p>
        )}

        <ul className="mt-2 divide-y divide-stone-100">
          {todo.map((task) => {
            const due = dueLabel(task.due_date);
            const busy = completingId === task.id;
            return (
              <li key={task.id} className={`flex items-center gap-3 py-3 ${busy ? "opacity-50" : ""}`}>
                <input
                  type="checkbox"
                  checked={busy}
                  disabled={busy}
                  onChange={() => handleComplete(task)}
                  className="h-4 w-4 cursor-pointer accent-delphi"
                  aria-label={`Mark "${task.title}" complete`}
                />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-stone-900">{task.title}</p>
                  <div className="mt-0.5 flex gap-4 text-xs">
                    {due && (
                      <span className={`flex items-center gap-1 ${due.tone}`}>
                        <CalendarDays className="h-3.5 w-3.5" /> {due.text}
                      </span>
                    )}
                    {task.duration_minutes ? (
                      <span className="flex items-center gap-1 text-stone-500">
                        <Clock className="h-3.5 w-3.5" /> {task.duration_minutes} min
                      </span>
                    ) : null}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      </section>

      {done.length > 0 && (
        <section className="rounded-2xl border border-stone-200 bg-white p-5">
          <h2 className="font-semibold text-stone-500">Done ({done.length})</h2>
          <ul className="mt-2 space-y-2">
            {done.map((task) => (
              <li key={task.id} className="text-sm text-stone-400 line-through">
                {task.title}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
