import type { FormEvent, ReactNode } from "react";

export function CoordinateForm({
  latitude,
  longitude,
  onLatitudeChange,
  onLongitudeChange,
  onSubmit,
  isLoading,
  extra,
}: {
  latitude: string;
  longitude: string;
  onLatitudeChange: (value: string) => void;
  onLongitudeChange: (value: string) => void;
  onSubmit: (event: FormEvent) => void;
  isLoading: boolean;
  extra?: ReactNode;
}) {
  return (
    <form onSubmit={onSubmit} className="mt-6 flex flex-wrap items-end gap-3">
      <label className="flex flex-col gap-1 text-sm">
        Latitude
        <input
          type="number"
          step="any"
          min={-90}
          max={90}
          required
          value={latitude}
          onChange={(e) => onLatitudeChange(e.target.value)}
          className="w-32 rounded border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900"
        />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        Longitude
        <input
          type="number"
          step="any"
          min={-180}
          max={180}
          required
          value={longitude}
          onChange={(e) => onLongitudeChange(e.target.value)}
          className="w-32 rounded border border-zinc-300 px-3 py-2 dark:border-zinc-700 dark:bg-zinc-900"
        />
      </label>
      {extra}
      <button
        type="submit"
        disabled={isLoading}
        className="rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
      >
        {isLoading ? "Loading…" : "Look up"}
      </button>
    </form>
  );
}
