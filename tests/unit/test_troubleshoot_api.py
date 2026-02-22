# PURPOSE: Validate troubleshooting API endpoint behavior.
# DEPENDENCIES: pytest, flask
# MODIFICATION NOTES: v0.1 - Basic endpoint test; v0.2 - Use client fixture, assert 200.

"""Tests for troubleshooting API endpoint."""

import json


def test_troubleshoot_endpoint_returns_payload(client) -> None:
    """Ensure troubleshooting endpoint returns 200 and valid JSON for valid requests."""
    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": "prusa-xl-1", "error_code": "E001"}),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert "printer_id" in data
    assert "recent_errors" in data
    assert "kb_matches" in data
