# HeatPilot AI

AI-powered Urban Heat Decision Support Platform — a production-oriented geospatial
platform for analyzing, predicting, and supporting decisions related to urban heat.

Built as a modular monolith with the intention of extracting true microservices once
domain boundaries are well understood. See `CLAUDE.md` for the full engineering
guidelines, architecture strategy, and roadmap.

## Status

Phase 8 — Frontend dashboard.

## Stack

- **Backend:** FastAPI, Python 3.12.13, Pydantic Settings
- **Frontend:** Next.js 16, TypeScript, Tailwind CSS v4, App Router
- **Database:** PostgreSQL + PostGIS, SQLAlchemy (async), Alembic
- **Runtimes:** managed via [mise](https://mise.jdx.dev/) — see `mise.toml`

## Backend — local development

```bash
mise install                              # installs pinned Python/Node
docker compose up -d db                   # local PostgreSQL + PostGIS
cd backend
pip install -r requirements-dev.txt
cp .env.example .env                      # adjust if your DB isn't the compose default
alembic upgrade head                      # apply migrations
uvicorn app.main:app --reload
```

The API is served at `http://localhost:8000`:

- `GET /livez` — liveness probe (no dependency checks)
- `GET /readyz` — readiness probe
- `GET /api/v1/...` — versioned application API
- `GET /docs`, `GET /redoc` — interactive API documentation (disabled in production)

Configuration is via environment variables prefixed `HEATPILOT_`. Copy
`backend/.env.example` to `backend/.env` and adjust as needed.

### Testing and quality gates

```bash
docker compose up -d db                   # tests run against a real PostGIS instance
cd backend
ruff check .
ruff format --check .
mypy app
pytest -v
```

All four run in CI on every push and pull request (`.github/workflows/ci.yml`), against
a Postgres+PostGIS service container.

## Frontend — local development

```bash
mise install                              # installs pinned Node
cd frontend
npm install
cp .env.example .env.local                # points at the local backend by default
npm run dev
```

The dashboard is served at `http://localhost:3000` and talks to the backend at
`NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`) — start the backend
first. Pages: dashboard home (API/DB status), `/weather`, `/predictions` (heat risk),
`/locations` (GIS — creating a location requires an admin account), `/login`,
`/register`.

```bash
cd frontend
npm run lint
npx tsc --noEmit
npm run build
```
