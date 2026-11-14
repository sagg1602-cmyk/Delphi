import { PenLine, ImageIcon, Link2, Tag, ArrowRight } from "lucide-react";

export default function CaptureCard() {
  return (
    <div className="absolute bottom-6 left-6 z-10 w-72 rounded-2xl border border-stone-200 bg-white p-4 shadow-lg">
      <div className="flex items-center gap-2 text-sm font-medium text-stone-700">
        <PenLine className="h-4 w-4" />
        Capture a thought…
      </div>
      <textarea
        placeholder="Write a note, idea, or question…"
        className="mt-3 h-16 w-full resize-none rounded-lg border border-stone-200 p-2 text-xs outline-none focus:border-delphi"
      />
      <div className="mt-2 flex items-center justify-between text-stone-400">
        <div className="flex gap-3">
          <ImageIcon className="h-4 w-4 cursor-pointer hover:text-stone-600" />
          <Link2 className="h-4 w-4 cursor-pointer hover:text-stone-600" />
          <Tag className="h-4 w-4 cursor-pointer hover:text-stone-600" />
        </div>
        <button className="rounded-lg bg-delphi p-1.5 text-white hover:opacity-90">
          <ArrowRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}