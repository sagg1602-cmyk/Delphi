import { Recommendation } from "@/types/recommendation";

export default function RecommendationCard({ rec }: { rec: Recommendation }) {
  const isStudy = rec.type === "study";
  const badgeColor = isStudy
    ? "bg-blue-100 text-blue-800"
    : "bg-green-100 text-green-800";
  const count = rec.evidence_ids.length;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
      <span className={`rounded-full px-3 py-1 text-xs font-semibold uppercase ${badgeColor}`}>
        {rec.type}
      </span>
      <h2 className="mt-3 text-lg font-semibold text-gray-900">{rec.title}</h2>
      <p className="mt-1 text-sm text-gray-600">{rec.reason}</p>
      <p className="mt-3 text-xs text-gray-400">
        Based on {count} item{count === 1 ? "" : "s"}
      </p>

      {isStudy ? (
        <button className="mt-4 rounded-lg bg-gray-900 px-4 py-2 text-sm text-white hover:bg-gray-700">
          Open task
        </button>
      ) : (
        <a
          href={rec.action_target}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block rounded-lg bg-gray-900 px-4 py-2 text-sm text-white hover:bg-gray-700"
        >
          Open resource ↗
        </a>
      )}
    </div>
  );
}