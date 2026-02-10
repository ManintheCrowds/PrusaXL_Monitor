# PURPOSE: Normalize Prusa XL diagnostics payloads into POC schemas.
# DEPENDENCIES: pydantic, datetime, services.collector.config.PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Initial normalization adapter for collector POC.

"""Prusa XL collector adapter and normalization utilities."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from services.collector.config import PrusaXLCollectorConfig

logger = logging.getLogger(__name__)


class PrusaXLErrorEvent(BaseModel):
    """Normalized Prusa XL error event."""

    error_code: str
    error_message: str
    severity: str = "unknown"
    subsystem: Optional[str] = None
    event_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = Field(default_factory=dict)

    # PURPOSE: Validate string fields for error events.
    # DEPENDENCIES: pydantic.field_validator
    # MODIFICATION NOTES: v0.1 - Prevent empty error fields.
    @field_validator("error_code", "error_message", "severity")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        """Ensure key string fields are non-empty."""
        if not value or value.strip() == "":
            raise ValueError("error event fields cannot be empty")
        return value


class PrusaXLTelemetrySample(BaseModel):
    """Normalized Prusa XL telemetry sample."""

    sample_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    nozzle_temp_c: Optional[float] = None
    bed_temp_c: Optional[float] = None
    chamber_temp_c: Optional[float] = None
    fan_speed_pct: Optional[float] = None
    print_progress_pct: Optional[float] = None
    print_state: Optional[str] = None
    toolhead_id: Optional[str] = None
    job_id: Optional[str] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)

    # PURPOSE: Normalize percentage values to 0-100.
    # DEPENDENCIES: pydantic.field_validator
    # MODIFICATION NOTES: v0.1 - Clamp percentage fields.
    @field_validator("fan_speed_pct", "print_progress_pct")
    @classmethod
    def clamp_percentages(cls, value: Optional[float]) -> Optional[float]:
        """Clamp percentage fields to 0-100 if provided."""
        if value is None:
            return value
        return max(0.0, min(100.0, float(value)))


class PrusaXLNormalizedPayload(BaseModel):
    """Normalized payload output from the adapter."""

    source: str
    errors: List[PrusaXLErrorEvent] = Field(default_factory=list)
    telemetry: Optional[PrusaXLTelemetrySample] = None
    raw_payload: Dict[str, Any] = Field(default_factory=dict)


class PrusaXLAdapter:
    """Adapter for normalizing Prusa XL payloads."""

    # PURPOSE: Initialize the Prusa XL adapter with config.
    # DEPENDENCIES: PrusaXLCollectorConfig
    # MODIFICATION NOTES: v0.1 - Accept optional config input.
    def __init__(self, config: Optional[PrusaXLCollectorConfig] = None) -> None:
        self.config = config or PrusaXLCollectorConfig()

    # PURPOSE: Normalize a raw payload into POC schemas.
    # DEPENDENCIES: PrusaXLErrorEvent, PrusaXLTelemetrySample
    # MODIFICATION NOTES: v0.1 - Basic normalization for errors and telemetry.
    def normalize_payload(self, payload: Dict[str, Any], source: str = "unknown") -> PrusaXLNormalizedPayload:
        """Normalize a raw payload dict into events and telemetry."""
        errors = self._parse_errors(payload)
        telemetry = self._parse_telemetry(payload)
        return PrusaXLNormalizedPayload(
            source=source,
            errors=errors,
            telemetry=telemetry,
            raw_payload=payload
        )

    # PURPOSE: Build a database-ready row for an error event.
    # DEPENDENCIES: PrusaXLErrorEvent
    # MODIFICATION NOTES: v0.1 - Convert event to row dict.
    def build_error_row(self, event: PrusaXLErrorEvent) -> Dict[str, Any]:
        """Convert a normalized error event to a DB row dict."""
        return {
            "printer_id": self.config.printer_id,
            "error_code": event.error_code,
            "error_message": event.error_message,
            "severity": event.severity,
            "subsystem": event.subsystem,
            "event_time": event.event_time,
            "raw_payload": event.raw_payload
        }

    # PURPOSE: Build a database-ready row for a telemetry sample.
    # DEPENDENCIES: PrusaXLTelemetrySample
    # MODIFICATION NOTES: v0.1 - Convert telemetry to row dict.
    def build_telemetry_row(self, sample: PrusaXLTelemetrySample) -> Dict[str, Any]:
        """Convert a normalized telemetry sample to a DB row dict."""
        return {
            "printer_id": self.config.printer_id,
            "sample_time": sample.sample_time,
            "nozzle_temp_c": sample.nozzle_temp_c,
            "bed_temp_c": sample.bed_temp_c,
            "chamber_temp_c": sample.chamber_temp_c,
            "fan_speed_pct": sample.fan_speed_pct,
            "print_progress_pct": sample.print_progress_pct,
            "print_state": sample.print_state,
            "toolhead_id": sample.toolhead_id,
            "job_id": sample.job_id,
            "raw_payload": sample.raw_payload
        }

    # PURPOSE: Parse error events from raw payload.
    # DEPENDENCIES: _extract_timestamp
    # MODIFICATION NOTES: v0.1 - Support dict or list error formats.
    def _parse_errors(self, payload: Dict[str, Any]) -> List[PrusaXLErrorEvent]:
        """Extract error events from raw payload."""
        raw_errors = payload.get("errors") or payload.get("error") or []
        if isinstance(raw_errors, dict):
            raw_errors = [raw_errors]
        if not isinstance(raw_errors, list):
            return []

        events: List[PrusaXLErrorEvent] = []
        for raw in raw_errors:
            if not isinstance(raw, dict):
                continue
            event_time = self._extract_timestamp(raw.get("timestamp") or raw.get("time"))
            event = PrusaXLErrorEvent(
                error_code=str(raw.get("code") or raw.get("error_code") or "unknown"),
                error_message=str(raw.get("message") or raw.get("error_message") or "unknown"),
                severity=str(raw.get("severity") or "unknown"),
                subsystem=raw.get("subsystem"),
                event_time=event_time,
                raw_payload=raw
            )
            events.append(event)
        return events

    # PURPOSE: Parse telemetry sample from raw payload.
    # DEPENDENCIES: _extract_timestamp
    # MODIFICATION NOTES: v0.1 - Map common telemetry keys if present.
    def _parse_telemetry(self, payload: Dict[str, Any]) -> Optional[PrusaXLTelemetrySample]:
        """Extract telemetry sample from raw payload."""
        telemetry = payload.get("telemetry") or payload.get("status") or {}
        if not isinstance(telemetry, dict):
            return None

        sample_time = self._extract_timestamp(telemetry.get("timestamp") or telemetry.get("time"))
        return PrusaXLTelemetrySample(
            sample_time=sample_time,
            nozzle_temp_c=telemetry.get("nozzle_temp_c") or telemetry.get("nozzle_temp"),
            bed_temp_c=telemetry.get("bed_temp_c") or telemetry.get("bed_temp"),
            chamber_temp_c=telemetry.get("chamber_temp_c") or telemetry.get("chamber_temp"),
            fan_speed_pct=telemetry.get("fan_speed_pct") or telemetry.get("fan_speed"),
            print_progress_pct=telemetry.get("print_progress_pct") or telemetry.get("print_progress"),
            print_state=telemetry.get("print_state") or telemetry.get("state"),
            toolhead_id=telemetry.get("toolhead_id") or telemetry.get("toolhead"),
            job_id=telemetry.get("job_id") or telemetry.get("job"),
            raw_payload=telemetry
        )

    # PURPOSE: Convert a raw timestamp to UTC datetime.
    # DEPENDENCIES: datetime, logger
    # MODIFICATION NOTES: v0.1 - Accept ISO strings or numeric epoch seconds.
    def _extract_timestamp(self, value: Any) -> datetime:
        """Parse a timestamp to a timezone-aware UTC datetime."""
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        if isinstance(value, str):
            try:
                normalized = value.replace("Z", "+00:00")
                return datetime.fromisoformat(normalized).astimezone(timezone.utc)
            except ValueError:
                logger.warning("Unparseable timestamp string: %s", value)
        return datetime.now(timezone.utc)
