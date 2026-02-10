# PURPOSE: Troubleshooting API endpoint for Prusa XL diagnostics.
# DEPENDENCIES: flask, pydantic, app.db, services.troubleshoot.service
# MODIFICATION NOTES: v0.1 - Initial troubleshoot endpoint.

"""Troubleshooting API endpoints."""

from __future__ import annotations

from typing import Optional

from flask import Blueprint, jsonify, request
from pydantic import BaseModel, Field, ValidationError

from app.db import get_db
from services.troubleshoot.service import build_troubleshoot_payload

troubleshoot_bp = Blueprint("troubleshoot", __name__)


class TroubleshootRequest(BaseModel):
    """Troubleshoot request payload."""

    printer_id: str = Field(..., min_length=1)
    error_code: Optional[str] = None
    symptom: Optional[str] = None


# PURPOSE: Handle troubleshooting lookup requests.
# DEPENDENCIES: build_troubleshoot_payload, pydantic validation
# MODIFICATION NOTES: v0.1 - Validate request and return KB matches.
@troubleshoot_bp.route("/troubleshoot", methods=["POST"])
def troubleshoot_lookup():
    """Return troubleshooting guidance for a printer."""
    try:
        payload = TroubleshootRequest.model_validate(request.get_json() or {})
    except ValidationError as exc:
        return jsonify({"error": "invalid_request", "details": exc.errors()}), 400

    session = next(get_db())
    try:
        result = build_troubleshoot_payload(
            session=session,
            printer_id=payload.printer_id,
            error_code=payload.error_code,
            symptom=payload.symptom
        )
        return jsonify(result)
    finally:
        session.close()
