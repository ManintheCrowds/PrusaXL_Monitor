# PURPOSE: Normalize OctoPrint payloads into telemetry/error schemas.
# DEPENDENCIES: datetime
# MODIFICATION NOTES: v0.1 - Initial OctoPrint adapter.

"""OctoPrint payload adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class OctoPrintAdapter:
    """Normalize OctoPrint printer/job/log data."""

    # PURPOSE: Normalize OctoPrint payloads.
    # DEPENDENCIES: datetime
    # MODIFICATION NOTES: v0.1 - Build telemetry and error lists.
    def normalize_payload(
        self,
        printer: Dict[str, Any],
        job: Dict[str, Any],
        logs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Normalize OctoPrint payload into telemetry + errors."""
        telemetry = self._build_telemetry(printer, job)
        errors = self._extract_errors(logs)
        return {
            "source": "octoprint",
            "telemetry": telemetry,
            "errors": errors,
            "raw_payload": {
                "printer": printer,
                "job": job,
                "logs": logs
            }
        }

    # PURPOSE: Build telemetry object from printer/job payloads.
    # DEPENDENCIES: datetime
    # MODIFICATION NOTES: v0.1 - Map common OctoPrint fields; v0.2 - Multi-tool (Prusa XL).
    def _build_telemetry(self, printer: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """Build telemetry dict from OctoPrint payloads. Supports multi-tool (tool0..tool4)."""
        temps = (printer or {}).get("temperature", {})
        bed = temps.get("bed", {})
        progress = (job or {}).get("progress", {})
        tool_temps: Dict[str, float] = {}
        for key, val in (temps or {}).items():
            if key.startswith("tool") and isinstance(val, dict) and "actual" in val:
                tool_temps[key] = val["actual"]
        tool0 = temps.get("tool0", {})
        nozzle_temp_c = tool0.get("actual") if tool0 else (list(tool_temps.values())[0] if tool_temps else None)
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nozzle_temp_c": nozzle_temp_c,
            "tool_temps": tool_temps if tool_temps else None,
            "nozzle_temps_c": list(tool_temps.values()) if tool_temps else None,
            "bed_temp_c": bed.get("actual"),
            "print_progress_pct": progress.get("completion"),
            "print_state": (printer or {}).get("state", {}).get("text"),
            "job_id": (job or {}).get("job", {}).get("file", {}).get("name")
        }

    # PURPOSE: Extract error-like entries from logs.
    # DEPENDENCIES: datetime
    # MODIFICATION NOTES: v0.1 - Heuristic log filtering.
    def _extract_errors(self, logs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract error events from OctoPrint logs."""
        entries = (logs or {}).get("logs", [])
        errors: List[Dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, str):
                continue
            lower = entry.lower()
            if "error" not in lower and "exception" not in lower:
                continue
            errors.append(
                {
                    "error_code": "octoprint_error",
                    "error_message": entry,
                    "severity": "error",
                    "event_time": datetime.now(timezone.utc).isoformat()
                }
            )
        return errors
