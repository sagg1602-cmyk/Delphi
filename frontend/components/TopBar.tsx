"use client";

import { useEffect, useState } from "react";
import { Search, Bell } from "lucide-react";

const userName = "Miya"; // Replace with the signed-in user once auth exists

export default function TopBar() {
  const [greeting, setGreeting] = useState("Welcome back");

  // Runs in the browser, so it uses the user's local time
  useEffect(() => {
    const hour = new Date().getHours();
    setGreeting(hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening");
  }, []);

  return (
    <header className="flex gap-4">
      <div className="rounded-2xl border border-stone-200 bg-white px-6 py-4">
        <h1 className="text-3xl font-semibold tracking-tight text-stone-900">
          {greeting}, <span className="font-normal">{userName}</span>
        </h1>
      </div>

      <div className="flex flex-1 items-center gap-4 rounded-2xl border border-stone-200 bg-white px-4">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-stone-200 px-3 py-2.5 text-sm text-stone-400">
          <Search className="h-4 w-4" />
          <span className="flex-1">Search notes, topics, or ask Delphi…</span>
          <kbd className="rounded border border-stone-200 px-1.5 text-xs">⌘K</kbd>
        </div>
        <Bell className="h-5 w-5 text-stone-500" />
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-delphi text-sm font-semibold text-white">
          M
        </div>
      </div>
    </header>
  );
}