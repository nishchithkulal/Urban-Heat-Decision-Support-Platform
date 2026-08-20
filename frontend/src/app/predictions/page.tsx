"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import type { PredictionResult } from "@/lib/types";
import { CoordinateForm } from "@/components/CoordinateForm";
import { DescriptionField } from "@/components/DescriptionField";
import { RiskBadge } from "@/components/RiskBadge";

export default function PredictionsPage() {
  const [latitude, setLatitude] = useState("25.28");
  const [longitude, setLongitude] = useState("51.53");
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);
    setResult(null);
    try {
      const prediction = await api.heatRisk(Number(latitude), Number(longitude));
      setResult(prediction);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="text-xl font-semibold">Heat Risk Prediction</h1>
      <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
        NWS heat-index (or, if enabled on the backend, an ML model) applied to live
        weather conditions.
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

      {result && (
        <div className="mt-6 rounded-lg border border-zinc-200 p-4 dark:border-zinc-800">
          <RiskBadge level={result.risk_level} />
          <dl className="mt-4 grid grid-cols-2 gap-4">
            <DescriptionField label="Heat index" value={`${result.heat_index_c.toFixed(1)} °C`} />
            <DescriptionField label="Temperature" value={`${result.temperature_c.toFixed(1)} °C`} />
            <DescriptionField label="Humidity" value={`${result.humidity_percent.toFixed(0)}%`} />
            <DescriptionField label="Strategy" value={result.strategy} />
          </dl>
        </div>
      )}
    </div>
  );
}
