"use client";

import { api } from "@/lib/api-client";
import { useApiData } from "@/lib/use-api-data";

// Calls GET /health from the browser. Green = the API answered (so CORS works too).
export default function ApiStatus() {
  const health = useApiData(api.health);

  const ok = health.status === "success" && health.data.database === "ok";
  const color = health.status === "loading" ? "bg-stone-300" : ok ? "bg-emerald-500" : "bg-red-500";
  const label =
    health.status === "loading"
      ? "Checking API…"
      : ok
        ? "API connected"
        : health.status === "error"
          ? health.error.message
          : "API is up, but the database isn't";

  return (
    <button
      onClick={health.reload}
      title={`${label} (click to check again)`}
      className="flex flex-col items-center gap-1 text-[10px] text-stone-400 hover:text-stone-600"
    >
      <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
      API
    </button>
  );
}
