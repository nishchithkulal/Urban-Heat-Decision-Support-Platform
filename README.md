# HeatPilot AI

AI-powered Urban Heat Decision Support Platform — a production-oriented geospatial
platform for analyzing, predicting, and supporting decisions related to urban heat.

Built as a modular monolith with the intention of extracting true microservices once
domain boundaries are well understood. See `CLAUDE.md` for the full engineering
guidelines, architecture strategy, and roadmap.

## Status

Phase 1 — Backend Foundation.

## Stack

- **Backend:** FastAPI, Python 3.12.13, Pydantic Settings
- **Frontend:** Next.js 16, TypeScript, Tailwind CSS v4 (not yet scaffolded — Phase 5)
- **Database:** PostgreSQL + PostGIS, SQLAlchemy, Alembic (not yet introduced — Phase 2)
- **Runtimes:** managed via [mise](https://mise.jdx.dev/) — see `mise.toml`

## Backend — local development

```bash
mise install                              # installs pinned Python/Node
cd backend
pip install -r requirements-dev.txt
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
cd backend
ruff check .
ruff format --check .
mypy app
pytest -v
```

All four run in CI on every push and pull request (`.github/workflows/ci.yml`).
