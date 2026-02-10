# PURPOSE: Read and parse Prusa XL log files into error events.
# DEPENDENCIES: pathlib, re, datetime, services.collector.prusa_xl_adapter
# MODIFICATION NOTES: v0.1 - Initial log reader for USB/manual logs.

"""Log reader for Prusa XL USB or exported logs."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

from services.collector.prusa_xl_adapter import PrusaXLErrorEvent

ERROR_CODE_PATTERN = re.compile(r"\bE\d{3,5}\b")
SEVERITY_PATTERN = re.compile(r"\b(INFO|WARN|WARNING|ERROR|CRITICAL)\b", re.IGNORECASE)
TIMESTAMP_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})")


# PURPOSE: List log files in a directory.
# DEPENDENCIES: pathlib.Path
# MODIFICATION NOTES: v0.1 - Filter by common log extensions.
def list_log_files(log_dir: str) -> List[Path]:
    """Return log file paths from a directory."""
    base = Path(log_dir)
    if not base.exists():
        return []
    patterns = ["*.log", "*.txt", "*.err"]
    files: List[Path] = []
    for pattern in patterns:
        files.extend(base.glob(pattern))
    return sorted(set(files))


# PURPOSE: Parse log files into error events.
# DEPENDENCIES: PrusaXLErrorEvent
# MODIFICATION NOTES: v0.1 - Best-effort parser for unknown log formats.
def parse_log_files(paths: Iterable[Path]) -> List[PrusaXLErrorEvent]:
    """Parse log files into normalized error events."""
    events: List[PrusaXLErrorEvent] = []
    for path in paths:
        if not path.is_file():
            continue
        events.extend(_parse_log_file(path))
    return events


# PURPOSE: Parse a single log file for error events.
# DEPENDENCIES: _extract_timestamp, _extract_severity
# MODIFICATION NOTES: v0.1 - Simple regex-based parser.
def _parse_log_file(path: Path) -> List[PrusaXLErrorEvent]:
    """Parse a single log file to extract error events."""
    events: List[PrusaXLErrorEvent] = []
    for line in path.read_text(errors="ignore").splitlines():
        error_code = _extract_error_code(line)
        severity = _extract_severity(line)
        if not error_code and severity not in {"error", "critical"}:
            continue
        event_time = _extract_timestamp(line)
        events.append(
            PrusaXLErrorEvent(
                error_code=error_code or "unknown",
                error_message=line.strip()[:500],
                severity=severity,
                subsystem=None,
                event_time=event_time,
                raw_payload={"line": line, "file": str(path)}
            )
        )
    return events


# PURPOSE: Extract error code from a log line.
# DEPENDENCIES: ERROR_CODE_PATTERN
# MODIFICATION NOTES: v0.1 - Use E#### code pattern.
def _extract_error_code(line: str) -> Optional[str]:
    """Extract Prusa error code from a log line."""
    match = ERROR_CODE_PATTERN.search(line)
    return match.group(0) if match else None


# PURPOSE: Extract severity from a log line.
# DEPENDENCIES: SEVERITY_PATTERN
# MODIFICATION NOTES: v0.1 - Normalize severity to lowercase.
def _extract_severity(line: str) -> str:
    """Extract severity from a log line."""
    match = SEVERITY_PATTERN.search(line)
    if not match:
        return "unknown"
    value = match.group(1).lower()
    return "warning" if value == "warn" else value


# PURPOSE: Extract timestamp from a log line.
# DEPENDENCIES: TIMESTAMP_PATTERN
# MODIFICATION NOTES: v0.1 - Parse ISO timestamps when present.
def _extract_timestamp(line: str) -> datetime:
    """Extract timestamp from log line or fallback to now."""
    match = TIMESTAMP_PATTERN.search(line)
    if match:
        try:
            return datetime.fromisoformat(match.group(1)).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)
