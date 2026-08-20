"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import type { LocationRead } from "@/lib/types";
import { useAuth } from "@/lib/auth-context";

export default function LocationsPage() {
  const { user, accessToken } = useAuth();
  const [locations, setLocations] = useState<LocationRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function reload() {
    setIsLoading(true);
    try {
      setLocations(await api.listLocations());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    // Deferred via microtask -- see the identical comment in auth-context.tsx for
    // why a direct `reload()` call here trips react-hooks/set-state-in-effect.
    queueMicrotask(reload);
  }, []);

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="text-xl font-semibold">Locations</h1>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
        Registered monitoring points. Creating a location requires an admin account.
      </p>

      {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}

      {isLoading ? (
        <p className="mt-6 text-sm text-zinc-500">Loading…</p>
      ) : locations.length === 0 ? (
        <p className="mt-6 text-sm text-zinc-500">No locations registered yet.</p>
      ) : (
        <ul className="mt-6 flex flex-col gap-2">
          {locations.map((location) => (
            <li
              key={location.id}
              className="rounded-lg border border-zinc-200 p-3 dark:border-zinc-800"
            >
              <p className="font-medium">{location.name}</p>
              {location.description && (
                <p className="text-sm text-zinc-600 dark:text-zinc-400">{location.description}</p>
              )}
              <p className="mt-1 text-xs text-zinc-500">
                {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
              </p>
            </li>
          ))}
        </ul>
      )}

      {user?.role === "admin" && accessToken && (
        <CreateLocationForm accessToken={accessToken} onCreated={reload} />
      )}
    </div>
  );
}

function CreateLocationForm({
  accessToken,
  onCreated,
}: {
  accessToken: string;
  onCreated: () => void;
}) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await api.createLocation(accessToken, {
        name,
        description: description || undefined,
        latitude: Number(latitude),
        longitude: Number(longitude),
      });
      setName("");
      setDescription("");
      setLatitude("");
      setLongitude("");
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-8 flex flex-col gap-3 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800"
    >
      <h2 className="text-sm font-medium">Register a new location</h2>
      <input
        placeholder="Name"
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="rounded border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
      />
      <input
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        className="rounded border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
      />
      <div className="flex gap-3">
        <input
          type="number"
          step="any"
          min={-90}
          max={90}
          placeholder="Latitude"
          required
          value={latitude}
          onChange={(e) => setLatitude(e.target.value)}
          className="w-full rounded border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
        />
        <input
          type="number"
          step="any"
          min={-180}
          max={180}
          placeholder="Longitude"
          required
          value={longitude}
          onChange={(e) => setLongitude(e.target.value)}
          className="w-full rounded border border-zinc-300 px-3 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900"
        />
      </div>
      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}
      <button
        type="submit"
        disabled={isSubmitting}
        className="self-start rounded bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900"
      >
        {isSubmitting ? "Creating…" : "Create location"}
      </button>
    </form>
  );
}
