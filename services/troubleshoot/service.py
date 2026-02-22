# PURPOSE: Build troubleshooting responses from device data and KB entries.
# DEPENDENCIES: sqlalchemy, services.knowledge_base.storage, services.troubleshoot.models
# MODIFICATION NOTES: v0.1 - Initial troubleshooting service.

"""Troubleshooting service logic."""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from services.knowledge_base.storage import find_kb_by_error_code, find_kb_by_symptom
from services.troubleshoot.models import PrusaXLErrorEventRecord


def _extract_help_url(event: PrusaXLErrorEventRecord) -> Optional[str]:
    """Extract help.prusa3d.com URL from event raw_payload if present."""
    payload = getattr(event, "raw_payload", None)
    if isinstance(payload, dict) and payload.get("url"):
        return str(payload["url"])
    return None


# PURPOSE: Fetch recent error events for a printer.
# DEPENDENCIES: SQLAlchemy Session
# MODIFICATION NOTES: v0.1 - Limit by count.
def fetch_recent_errors(session: Session, printer_id: str, limit: int = 20) -> List[PrusaXLErrorEventRecord]:
    """Fetch recent error events for a printer."""
    return (
        session.query(PrusaXLErrorEventRecord)
        .filter(PrusaXLErrorEventRecord.printer_id == printer_id)
        .order_by(PrusaXLErrorEventRecord.event_time.desc())
        .limit(limit)
        .all()
    )


# PURPOSE: Build troubleshooting response payload.
# DEPENDENCIES: find_kb_by_error_code, find_kb_by_symptom
# MODIFICATION NOTES: v0.1 - Join error events with KB results.
def build_troubleshoot_payload(
    session: Session,
    printer_id: str,
    error_code: Optional[str] = None,
    symptom: Optional[str] = None
) -> Dict[str, object]:
    """Build troubleshooting payload with errors and KB matches."""
    errors = fetch_recent_errors(session, printer_id)
    kb_matches = []
    if error_code:
        kb_matches.extend(find_kb_by_error_code(session, error_code))
    if symptom:
        kb_matches.extend(find_kb_by_symptom(session, symptom))

    return {
        "printer_id": printer_id,
        "recent_errors": [
            {
                "error_code": e.error_code,
                "error_message": e.error_message,
                "severity": e.severity,
                "subsystem": e.subsystem,
                "event_time": e.event_time.isoformat() if e.event_time else None,
                "help_url": _extract_help_url(e),
            }
            for e in errors
        ],
        "kb_matches": [
            {
                "title": k.title,
                "url": k.url,
                "error_code": k.error_code,
                "symptoms": k.symptoms,
                "guidance": k.guidance
            }
            for k in kb_matches
        ]
    }
