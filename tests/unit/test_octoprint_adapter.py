# PURPOSE: Validate OctoPrint adapter normalization behavior.
# DEPENDENCIES: services.octoprint.adapter
# MODIFICATION NOTES: v0.1 - Initial adapter tests.

"""Tests for OctoPrint adapter."""

from services.octoprint.adapter import OctoPrintAdapter


# PURPOSE: Ensure telemetry and errors are extracted.
# DEPENDENCIES: OctoPrintAdapter
# MODIFICATION NOTES: v0.1 - Basic normalization test.
def test_octoprint_normalize_payload() -> None:
    adapter = OctoPrintAdapter()
    printer = {
        "temperature": {"tool0": {"actual": 210.5}, "bed": {"actual": 60.0}},
        "state": {"text": "Printing"}
    }
    job = {"progress": {"completion": 12.5}, "job": {"file": {"name": "test.gcode"}}}
    logs = {"logs": ["INFO start", "ERROR heater failure"]}

    result = adapter.normalize_payload(printer=printer, job=job, logs=logs)

    assert result["source"] == "octoprint"
    assert result["telemetry"]["nozzle_temp_c"] == 210.5
    assert result["telemetry"]["print_progress_pct"] == 12.5
    assert len(result["errors"]) == 1


def test_octoprint_multitool_temps() -> None:
    """Multi-tool (Prusa XL) extracts tool0..tool4 temperatures."""
    adapter = OctoPrintAdapter()
    printer = {
        "temperature": {
            "tool0": {"actual": 215.0},
            "tool1": {"actual": 210.0},
            "tool2": {"actual": 0.0},
            "bed": {"actual": 60.0},
        },
        "state": {"text": "Printing"},
    }
    job = {"progress": {"completion": 50.0}, "job": {"file": {"name": "multi.gcode"}}}
    logs = {"logs": []}

    result = adapter.normalize_payload(printer=printer, job=job, logs=logs)

    assert result["telemetry"]["nozzle_temp_c"] == 215.0
    assert result["telemetry"]["tool_temps"] == {"tool0": 215.0, "tool1": 210.0, "tool2": 0.0}
    assert result["telemetry"]["nozzle_temps_c"] == [215.0, 210.0, 0.0]
