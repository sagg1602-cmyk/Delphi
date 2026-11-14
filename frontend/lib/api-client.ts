// The ONLY place the frontend talks to the Delphi API.
// Pages call the functions in `api` below. They never call fetch() themselves,
// so the base URL, the dev header and error handling all live in one file.

import sampleRecommendations from "@/data/sample_recommendations.json"; // copy of shared/fixtures/recommendations_week2.output.json
import type {
  Evidence,
  Health,
  Interest,
  InterestCreate,
  InterestUpdate,
  Note,
  NoteCreate,
  RawRecommendation,
  Recommendation,
  Task,
  TaskCreate,
  TaskUpdate,
} from "@/lib/types";

/* ---------- Settings (from frontend/.env.local) ---------- */

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

// true = Today uses the sample fixture instead of the live endpoint.
export const USE_FIXTURES = process.env.NEXT_PUBLIC_USE_FIXTURES === "true";

// Dev-only stand-in for login. Every request says "I am dev-user-1".
const DEV_USER = "dev-user-1";

/* ---------- Errors ---------- */

// Every failed request becomes an ApiError with a message a person can read.
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number, // 0 means the API could not be reached at all
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// FastAPI sends { detail: "text" } or, for invalid data (422),
// { detail: [{ loc: ["body", "title"], msg: "..." }] }.
function readErrorDetail(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d: { loc?: unknown[]; msg?: string }) => {
        const field = d.loc?.filter((part) => part !== "body").join(".");
        return field ? `${field}: ${d.msg}` : d.msg;
      })
      .join("; ");
  }

  if (status === 404) return "Not found.";
  if (status >= 500) return "The server had a problem. Try again in a moment.";
  return `Request failed (HTTP ${status}).`;
}

/* ---------- The one function that calls fetch ---------- */

async function request<T>(path: string, options: { method?: string; body?: unknown } = {}): Promise<T> {
  const { method = "GET", body } = options;

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers: {
        Accept: "application/json",
        "X-Dev-User": DEV_USER,
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    // fetch only throws when the request never got an answer:
    // the backend is off, the URL is wrong, or CORS blocked it.
    throw new ApiError(`Can't reach the Delphi API at ${API_URL}. Is the backend running?`, 0);
  }

  // Some responses (like a successful DELETE) have no body.
  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    throw new ApiError(readErrorDetail(data, response.status), response.status);
  }

  return data as T;
}

/* ---------- Recommendation helpers ---------- */

// "task_calc" → { type: "task", label: "calc" }. Used when the API only sends ids.
function evidenceFromId(rawId: string | number): Evidence {
  const id = String(rawId);
  const match = id.match(/^(task|note|interest|resource)[_:-](.+)$/);
  if (!match) return { id, type: "item", label: id };
  return { id, type: match[1], label: match[2].replace(/_/g, " ") };
}

// Accepts the live response or Week 1 fixtures, and returns one consistent shape.
export function normalizeRecommendation(raw: RawRecommendation, index = 0): Recommendation {
  const evidence: Evidence[] = raw.evidence
    ? raw.evidence.map((e) => {
        const fallback = evidenceFromId(e.id);
        return {
          id: String(e.id),
          type: e.type ?? fallback.type,
          label: e.label ?? fallback.label,
        };
      })
    : (raw.evidence_ids ?? []).map(evidenceFromId);

  const target = String(raw.action?.target ?? raw.action_target ?? "");
  const actionType = raw.action?.type ?? (raw.type === "discovery" ? "open_url" : "open_task");

  return {
    id: raw.id ?? `${raw.type}-${target}-${index}`,
    type: raw.type,
    title: raw.title,
    reason: raw.reason,
    estimated_minutes: raw.estimated_minutes ?? null,
    evidence,
    action: { type: actionType, target },
  };
}

// The live API sends { recommendations: [...] }; Week 1 fixtures are a plain array.
function toRecommendationList(data: unknown): Recommendation[] {
  const list = Array.isArray(data)
    ? data
    : ((data as { recommendations?: RawRecommendation[] } | null)?.recommendations ?? []);
  return (list as RawRecommendation[]).map((raw, i) => normalizeRecommendation(raw, i));
}

/* ---------- Everything the app can ask the API ---------- */

export const api = {
  health: () => request<Health>("/health"),

  // Tasks
  listTasks: () => request<Task[]>("/tasks"),
  createTask: (task: TaskCreate) => request<Task>("/tasks", { method: "POST", body: task }),
  updateTask: (id: number, changes: TaskUpdate) =>
    request<Task>(`/tasks/${id}`, { method: "PATCH", body: changes }),
  completeTask: (id: number) => request<Task>(`/tasks/${id}`, { method: "PATCH", body: { status: "done" } }),

  // Notes
  listNotes: () => request<Note[]>("/notes"),
  createNote: (note: NoteCreate) => request<Note>("/notes", { method: "POST", body: note }),
  deleteNote: (id: number) => request<void>(`/notes/${id}`, { method: "DELETE" }), // below the cut line
  searchNotes: (q: string) => request<Note[]>(`/notes/search?q=${encodeURIComponent(q)}`), // below the cut line

  // Interests (below the cut line)
  listInterests: () => request<Interest[]>("/interests"),
  createInterest: (interest: InterestCreate) => request<Interest>("/interests", { method: "POST", body: interest }),
  updateInterest: (id: number, changes: InterestUpdate) =>
    request<Interest>(`/interests/${id}`, { method: "PATCH", body: changes }),

  // Recommendations: live endpoint, or the sample fixture in fixture mode
  generateRecommendations: async (): Promise<Recommendation[]> => {
    if (USE_FIXTURES) return toRecommendationList(sampleRecommendations);
    try {
      const data = await request<unknown>("/recommendations/generate", { method: "POST" });
      return toRecommendationList(data);
    } catch (err) {
      // 404 = the route isn't plugged into this backend yet (not a frontend bug)
      if (err instanceof ApiError && err.status === 404) {
        throw new ApiError(
          "This backend doesn't have /recommendations/generate yet. Set NEXT_PUBLIC_USE_FIXTURES=true to use sample data.",
          404,
        );
      }
      throw err;
    }
  },
};
