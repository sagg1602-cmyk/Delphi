"use client";

import { useState } from "react";
import Link from "next/link";
import {
  BookOpen, Compass, Sparkles, Share2, List, LayoutGrid, Filter,
  RefreshCw, CircleAlert, ChevronDown, LoaderCircle,
} from "lucide-react";
import type { Evidence, Recommendation } from "@/lib/types";
import CaptureCard from "@/components/CaptureCard";

// Layout knobs: tweak these if cards overlap on your screen (all values are % of the map area)
const CENTER = { x: 50, y: 50 };
const NODE_DISTANCE = { x: 28, y: 26 };      // how far cards sit from the center
const EVIDENCE_DISTANCE = { x: 18, y: 20 };  // how far evidence dots sit from their card

const typeStyles = {
  study: {
    icon: BookOpen, label: "Study",
    card: "bg-indigo-50 border-indigo-200", iconColor: "text-indigo-600", dot: "bg-indigo-400",
  },
  discovery: {
    icon: Compass, label: "Discover",
    card: "bg-emerald-50 border-emerald-200", iconColor: "text-emerald-600", dot: "bg-emerald-400",
  },
};

// Colors for the evidence type chips in "Why this?"
const evidenceChip: Record<string, string> = {
  task: "bg-indigo-100 text-indigo-700",
  note: "bg-amber-100 text-amber-800",
  interest: "bg-pink-100 text-pink-700",
  resource: "bg-emerald-100 text-emerald-700",
};

// Places each recommendation around the center, and its evidence around it
function layout(recs: Recommendation[]) {
  return recs.map((rec, i) => {
    const angle = Math.PI + 0.4 + (i * 2 * Math.PI) / recs.length;
    const x = CENTER.x + NODE_DISTANCE.x * Math.cos(angle);
    const y = CENTER.y + NODE_DISTANCE.y * Math.sin(angle);

    const evidence = rec.evidence.map((item, j) => {
      const spread = (j - (rec.evidence.length - 1) / 2) * 0.9;
      const a = angle + spread;
      return {
        item,
        x: x + EVIDENCE_DISTANCE.x * Math.cos(a),
        y: y + EVIDENCE_DISTANCE.y * Math.sin(a),
      };
    });

    return { rec, x, y, evidence, key: rec.id };
  });
}

interface KnowledgeMapProps {
  status: "loading" | "success" | "error";
  recs: Recommendation[];
  errorMessage?: string;
  onRefresh: () => void;
  isSample: boolean;
}

export default function KnowledgeMap({ status, recs, errorMessage, onRefresh, isSample }: KnowledgeMapProps) {
  // While reloading, keep showing the last cards so the map doesn't flash
  const nodes = status === "error" ? [] : layout(recs);
  const isLoading = status === "loading";
  const isFirstLoad = isLoading && recs.length === 0;

  return (
    <section className="relative flex min-h-[600px] flex-1 flex-col rounded-2xl border border-stone-200 bg-white p-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-semibold tracking-tight">Your space, connected.</h2>
            {isSample && (
              <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-800">
                Sample data
              </span>
            )}
          </div>
          <p className="text-sm text-stone-500">A visual map of your ideas, notes, and goals.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="flex items-center gap-1.5 rounded-xl border border-stone-200 px-3 py-2 text-sm text-stone-600 hover:bg-stone-50 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
          <div className="flex rounded-xl bg-stone-100 p-1 text-sm">
            <span className="flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 font-medium shadow-sm">
              <Share2 className="h-4 w-4 text-delphi" /> Graph
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 text-stone-400" title="Coming soon">
              <List className="h-4 w-4" /> List
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 text-stone-400" title="Coming soon">
              <LayoutGrid className="h-4 w-4" /> Canvas
            </span>
          </div>
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
            <g key={n.key}>
              <line x1={`${CENTER.x}%`} y1={`${CENTER.y}%`} x2={`${n.x}%`} y2={`${n.y}%`} stroke="#a5a3f0" strokeWidth="1.5" />
              {n.evidence.map((e) => (
                <line key={e.item.id} x1={`${n.x}%`} y1={`${n.y}%`} x2={`${e.x}%`} y2={`${e.y}%`} stroke="#d6d3d1" strokeWidth="1" />
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
            {isLoading ? (
              <LoaderCircle className="h-6 w-6 animate-spin text-delphi" />
            ) : (
              <Sparkles className="h-6 w-6 text-delphi" />
            )}
            <div>
              <p className="text-lg font-semibold text-stone-900">Today</p>
              <p className="text-xs text-stone-500">
                {isFirstLoad
                  ? "Finding suggestions…"
                  : status === "error"
                    ? "Couldn't load"
                    : `${recs.length} recommendation${recs.length === 1 ? "" : "s"}`}
              </p>
            </div>
          </div>
        </div>

        {/* Empty state */}
        {status === "success" && recs.length === 0 && (
          <div className="absolute left-1/2 top-[64%] -translate-x-1/2 text-center">
            <p className="text-sm text-stone-600">Add a task or interest to get suggestions</p>
            <Link href="/tasks" className="mt-2 inline-block text-sm font-medium text-delphi hover:underline">
              Add a task →
            </Link>
          </div>
        )}

        {/* Error state with retry */}
        {status === "error" && (
          <div className="absolute left-1/2 top-[66%] w-80 -translate-x-1/2 rounded-xl border border-red-200 bg-red-50 p-4 text-center">
            <CircleAlert className="mx-auto h-5 w-5 text-red-500" />
            <p className="mt-2 text-sm text-red-800">{errorMessage ?? "Couldn't load recommendations."}</p>
            <button
              onClick={onRefresh}
              className="mt-3 rounded-lg bg-red-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-red-700"
            >
              Try again
            </button>
          </div>
        )}

        {/* Evidence dots */}
        {nodes.flatMap((n) =>
          n.evidence.map((e) => (
            <div
              key={`${n.key}-${e.item.id}`}
              className="absolute flex max-w-40 -translate-x-1/2 -translate-y-1/2 items-center gap-1.5 text-[11px] text-stone-500"
              style={{ left: `${e.x}%`, top: `${e.y}%` }}
              title={`${e.item.type}: ${e.item.label}`}
            >
              <span className={`h-2 w-2 shrink-0 rounded-full ${typeStyles[n.rec.type].dot}`} />
              <span className="truncate">{e.item.label}</span>
            </div>
          ))
        )}

        {/* Recommendation cards */}
        {nodes.map(({ rec, x, y, key }) => (
          <RecommendationNode key={key} rec={rec} x={x} y={y} />
        ))}
      </div>

      {/* Floating pieces */}
      <CaptureCard />
      <button className="absolute bottom-6 right-6 flex items-center gap-2 rounded-xl border border-stone-200 bg-white px-4 py-2 text-sm text-stone-600 shadow-sm hover:bg-stone-50">
        <Filter className="h-4 w-4" /> Filter
      </button>
    </section>
  );
}

/* ---------- One recommendation card on the map ---------- */

function RecommendationNode({ rec, x, y }: { rec: Recommendation; x: number; y: number }) {
  const [showWhy, setShowWhy] = useState(false);
  const s = typeStyles[rec.type];
  const Icon = s.icon;
  const count = rec.evidence.length;

  return (
    <div
      className={`absolute w-72 -translate-x-1/2 -translate-y-1/2 rounded-2xl border px-4 py-3 shadow-sm transition hover:shadow-md ${s.card} ${showWhy ? "z-20" : "z-10"}`}
      style={{ left: `${x}%`, top: `${y}%` }}
    >
      <div className="flex items-start gap-3">
        <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${s.iconColor}`} />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-semibold text-stone-900">{rec.title}</p>
          <p className="mt-0.5 text-xs text-stone-500">
            {s.label}
            {rec.estimated_minutes ? ` · ${rec.estimated_minutes} min` : ""} · {count} source{count === 1 ? "" : "s"}
          </p>
          <p className={`mt-2 text-xs text-stone-600 ${showWhy ? "" : "line-clamp-2"}`}>{rec.reason}</p>

          <div className="mt-2 flex items-center justify-between">
            {rec.action.type === "open_task" ? (
              <Link href="/tasks" className="text-xs font-medium text-delphi hover:underline">
                Open task →
              </Link>
            ) : (
              <a
                href={rec.action.target}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs font-medium text-delphi hover:underline"
              >
                Open resource ↗
              </a>
            )}
            <button
              onClick={() => setShowWhy((open) => !open)}
              aria-expanded={showWhy}
              className="flex items-center gap-1 text-xs text-stone-500 hover:text-stone-800"
            >
              Why this?
              <ChevronDown className={`h-3.5 w-3.5 transition ${showWhy ? "rotate-180" : ""}`} />
            </button>
          </div>

          {showWhy && <WhyThisPanel evidence={rec.evidence} />}
        </div>
      </div>
    </div>
  );
}

/* ---------- "Why this?" list of evidence ---------- */

function WhyThisPanel({ evidence }: { evidence: Evidence[] }) {
  return (
    <div className="mt-3 rounded-xl border border-stone-200 bg-white p-3">
      <p className="text-[11px] font-medium uppercase tracking-wide text-stone-400">Based on</p>
      {evidence.length === 0 ? (
        <p className="mt-1 text-xs text-stone-500">No evidence was sent with this suggestion.</p>
      ) : (
        <ul className="mt-2 space-y-1.5">
          {evidence.map((item) => (
            <li key={item.id} className="flex items-center gap-2 text-xs text-stone-700">
              <span
                className={`shrink-0 rounded-md px-1.5 py-0.5 text-[10px] font-semibold uppercase ${
                  evidenceChip[item.type] ?? "bg-stone-100 text-stone-600"
                }`}
              >
                {item.type}
              </span>
              <span className="truncate" title={item.label}>{item.label}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
