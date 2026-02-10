# PURPOSE: Validate Prusa XL adapter normalization behavior.
# DEPENDENCIES: pytest, services.collector.prusa_xl_adapter
# MODIFICATION NOTES: v0.1 - Initial normalization tests.

"""Tests for Prusa XL collector adapter."""

from services.collector.prusa_xl_adapter import PrusaXLAdapter


# PURPOSE: Verify error and telemetry parsing from payload.
# DEPENDENCIES: PrusaXLAdapter
# MODIFICATION NOTES: v0.1 - Basic normalization test.
def test_normalize_payload_parses_errors_and_telemetry() -> None:
    adapter = PrusaXLAdapter()
    payload = {
        "errors": [
            {
                "code": "E001",
                "message": "Nozzle overheat",
                "severity": "critical",
                "timestamp": "2026-01-15T00:00:00Z"
            }
        ],
        "telemetry": {
            "nozzle_temp_c": 285.5,
            "bed_temp_c": 95.0,
            "fan_speed_pct": 75,
            "print_progress_pct": 12.5,
            "state": "printing",
            "timestamp": "2026-01-15T00:00:05Z"
        }
    }

    normalized = adapter.normalize_payload(payload, source="test")

    assert normalized.source == "test"
    assert len(normalized.errors) == 1
    assert normalized.errors[0].error_code == "E001"
    assert normalized.telemetry is not None
    assert normalized.telemetry.nozzle_temp_c == 285.5
    assert normalized.telemetry.print_state == "printing"


# PURPOSE: Ensure percentage values are clamped to 0-100.
# DEPENDENCIES: PrusaXLAdapter
# MODIFICATION NOTES: v0.1 - Clamp validation test.
def test_percentage_clamping() -> None:
    adapter = PrusaXLAdapter()
    payload = {
        "telemetry": {
            "fan_speed_pct": 130,
            "print_progress_pct": -5
        }
    }

    normalized = adapter.normalize_payload(payload, source="test")

    assert normalized.telemetry is not None
    assert normalized.telemetry.fan_speed_pct == 100.0
    assert normalized.telemetry.print_progress_pct == 0.0
