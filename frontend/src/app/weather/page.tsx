"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import type { WeatherReading } from "@/lib/types";
import { CoordinateForm } from "@/components/CoordinateForm";
import { DescriptionField } from "@/components/DescriptionField";

export default function WeatherPage() {
  const [latitude, setLatitude] = useState("12.97");
  const [longitude, setLongitude] = useState("77.59");
  const [reading, setReading] = useState<WeatherReading | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    setReading(null);
    try {
      const result = await api.currentWeather(Number(latitude), Number(longitude));
      setReading(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-xl font-semibold">Current Weather</h1>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
        Live conditions from Open-Meteo for any coordinate.
      </p>

      <CoordinateForm
        latitude={latitude}
        longitude={longitude}
        onLatitudeChange={setLatitude}
        onLongitudeChange={setLongitude}
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />

      {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}

      {reading && (
        <dl className="mt-6 grid grid-cols-2 gap-4 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
          <DescriptionField label="Temperature" value={`${reading.temperature_c.toFixed(1)} °C`} />
          <DescriptionField label="Humidity" value={`${reading.humidity_percent.toFixed(0)}%`} />
          <DescriptionField label="Wind speed" value={`${reading.wind_speed_kph.toFixed(1)} km/h`} />
          <DescriptionField label="Observed at" value={new Date(reading.observed_at).toLocaleString()} />
          <DescriptionField label="Provider" value={reading.provider} />
        </dl>
      )}
    </div>
  );
}
