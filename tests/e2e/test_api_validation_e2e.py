# PURPOSE: E2E tests for /api/troubleshoot validation (400 responses).
# DEPENDENCIES: pytest, flask
# MODIFICATION NOTES: v0.1 - Validate 400 for invalid payloads.

"""E2E tests for troubleshoot API validation."""

import json

import pytest


@pytest.mark.e2e
def test_troubleshoot_400_missing_printer_id(client) -> None:
    """POST /api/troubleshoot without printer_id returns 400."""
    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({}),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data.get("error") == "invalid_request"
    assert "details" in data


@pytest.mark.e2e
def test_troubleshoot_400_empty_printer_id(client) -> None:
    """POST /api/troubleshoot with empty printer_id returns 400."""
    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": ""}),
        content_type="application/json"
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


@pytest.mark.e2e
def test_troubleshoot_400_invalid_json(client) -> None:
    """POST /api/troubleshoot with invalid JSON returns 400."""
    response = client.post(
        "/api/troubleshoot",
        data="not json",
        content_type="application/json"
    )

    assert response.status_code == 400
