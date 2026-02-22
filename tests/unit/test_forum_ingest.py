# PURPOSE: Validate forum ingest error code pattern.
# DEPENDENCIES: services.knowledge_base.forum_ingest
# MODIFICATION NOTES: v0.1 - XXYZZ format tests.

"""Tests for forum ingest error code pattern."""

from services.knowledge_base.forum_ingest import ERROR_CODE_PATTERN, extract_kb_entries_from_text


def test_error_code_pattern_matches_xl_codes() -> None:
    """Pattern matches 17xxx (XL) and other Prusa printer codes."""
    assert ERROR_CODE_PATTERN.search("Error 17101 heatbed")
    assert ERROR_CODE_PATTERN.search("Code 17201 temperature")
    assert ERROR_CODE_PATTERN.search("12201 MINI heatbed")
    assert ERROR_CODE_PATTERN.search("13101 MK4")


def test_error_code_pattern_rejects_old_format() -> None:
    """Pattern does not match generic E1234 format."""
    assert not ERROR_CODE_PATTERN.search("E1234")
    assert not ERROR_CODE_PATTERN.search("Error E001")


def test_extract_kb_entries_finds_xxyzz() -> None:
    """extract_kb_entries_from_text extracts Prusa XXYZZ codes."""
    text = "My printer showed 17101 and 17201. Fix was to check heatbed."
    entries = extract_kb_entries_from_text(text, "https://forum.example.com/thread")
    codes = [e.error_code for e in entries]
    assert "17101" in codes
    assert "17201" in codes
