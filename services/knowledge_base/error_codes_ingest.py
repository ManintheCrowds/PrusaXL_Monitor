# PURPOSE: Ingest Prusa-Error-Codes YAML into KB entries.
# DEPENDENCIES: httpx, pyyaml, services.knowledge_base.storage
# MODIFICATION NOTES: v0.1 - Initial error codes ingestion.

"""Prusa-Error-Codes YAML ingestion."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx
import yaml

from services.knowledge_base.models import KnowledgeBaseEntry
from services.knowledge_base.storage import build_kb_entry

logger = logging.getLogger(__name__)

ERROR_CODES_YAML_URL = "https://raw.githubusercontent.com/prusa3d/Prusa-Error-Codes/master/yaml/buddy-error-codes.yaml"
PRUSA_ERROR_CODES_BASE = "https://prusa.io/error-codes"
SOURCE = "prusa_error_codes"


def fetch_error_codes_yaml(url: str = ERROR_CODES_YAML_URL, timeout_seconds: int = 30) -> str:
    """Fetch raw YAML content from URL."""
    response = httpx.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def parse_error_codes_yaml(content: str) -> List[Dict[str, Any]]:
    """Parse YAML and return list of error dicts."""
    data = yaml.safe_load(content)
    if not data or not isinstance(data, dict):
        return []
    errors = data.get("Errors") or data.get("errors") or []
    if not isinstance(errors, list):
        return []
    return [e for e in errors if isinstance(e, dict)]


def filter_xl_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter errors applicable to Prusa XL (printers includes XL or code starts with 17)."""
    result: List[Dict[str, Any]] = []
    for e in errors:
        printers = e.get("printers") or []
        if isinstance(printers, str):
            printers = [printers]
        code = str(e.get("code") or "")
        if "XL" in printers:
            result.append(e)
        elif code.startswith("17"):
            result.append(e)
    return result


def error_dict_to_kb_entry(error: Dict[str, Any]) -> KnowledgeBaseEntry:
    """Map error dict to KnowledgeBaseEntry."""
    code = str(error.get("code") or "unknown")
    title = str(error.get("title") or "Unknown error")
    text = str(error.get("text") or "")
    guidance = f"{title}. {text}".strip() if text else title
    url = f"{PRUSA_ERROR_CODES_BASE}"
    return build_kb_entry(
        source=SOURCE,
        title=title,
        guidance=guidance,
        url=url,
        error_code=code,
        symptoms=None
    )


def ingest_error_codes(
    url: str = ERROR_CODES_YAML_URL,
    xl_only: bool = True,
    timeout_seconds: int = 30
) -> List[KnowledgeBaseEntry]:
    """Fetch, parse, filter, and build KB entries from Prusa-Error-Codes YAML."""
    content = fetch_error_codes_yaml(url=url, timeout_seconds=timeout_seconds)
    errors = parse_error_codes_yaml(content)
    if xl_only:
        errors = filter_xl_errors(errors)
    return [error_dict_to_kb_entry(e) for e in errors]
