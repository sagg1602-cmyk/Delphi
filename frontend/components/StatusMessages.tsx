import { CircleAlert, LoaderCircle } from "lucide-react";

// Small shared pieces for loading and error states, so every page looks the same.

export function LoadingRow({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-6 text-sm text-stone-500">
      <LoaderCircle className="h-4 w-4 animate-spin" /> {label}
    </div>
  );
}

export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      <CircleAlert className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
      <p className="flex-1">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="shrink-0 font-medium text-red-700 underline hover:text-red-900">
          Try again
        </button>
      )}
    </div>
  );
}
