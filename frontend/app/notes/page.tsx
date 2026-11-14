"use client";

import { useState, type FormEvent } from "react";
import { Plus } from "lucide-react";
import { api, ApiError } from "@/lib/api-client";
import { useApiData } from "@/lib/use-api-data";
import { ErrorBanner, LoadingRow } from "@/components/StatusMessages";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export default function NotesPage() {
  const notes = useApiData(api.listNotes);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    if (!title.trim()) {
      setFormError("Give the note a title.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await api.createNote({ title: title.trim(), content });
      setTitle("");
      setContent("");
      notes.reload();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : "Couldn't save the note.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight text-stone-900">My Notes</h1>
        <p className="mt-1 text-stone-500">Everything you&apos;ve captured. Delphi connects notes to your tasks.</p>
      </header>

      {/* Create a note */}
      <form onSubmit={handleCreate} className="space-y-3 rounded-2xl border border-stone-200 bg-white p-5">
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Title, e.g. Calculus: derivative rules"
          maxLength={200}
          className="w-full rounded-lg border border-stone-200 px-3 py-2 text-sm font-medium outline-none focus:border-delphi"
          aria-label="Note title"
        />
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your note…"
          rows={4}
          className="w-full resize-y rounded-lg border border-stone-200 px-3 py-2 text-sm outline-none focus:border-delphi"
          aria-label="Note content"
        />
        <div className="flex items-center justify-between">
          <p className="text-sm text-red-600">{formError}</p>
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-1.5 rounded-lg bg-delphi px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
          >
            <Plus className="h-4 w-4" />
            {saving ? "Saving…" : "Save note"}
          </button>
        </div>
      </form>

      {/* Note list */}
      {notes.status === "loading" && !notes.data && <LoadingRow label="Loading notes…" />}
      {notes.status === "error" && <ErrorBanner message={notes.error.message} onRetry={notes.reload} />}

      {notes.data && notes.data.length === 0 && (
        <p className="text-sm text-stone-500">No notes yet. Your first one goes above.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        {notes.data?.map((note) => (
          <article key={note.id} className="rounded-2xl border border-stone-200 bg-white p-5">
            <h2 className="font-semibold text-stone-900">{note.title}</h2>
            {note.content && (
              <p className="mt-2 line-clamp-4 whitespace-pre-line text-sm text-stone-600">{note.content}</p>
            )}
            <p className="mt-3 text-xs text-stone-400">{formatDate(note.created_at)}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
