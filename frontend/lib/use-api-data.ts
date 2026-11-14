"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError } from "@/lib/api-client";

type LoadState<T> =
  | { status: "loading"; data?: T; error?: undefined }
  | { status: "success"; data: T; error?: undefined }
  | { status: "error"; data?: T; error: ApiError };

// Loads data from the API when a page opens, and gives back:
//   status: "loading" | "success" | "error"
//   data:   what came back (kept while reloading, so the page doesn't flash)
//   error:  an ApiError with a readable message
//   reload: call it to fetch again (refresh buttons, after saving something)
//
// Pass a function defined outside the component, like api.listTasks,
// so it doesn't change on every render.
export function useApiData<T>(fetcher: () => Promise<T>) {
  const [state, setState] = useState<LoadState<T>>({ status: "loading" });
  const [version, setVersion] = useState(0);

  useEffect(() => {
    let cancelled = false; // ignore answers that arrive after the page closed
    fetcher()
      .then((data) => {
        if (!cancelled) setState({ status: "success", data });
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const error = err instanceof ApiError ? err : new ApiError("Something went wrong.", -1);
        setState((prev) => ({ status: "error", data: prev.data, error }));
      });
    return () => {
      cancelled = true;
    };
  }, [fetcher, version]);

  const reload = useCallback(() => {
    setState((prev) => ({ status: "loading", data: prev.data }));
    setVersion((v) => v + 1);
  }, []);

  return { ...state, reload };
}
