"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/weather", label: "Weather" },
  { href: "/predictions", label: "Heat Risk" },
  { href: "/locations", label: "Locations" },
];

export function NavBar() {
  const { user, isLoading, logout } = useAuth();

  return (
    <nav className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 dark:border-zinc-800">
      <div className="flex items-center gap-6">
        <span className="text-sm font-semibold tracking-tight">HeatPilot AI</span>
        <div className="flex gap-4 text-sm text-zinc-600 dark:text-zinc-400">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="hover:text-zinc-950 dark:hover:text-zinc-50">
              {link.label}
            </Link>
          ))}
        </div>
      </div>
      <div className="text-sm">
        {isLoading ? null : user ? (
          <div className="flex items-center gap-3">
            <span className="text-zinc-500 dark:text-zinc-400">
              {user.email} ({user.role})
            </span>
            <button
              onClick={logout}
              className="rounded border border-zinc-300 px-3 py-1 hover:bg-zinc-100 dark:border-zinc-700 dark:hover:bg-zinc-900"
            >
              Log out
            </button>
          </div>
        ) : (
          <div className="flex gap-3">
            <Link href="/login" className="hover:underline">
              Log in
            </Link>
            <Link href="/register" className="hover:underline">
              Register
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
}
