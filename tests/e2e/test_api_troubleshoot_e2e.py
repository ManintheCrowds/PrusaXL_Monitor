# PURPOSE: E2E tests for /api/troubleshoot endpoint.
# DEPENDENCIES: pytest, flask, app.db (SQLite in-memory for CI)
# MODIFICATION NOTES: v0.1 - Validate 200 and JSON schema.

"""E2E tests for troubleshoot API."""

import json

import pytest


@pytest.mark.e2e
def test_troubleshoot_returns_valid_schema(client) -> None:
    """POST /api/troubleshoot returns 200 with printer_id, recent_errors, kb_matches."""
    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": "prusa-xl-1"}),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["printer_id"] == "prusa-xl-1"
    assert isinstance(data["recent_errors"], list)
    assert isinstance(data["kb_matches"], list)


@pytest.mark.e2e
def test_troubleshoot_with_error_code(client) -> None:
    """POST /api/troubleshoot with error_code returns valid payload."""
    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": "prusa-xl-1", "error_code": "17Y01"}),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "printer_id" in data
    assert "recent_errors" in data
    assert "kb_matches" in data


@pytest.mark.e2e
def test_troubleshoot_with_symptom(client) -> None:
    """POST /api/troubleshoot with symptom returns valid payload."""
    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": "prusa-xl-1", "symptom": "nozzle clog"}),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "printer_id" in data
    assert "kb_matches" in data
