// Shapes of the data the Delphi API sends and accepts.
// These mirror the team contracts: Task, Note, Interest (Ava) and Recommendation (Youssef).
// If a contract changes, change it here first. TypeScript will then underline
// every place in the app that needs to follow.

/* ---------- Tasks (Ava) ---------- */

export type TaskStatus = "todo" | "done";
export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: number;
  user_id: number;
  title: string;
  due_date: string | null; // "YYYY-MM-DD"
  duration_minutes: number | null;
  priority: TaskPriority | null;
  status: TaskStatus;
  created_at: string; // ISO 8601, UTC
  updated_at: string;
}

export interface TaskCreate {
  title: string;
  due_date?: string | null;
  duration_minutes?: number | null;
  priority?: TaskPriority | null;
}

// PATCH sends only the fields that change.
export type TaskUpdate = Partial<Pick<Task, "title" | "due_date" | "duration_minutes" | "priority" | "status">>;

/* ---------- Notes (Ava) ---------- */

export interface Note {
  id: number;
  user_id: number;
  title: string;
  content: string;
  source_type: string;
  source_path: string | null;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  title: string;
  content?: string;
  source_type?: string;
}

/* ---------- Interests (Ava) ---------- */

export interface Interest {
  id: number;
  user_id: number;
  name: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface InterestCreate {
  name: string;
}

// PATCH /interests/{id} only accepts { active }
export interface InterestUpdate {
  active: boolean;
}

/* ---------- Recommendations (Youssef) ---------- */

export type RecommendationType = "study" | "discovery";
export type EvidenceType = "task" | "note" | "interest" | "resource";

// One item that explains a recommendation ("Why this?").
export interface Evidence {
  id: string;
  type: EvidenceType | string;
  label: string;
}

export interface RecommendationAction {
  type: "open_task" | "open_url";
  target: string; // task id for open_task, URL for open_url
}

// What the UI uses everywhere. Always has full evidence objects.
export interface Recommendation {
  id: string;
  type: RecommendationType;
  title: string;
  reason: string;
  estimated_minutes: number | null;
  evidence: Evidence[];
  action: RecommendationAction;
}

// What the API (or a fixture) may send.
// Live API (Youssef, Week 2): { id, estimated_minutes, evidence: [{type,id,label}], action: {type,target} }
// Week 1 fixtures:            { evidence_ids: [...], action_target: "..." }
// api-client.ts turns either one into a Recommendation.
export interface RawRecommendation {
  id?: string;
  type: RecommendationType;
  title: string;
  reason: string;
  estimated_minutes?: number | null;
  evidence?: Array<Partial<Evidence> & { id: string | number }>;
  evidence_ids?: Array<string | number>;
  action?: { type: "open_task" | "open_url"; target: string | number };
  action_target?: string | number;
}

/* ---------- Health ---------- */

export interface Health {
  status: string;
  database: string;
}
