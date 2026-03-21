# PrusaXL_Monitor — Observability and remediation for Prusa XL 3D printing

Identify, monitor, and suggest fixes for Prusa XL print issues. Flask API, PrusaLink/OctoPrint collectors, PostgreSQL, optional Redis/Grafana.

**Python 3.10+** | Flask, SQLAlchemy, PostgreSQL, Alembic, Redis (optional), Flask-Limiter, Flask-Caching

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Observability** | Collect print state, errors, and telemetry from PrusaLink and OctoPrint |
| **Collector** | Read-only data collection from Prusa XL via PrusaLink API and OctoPrint |
| **Knowledge-base seed** | Prusa error codes and troubleshooting patterns stored in PostgreSQL |
| **Troubleshoot pipeline** | Analyze collected data, match against KB, suggest remediation steps |

## Quick start

1. Copy environment: `cp .env.example .env` and edit with your Prusa XL host.
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure PostgreSQL and Redis (optional, for caching) are running.
4. Run the API: `FLASK_APP=app:create_app flask run` or `python -m flask run` (set `FLASK_APP=app:create_app`).

See [docs/prusa_xl_collector_poc.md](docs/prusa_xl_collector_poc.md) for collector configuration and data flow.

## Project structure

- `app/` — Flask app, API, CLI (kb seed, troubleshoot)
- `services/` — PrusaLink, OctoPrint, collector, knowledge_base
- `alembic/` — DB migrations
- `monitoring/` — Grafana dashboards, alerts
- `scripts/` — Smoke test, utilities

## Testing

```bash
pytest tests/ -v
```

**CI** ([`.github/workflows/tests.yml`](.github/workflows/tests.yml)) runs the same suite plus the smoke script:

```bash
python -m pytest tests/ -v --tb=short
python scripts/smoke_test.py
```

(Run from repo root; tests use in-memory SQLite via [`tests/conftest.py`](tests/conftest.py)—no Postgres required in CI.)

Run E2E only: `pytest tests/e2e/ -v -m e2e`  
Smoke test: `python scripts/smoke_test.py`

## Documentation

- [Collector POC](docs/prusa_xl_collector_poc.md) — data sources, PrusaLink, network config, OctoPrint integration
- [OctoPrint XL quirks](docs/octoprint_xl_quirks.md) — known behaviors (absorbing heat, size warning)
- [OpenAPI troubleshoot](docs/openapi_troubleshoot.yaml) — API spec

**Optional components:** Redis (for caching when not in test mode), `monitoring/` (Grafana dashboards).

## KB Seed (Prusa-Error-Codes)

```bash
FLASK_APP=app:create_app flask kb seed-error-codes
```

*Built by a programmer who ships. See [portfolio-harness/docs/AUTHOR.md](../portfolio-harness/docs/AUTHOR.md) if viewing from sibling workspace.*
