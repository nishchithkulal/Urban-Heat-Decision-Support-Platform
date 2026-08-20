import type { HeatRiskLevel } from "@/lib/types";

// Matches the NWS heat-index risk categories the backend classifies into (see
// backend/app/modules/prediction/heat_index.py). Colors loosely follow NWS's own
// heat-index chart conventions (green -> yellow -> orange -> red) for anyone already
// familiar with it.
const STYLES: Record<HeatRiskLevel, { label: string; className: string }> = {
  low: { label: "Low", className: "bg-emerald-100 text-emerald-900 dark:bg-emerald-900/40 dark:text-emerald-200" },
  caution: { label: "Caution", className: "bg-yellow-100 text-yellow-900 dark:bg-yellow-900/40 dark:text-yellow-200" },
  extreme_caution: { label: "Extreme Caution", className: "bg-amber-200 text-amber-950 dark:bg-amber-900/50 dark:text-amber-200" },
  danger: { label: "Danger", className: "bg-orange-200 text-orange-950 dark:bg-orange-900/50 dark:text-orange-200" },
  extreme_danger: { label: "Extreme Danger", className: "bg-red-200 text-red-950 dark:bg-red-900/50 dark:text-red-200" },
};

export function RiskBadge({ level }: { level: HeatRiskLevel }) {
  const style = STYLES[level];
  return (
    <span className={`inline-block rounded-full px-3 py-1 text-sm font-medium ${style.className}`}>
      {style.label}
    </span>
  );
}
