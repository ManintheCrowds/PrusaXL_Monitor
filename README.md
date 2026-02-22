# PrusaXL_Monitor

Seeking to identify, monitor and suggest fixes on Prusa XL 3d Printing.

**Python 3.10+** | Flask, SQLAlchemy, PostgreSQL, Alembic

## Quick start

1. Copy environment: `cp .env.example .env` and edit with your Prusa XL host.
2. Install dependencies (Flask, SQLAlchemy, etc.) and ensure PostgreSQL is running.
3. Run the API: `FLASK_APP=app:create_app flask run` or `python -m flask run` (set `FLASK_APP=app:create_app`).

See [docs/prusa_xl_collector_poc.md](docs/prusa_xl_collector_poc.md) for collector configuration and data flow.

## Testing

```bash
pytest tests/ -v
```

Run E2E only: `pytest tests/e2e/ -v -m e2e`  
Smoke test: `python scripts/smoke_test.py`

## Documentation

- [Collector POC](docs/prusa_xl_collector_poc.md) — data sources, PrusaLink, network config, OctoPrint integration
- [OctoPrint XL quirks](docs/octoprint_xl_quirks.md) — known behaviors (absorbing heat, size warning)
- [OpenAPI troubleshoot](docs/openapi_troubleshoot.yaml) — API spec

## KB Seed (Prusa-Error-Codes)

```bash
FLASK_APP=app:create_app flask kb seed-error-codes
```
