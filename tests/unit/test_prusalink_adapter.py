# PURPOSE: Validate PrusaLink adapter normalization.
# DEPENDENCIES: pytest, services.prusalink.adapter
# MODIFICATION NOTES: v0.1 - Initial PrusaLink adapter tests.

"""Tests for PrusaLink adapter."""

import pytest
from services.prusalink.adapter import PrusaLinkAdapter
from services.prusalink.config import PrusaLinkConfig


def test_prusalink_adapter_normalizes_status_and_job() -> None:
    """PrusaLink adapter maps StatusPrinter and StatusJob to telemetry."""
    adapter = PrusaLinkAdapter(PrusaLinkConfig(printer_id="test-xl"))
    status = {
        "printer": {
            "state": "PRINTING",
            "temp_nozzle": 215.0,
            "temp_bed": 60.0,
            "fan_hotend": 100,
            "fan_print": 50,
        },
        "job": {
            "progress": 42.5,
            "state": "PRINTING",
            "file": {"display_name": "test.gcode"},
        },
    }
    result = adapter.normalize_payload(status=status, job=status.get("job"))
    assert result.source == "prusalink"
    assert result.telemetry is not None
    assert result.telemetry.nozzle_temp_c == 215.0
    assert result.telemetry.bed_temp_c == 60.0
    assert result.telemetry.print_state == "PRINTING"
    assert result.telemetry.print_progress_pct == 42.5
    assert result.telemetry.job_id == "test.gcode"
    assert result.telemetry.fan_speed_pct == 100


def test_prusalink_adapter_extracts_error_from_printer_state() -> None:
    """When printer.state is ERROR, adapter emits error event."""
    adapter = PrusaLinkAdapter()
    status = {
        "printer": {
            "state": "ERROR",
            "status_printer": {"ok": False, "message": "Heatbed heating failed"},
        },
    }
    result = adapter.normalize_payload(status=status)
    assert len(result.errors) == 1
    assert result.errors[0].error_code == "printer_error"
    assert "Heatbed heating failed" in result.errors[0].error_message


def test_prusalink_adapter_extracts_error_from_http_error() -> None:
    """When http_error is provided, adapter emits error event with url."""
    adapter = PrusaLinkAdapter()
    http_error = {
        "code": "17201",
        "title": "Heatbed heating failed",
        "url": "https://help.prusa3d.com/en/17201",
    }
    result = adapter.normalize_payload(status={}, job={}, http_error=http_error)
    assert len(result.errors) == 1
    assert result.errors[0].error_code == "17201"
    assert result.errors[0].raw_payload.get("url") == "https://help.prusa3d.com/en/17201"
