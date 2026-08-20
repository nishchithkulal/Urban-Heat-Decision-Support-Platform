import Link from "next/link";
import { api, ApiError } from "@/lib/api";

// A Server Component: this fetch runs on the Next.js server at request time, not in
// the browser, so it needs no client-side JS and isn't subject to browser CORS at
// all (server-to-server). The interactive pages (weather/predictions/locations) are
// Client Components instead, since they need state (form input, auth token) that
// only exists in the browser.
async function getStatus(check: () => Promise<{ status: string }>) {
  try {
    const result = await check();
    return { ok: true as const, status: result.status };
  } catch (error) {
    const message = error instanceof ApiError ? error.message : "unreachable";
    return { ok: false as const, status: message };
  }
}

const CARDS = [
  { href: "/weather", title: "Weather", description: "Current conditions at any point." },
  { href: "/predictions", title: "Heat Risk", description: "NWS heat-index and ML-based risk prediction." },
  { href: "/locations", title: "Locations", description: "Registered monitoring points and spatial search." },
];

export default async function DashboardPage() {
  const [live, ready] = await Promise.all([getStatus(api.livez), getStatus(api.readyz)]);

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">HeatPilot AI</h1>
        <p className="mt-1 text-zinc-600 dark:text-zinc-400">
          AI-powered Urban Heat Decision Support Platform.
        </p>
      </div>

      <div className="flex gap-4">
        <StatusPill label="API" ok={live.ok} detail={live.status} />
        <StatusPill label="Database" ok={ready.ok} detail={ready.status} />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        {CARDS.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-lg border border-zinc-200 p-4 transition-colors hover:border-zinc-400 dark:border-zinc-800 dark:hover:border-zinc-600"
          >
            <h2 className="font-medium">{card.title}</h2>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{card.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

function StatusPill({ label, ok, detail }: { label: string; ok: boolean; detail: string }) {
  return (
    <div className="flex items-center gap-2 rounded-full border border-zinc-200 px-3 py-1.5 text-sm dark:border-zinc-800">
      <span className={`h-2 w-2 rounded-full ${ok ? "bg-emerald-500" : "bg-red-500"}`} />
      <span className="font-medium">{label}</span>
      <span className="text-zinc-500 dark:text-zinc-400">{detail}</span>
    </div>
  );
}
