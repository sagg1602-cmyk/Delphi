"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { House, FileText, Share2, Compass, SquareCheck, Landmark } from "lucide-react";

const navItems = [
  { href: "/", label: "Home", icon: House },
  { href: "/notes", label: "My Notes", icon: FileText },
  { href: "/map", label: "Knowledge Map", icon: Share2 },
  { href: "/discover", label: "Discover", icon: Compass },
  { href: "/tasks", label: "Tasks", icon: SquareCheck },
];

const vaults = [
  { name: "School", color: "bg-blue-500" },
  { name: "Research", color: "bg-violet-500" },
  { name: "Personal", color: "bg-emerald-500" },
  { name: "Ideas", color: "bg-orange-400" },
  { name: "Archive", color: "bg-stone-400" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-20 shrink-0 flex-col items-center border-r border-stone-200 bg-white py-6">
      <Landmark className="h-8 w-8 text-stone-800" />

      <nav className="mt-10 flex flex-col gap-2">
        {navItems.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              title={label}
              className={`flex h-11 w-11 items-center justify-center rounded-xl transition ${
                active
                  ? "bg-delphi-light text-delphi"
                  : "text-stone-500 hover:bg-stone-100 hover:text-stone-800"
              }`}
            >
              <Icon className="h-5 w-5" />
            </Link>
          );
        })}
      </nav>

      <div className="mt-8 w-10 border-t border-stone-200" />

      <p className="mt-6 text-[10px] font-medium uppercase tracking-wider text-stone-400">Vaults</p>
      <div className="mt-3 flex flex-col items-center gap-3">
        {vaults.map((v) => (
          <span
            key={v.name}
            title={v.name}
            className={`h-3.5 w-3.5 cursor-pointer rounded-full ${v.color} transition hover:scale-125`}
          />
        ))}
      </div>
    </aside>
  );
}