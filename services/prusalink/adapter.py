# PURPOSE: Normalize PrusaLink payloads into telemetry/error schemas.
# DEPENDENCIES: services.collector.prusa_xl_adapter
# MODIFICATION NOTES: v0.1 - Initial PrusaLink adapter.

"""PrusaLink payload adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.collector.prusa_xl_adapter import (
    PrusaXLErrorEvent,
    PrusaXLNormalizedPayload,
    PrusaXLTelemetrySample,
)
from services.prusalink.config import PrusaLinkConfig


class PrusaLinkAdapter:
    """Normalize PrusaLink status/job/info into POC schemas."""

    def __init__(self, config: Optional[PrusaLinkConfig] = None) -> None:
        self.config = config or PrusaLinkConfig()

    def normalize_payload(
        self,
        status: Dict[str, Any],
        job: Optional[Dict[str, Any]] = None,
        info: Optional[Dict[str, Any]] = None,
        http_error: Optional[Dict[str, Any]] = None
    ) -> PrusaXLNormalizedPayload:
        """Build normalized payload from PrusaLink responses."""
        printer = (status or {}).get("printer") or {}
        job_data = (job or status.get("job")) or {}
        errors = self._extract_errors(printer, job_data, http_error)
        telemetry = self._build_telemetry(printer, job_data)
        raw = {"status": status, "job": job_data, "info": info or {}, "http_error": http_error}
        return PrusaXLNormalizedPayload(
            source="prusalink",
            errors=errors,
            telemetry=telemetry,
            raw_payload=raw
        )

    def _build_telemetry(
        self,
        printer: Dict[str, Any],
        job: Dict[str, Any]
    ) -> Optional[PrusaXLTelemetrySample]:
        """Map StatusPrinter + StatusJob to PrusaXLTelemetrySample."""
        state = printer.get("state")
        if state is None and not printer:
            return None

        fan_hotend = printer.get("fan_hotend")
        fan_print = printer.get("fan_print")
        fan_speed_pct = None
        if fan_hotend is not None or fan_print is not None:
            vals = [v for v in (fan_hotend, fan_print) if v is not None]
            fan_speed_pct = max(vals) if vals else None

        job_file = (job.get("file") or {}) if isinstance(job.get("file"), dict) else {}
        job_name = job_file.get("display_name") or job_file.get("name")

        return PrusaXLTelemetrySample(
            sample_time=datetime.now(timezone.utc),
            nozzle_temp_c=printer.get("temp_nozzle"),
            bed_temp_c=printer.get("temp_bed"),
            chamber_temp_c=None,
            fan_speed_pct=fan_speed_pct,
            print_progress_pct=job.get("progress"),
            print_state=state,
            toolhead_id=None,
            job_id=job_name,
            raw_payload={"printer": printer, "job": job}
        )

    def _extract_errors(
        self,
        printer: Dict[str, Any],
        job: Dict[str, Any],
        http_error: Optional[Dict[str, Any]]
    ) -> List[PrusaXLErrorEvent]:
        """Extract error events from printer state, job, or HTTP error."""
        errors: List[PrusaXLErrorEvent] = []
        now = datetime.now(timezone.utc)

        if http_error:
            code = str(http_error.get("code") or "unknown")
            msg = str(http_error.get("title") or http_error.get("text") or "API error")
            raw = dict(http_error)
            if http_error.get("url"):
                raw["url"] = http_error["url"]
            errors.append(PrusaXLErrorEvent(
                error_code=code,
                error_message=msg,
                severity="error",
                subsystem="prusalink",
                event_time=now,
                raw_payload=raw
            ))

        if printer.get("state") == "ERROR":
            status_printer = (printer.get("status_printer") or {}) if isinstance(printer.get("status_printer"), dict) else {}
            status_connect = (printer.get("status_connect") or {}) if isinstance(printer.get("status_connect"), dict) else {}
            msg = status_printer.get("message") or status_connect.get("message") or "Printer in ERROR state"
            if not any(e.error_message == msg for e in errors):
                errors.append(PrusaXLErrorEvent(
                    error_code="printer_error",
                    error_message=msg,
                    severity="error",
                    subsystem="printer",
                    event_time=now,
                    raw_payload={"status_printer": status_printer, "status_connect": status_connect}
                ))

        job_state = job.get("state")
        if job_state == "ERROR":
            msg = "Job in ERROR state"
            if not any(e.error_message == msg for e in errors):
                errors.append(PrusaXLErrorEvent(
                    error_code="job_error",
                    error_message=msg,
                    severity="error",
                    subsystem="job",
                    event_time=now,
                    raw_payload=job
                ))

        return errors
