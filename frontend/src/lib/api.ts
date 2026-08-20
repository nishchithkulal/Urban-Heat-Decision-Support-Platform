import type {
  LocationRead,
  NearbyLocationRead,
  PredictionResult,
  ProblemDetail,
  TokenPair,
  UserRead,
  WeatherReading,
} from "./types";

// Server Components (dashboard home) and Client Components (interactive forms) both
// call this file directly against the backend rather than through Next.js API
// routes/rewrites -- there is no server-side secret to hide (the backend has its own
// auth), so a proxy layer would only add latency and a second place for errors to
// hide.
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  accessToken?: string | null;
  // Form-encoded bodies (OAuth2PasswordRequestForm on /auth/login) instead of JSON.
  form?: boolean;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {};
  let body: BodyInit | undefined;

  if (options.body !== undefined) {
    if (options.form) {
      headers["Content-Type"] = "application/x-www-form-urlencoded";
      body = new URLSearchParams(options.body as Record<string, string>).toString();
    } else {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(options.body);
    }
  }

  if (options.accessToken) {
    headers.Authorization = `Bearer ${options.accessToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body,
    cache: "no-store",
  });

  if (!response.ok) {
    const problem = (await response.json().catch(() => null)) as ProblemDetail | null;
    throw new ApiError(response.status, problem?.detail ?? response.statusText);
  }

  return response.json() as Promise<T>;
}

export interface HealthStatus {
  status: string;
}

export const api = {
  livez: () => request<HealthStatus>("/livez"),
  readyz: () => request<HealthStatus>("/readyz"),

  register: (email: string, password: string) =>
    request<UserRead>("/api/v1/auth/register", {
      method: "POST",
      body: { email, password },
    }),

  login: (email: string, password: string) =>
    request<TokenPair>("/api/v1/auth/login", {
      method: "POST",
      body: { username: email, password },
      form: true,
    }),

  refresh: (refreshToken: string) =>
    request<TokenPair>("/api/v1/auth/refresh", {
      method: "POST",
      body: { refresh_token: refreshToken },
    }),

  me: (accessToken: string) =>
    request<UserRead>("/api/v1/auth/me", { accessToken }),

  currentWeather: (latitude: number, longitude: number) =>
    request<WeatherReading>(
      `/api/v1/weather/current?latitude=${latitude}&longitude=${longitude}`,
    ),

  heatRisk: (latitude: number, longitude: number) =>
    request<PredictionResult>(
      `/api/v1/predictions/heat-risk?latitude=${latitude}&longitude=${longitude}`,
    ),

  listLocations: () => request<LocationRead[]>("/api/v1/gis/locations"),

  nearbyLocations: (latitude: number, longitude: number, radiusKm: number) =>
    request<NearbyLocationRead[]>(
      `/api/v1/gis/locations/nearby?latitude=${latitude}&longitude=${longitude}&radius_km=${radiusKm}`,
    ),

  createLocation: (
    accessToken: string,
    payload: { name: string; description?: string; latitude: number; longitude: number },
  ) =>
    request<LocationRead>("/api/v1/gis/locations", {
      method: "POST",
      body: payload,
      accessToken,
    }),
};
