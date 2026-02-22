# PURPOSE: Validate Prusa-Error-Codes YAML ingestion.
# DEPENDENCIES: pytest, unittest.mock, services.knowledge_base.error_codes_ingest
# MODIFICATION NOTES: v0.1 - Initial error codes ingest tests.

"""Tests for Prusa-Error-Codes YAML ingestion."""

from unittest.mock import MagicMock, patch

import pytest
from services.knowledge_base.error_codes_ingest import (
    filter_xl_errors,
    ingest_error_codes,
    parse_error_codes_yaml,
)


SAMPLE_YAML = """
Errors:
  - code: "XX101"
    printers: [XL]
    title: "TOOLCHANGER ERROR"
    text: "Check all tools if they are properly parked or picked."
    id: "TOOLCHANGER"
    approved: true
  - code: "17101"
    printers: [XL]
    title: "XL HEATBED ERROR"
    text: "Heatbed heating failed."
    id: "HEATBED_XL"
    approved: true
  - code: "XX102"
    printers: [MK4]
    title: "MK4 ONLY"
    text: "Not for XL."
    approved: true
"""


def test_parse_error_codes_yaml() -> None:
    """Parse YAML returns list of error dicts."""
    errors = parse_error_codes_yaml(SAMPLE_YAML)
    assert len(errors) == 3
    assert errors[0]["code"] == "XX101"
    assert errors[0]["printers"] == ["XL"]
    assert errors[1]["code"] == "17101"


def test_filter_xl_errors() -> None:
    """Filter keeps only XL-applicable errors."""
    errors = parse_error_codes_yaml(SAMPLE_YAML)
    xl_errors = filter_xl_errors(errors)
    assert len(xl_errors) == 2
    codes = [e["code"] for e in xl_errors]
    assert "XX101" in codes
    assert "17101" in codes
    assert "XX102" not in codes


@patch("services.knowledge_base.error_codes_ingest.fetch_error_codes_yaml")
def test_ingest_error_codes_fetch_and_filter(mock_fetch: MagicMock) -> None:
    """Ingest fetches YAML and returns XL-filtered KB entries."""
    mock_fetch.return_value = SAMPLE_YAML
    entries = ingest_error_codes(xl_only=True)
    mock_fetch.assert_called_once()
    assert len(entries) == 2
    assert entries[0].source == "prusa_error_codes"
    assert entries[0].error_code in ("XX101", "17101")
    assert entries[0].title
    assert entries[0].guidance
    assert "prusa.io" in (entries[0].url or "")
