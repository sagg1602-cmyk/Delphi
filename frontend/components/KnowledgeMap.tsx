import { BookOpen, Compass, Sparkles, Share2, List, LayoutGrid, Filter } from "lucide-react";
import { Recommendation } from "@/types/recommendation";
import CaptureCard from "@/components/CaptureCard";

// Layout knobs: tweak these if cards overlap on your screen (all values are % of the map area)
const CENTER = { x: 50, y: 50 };
const NODE_DISTANCE = { x: 28, y: 26 };      // how far cards sit from the center
const EVIDENCE_DISTANCE = { x: 18, y: 20 };  // how far evidence dots sit from their card

const typeStyles = {
  study: {
    icon: BookOpen, label: "Study",
    card: "bg-indigo-50/90 border-indigo-200", iconColor: "text-indigo-600", dot: "bg-indigo-400",
  },
  discovery: {
    icon: Compass, label: "Discover",
    card: "bg-emerald-50/90 border-emerald-200", iconColor: "text-emerald-600", dot: "bg-emerald-400",
  },
};

// "task_calc" → "task · calc"
function formatEvidence(id: string) {
  const [prefix, ...rest] = id.split("_");
  return rest.length ? `${prefix} · ${rest.join(" ")}` : id;
}

// Places each recommendation around the center, and its evidence around it
function layout(recs: Recommendation[]) {
  return recs.map((rec, i) => {
    const angle = Math.PI + 0.4 + (i * 2 * Math.PI) / recs.length;
    const x = CENTER.x + NODE_DISTANCE.x * Math.cos(angle);
    const y = CENTER.y + NODE_DISTANCE.y * Math.sin(angle);

    const evidence = rec.evidence_ids.map((id, j) => {
      const spread = (j - (rec.evidence_ids.length - 1) / 2) * 0.9;
      const a = angle + spread;
      return {
        id,
        x: x + EVIDENCE_DISTANCE.x * Math.cos(a),
        y: y + EVIDENCE_DISTANCE.y * Math.sin(a),
      };
    });

    return { rec, x, y, evidence };
  });
}

export default function KnowledgeMap({ recs }: { recs: Recommendation[] }) {
  const nodes = layout(recs);

  return (
    <section className="relative flex min-h-[560px] flex-1 flex-col rounded-2xl border border-stone-200 bg-white p-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Your space, connected.</h2>
          <p className="text-sm text-stone-500">A visual map of your ideas, notes, and goals.</p>
        </div>
        <div className="flex rounded-xl bg-stone-100 p-1 text-sm">
          <span className="flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 font-medium shadow-sm">
            <Share2 className="h-4 w-4 text-delphi" /> Graph
          </span>
          <span className="flex items-center gap-1.5 px-3 py-1.5 text-stone-500">
            <List className="h-4 w-4" /> List
          </span>
          <span className="flex items-center gap-1.5 px-3 py-1.5 text-stone-500">
            <LayoutGrid className="h-4 w-4" /> Canvas
          </span>
        </div>
      </div>

      {/* Map canvas with dotted background */}
      <div
        className="relative mt-4 flex-1 rounded-xl"
        style={{
          backgroundImage: "radial-gradient(#e7e5e4 1px, transparent 1px)",
          backgroundSize: "20px 20px",
        }}
      >
        {/* Lines */}
        <svg className="absolute inset-0 h-full w-full">
          {nodes.map((n) => (
            <g key={n.rec.action_target}>
              <line x1={`${CENTER.x}%`} y1={`${CENTER.y}%`} x2={`${n.x}%`} y2={`${n.y}%`} stroke="#a5a3f0" strokeWidth="1.5" />
              {n.evidence.map((e) => (
                <line key={e.id} x1={`${n.x}%`} y1={`${n.y}%`} x2={`${e.x}%`} y2={`${e.y}%`} stroke="#d6d3d1" strokeWidth="1" />
              ))}
            </g>
          ))}
        </svg>

        {/* Center hub */}
        <div
          className="absolute -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-delphi/30 bg-delphi-light px-6 py-4 shadow-sm"
          style={{ left: `${CENTER.x}%`, top: `${CENTER.y}%` }}
        >
          <div className="flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-delphi" />
            <div>
              <p className="text-lg font-semibold text-stone-900">Today</p>
              <p className="text-xs text-stone-500">
                {recs.length} recommendation{recs.length === 1 ? "" : "s"}
              </p>
            </div>
          </div>
        </div>

        {/* Empty state */}
        {recs.length === 0 && (
          <p className="absolute left-1/2 top-[62%] -translate-x-1/2 text-sm text-stone-500">
            No recommendations yet. Add a task or note to get started.
          </p>
        )}

        {/* Evidence dots */}
        {nodes.flatMap((n) =>
          n.evidence.map((e) => (
            <div
              key={`${n.rec.action_target}-${e.id}`}
              className="absolute flex -translate-x-1/2 -translate-y-1/2 items-center gap-1.5 whitespace-nowrap text-[11px] text-stone-500"
              style={{ left: `${e.x}%`, top: `${e.y}%` }}
            >
              <span className={`h-2 w-2 rounded-full ${typeStyles[n.rec.type].dot}`} />
              {formatEvidence(e.id)}
            </div>
          ))
        )}

        {/* Recommendation cards */}
        {nodes.map(({ rec, x, y }) => {
          const s = typeStyles[rec.type];
          const Icon = s.icon;
          const count = rec.evidence_ids.length;
          return (
            <div
              key={rec.action_target}
              className={`absolute w-64 -translate-x-1/2 -translate-y-1/2 rounded-2xl border px-4 py-3 shadow-sm transition hover:shadow-md ${s.card}`}
              style={{ left: `${x}%`, top: `${y}%` }}
            >
              <div className="flex items-start gap-3">
                <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${s.iconColor}`} />
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-stone-900">{rec.title}</p>
                  <p className="mt-0.5 text-xs text-stone-500">
                    {s.label} · {count} source{count === 1 ? "" : "s"}
                  </p>
                  <p className="mt-2 line-clamp-2 text-xs text-stone-600" title={rec.reason}>
                    {rec.reason}
                  </p>
                  {rec.type === "study" ? (
                    <button className="mt-2 text-xs font-medium text-delphi hover:underline">Open task →</button>
                  ) : (
                    <a href={rec.action_target} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-xs font-medium text-delphi hover:underline">
                      Open resource ↗
                    </a>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Floating pieces */}
      <CaptureCard />
      <button className="absolute bottom-6 right-6 flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm text-stone-600 shadow-sm hover:bg-stone-50">
        <Filter className="h-4 w-4" /> Filter
      </button>
    </section>
  );
}