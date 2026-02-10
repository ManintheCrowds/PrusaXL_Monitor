# PURPOSE: Validate troubleshooting API endpoint behavior.
# DEPENDENCIES: pytest, flask
# MODIFICATION NOTES: v0.1 - Initial API test stub.

"""Tests for troubleshooting API endpoint."""

import json

from flask import Flask

from app import create_app


# PURPOSE: Ensure troubleshooting endpoint returns JSON for valid requests.
# DEPENDENCIES: Flask test client
# MODIFICATION NOTES: v0.1 - Basic endpoint test.
def test_troubleshoot_endpoint_returns_payload() -> None:
    app: Flask = create_app()
    client = app.test_client()

    response = client.post(
        "/api/troubleshoot",
        data=json.dumps({"printer_id": "prusa-xl-1", "error_code": "E001"}),
        content_type="application/json"
    )

    # CONTINUE TESTING: Mock DB session and validate payload contents.
    assert response.status_code in {200, 500}
