#!/usr/bin/env python3
# PURPOSE: Smoke test for PrusaXL_Monitor API.
# DEPENDENCIES: flask, app
# MODIFICATION NOTES: v0.1 - POST /api/troubleshoot sanity check.
# Run: python scripts/smoke_test.py (from repo root)
# Or: FLASK_APP=app:create_app python scripts/smoke_test.py

"""Smoke test: verify /api/troubleshoot returns 200 and valid schema."""

from __future__ import annotations

import json
import os
import sys

# Add repo root to path when run as script
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Use test config for standalone smoke (no Docker)
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("TESTING", "1")


def main() -> int:
    """Run smoke test; return 0 on pass, 1 on fail."""
    from app import create_app
    from app.db import SessionLocal, engine
    from services.knowledge_base.models import Base as KBBase
    from services.troubleshoot.models import Base as TroubleshootBase

    # Create tables for in-memory SQLite
    TroubleshootBase.metadata.create_all(engine)
    KBBase.metadata.create_all(engine)

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": "smoke-test"}),
        content_type="application/json",
    )

    if response.status_code != 200:
        print(f"FAIL: POST /api/troubleshoot returned {response.status_code}", file=sys.stderr)
        print(response.get_data(as_text=True), file=sys.stderr)
        return 1

    data = response.get_json()
    required = ("printer_id", "recent_errors", "kb_matches")
    for key in required:
        if key not in data:
            print(f"FAIL: Response missing key '{key}'", file=sys.stderr)
            return 1

    print("PASS: Smoke test OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
