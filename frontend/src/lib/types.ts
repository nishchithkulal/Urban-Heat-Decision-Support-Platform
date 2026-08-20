// Mirrors the backend's Pydantic response schemas (see backend/app/modules/*/schemas.py).
// Kept as plain interfaces, hand-written rather than generated from the OpenAPI schema:
// the API surface is still small enough that a codegen step would be more ceremony
// than it saves right now.

export type Role = "user" | "admin";

export interface UserRead {
  id: string;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface WeatherReading {
  latitude: number;
  longitude: number;
  temperature_c: number;
  humidity_percent: number;
  wind_speed_kph: number;
  weather_code: number;
  observed_at: string;
  provider: string;
}

export type HeatRiskLevel =
  | "low"
  | "caution"
  | "extreme_caution"
  | "danger"
  | "extreme_danger";

export interface PredictionResult {
  latitude: number;
  longitude: number;
  temperature_c: number;
  humidity_percent: number;
  heat_index_c: number;
  risk_level: HeatRiskLevel;
  strategy: string;
  observed_at: string;
}

export interface LocationRead {
  id: string;
  name: string;
  description: string | null;
  latitude: number;
  longitude: number;
  created_at: string;
}

export interface NearbyLocationRead extends LocationRead {
  distance_km: number;
}

// RFC 9457 problem+json, produced by every error response (see
// backend/app/core/errors.py).
export interface ProblemDetail {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  errors?: { field: string; message: string }[];
}
