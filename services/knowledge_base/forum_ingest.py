# PURPOSE: Ingest Prusa forum content into KB entries.
# DEPENDENCIES: httpx, re, services.knowledge_base.storage
# MODIFICATION NOTES: v0.1 - Initial forum ingestion logic.

"""Prusa forum ingestion utilities."""

from __future__ import annotations

import re
from typing import Iterable, List

import httpx

from services.knowledge_base.models import KnowledgeBaseEntry
from services.knowledge_base.storage import build_kb_entry

ERROR_CODE_PATTERN = re.compile(r"\bE\d{3,5}\b")


# PURPOSE: Fetch forum page content.
# DEPENDENCIES: httpx
# MODIFICATION NOTES: v0.1 - Basic HTTP fetch.
def fetch_forum_page(url: str, timeout_seconds: int = 10) -> str:
    """Fetch forum HTML content."""
    response = httpx.get(url, timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


# PURPOSE: Extract KB entries from forum content.
# DEPENDENCIES: re, build_kb_entry
# MODIFICATION NOTES: v0.1 - Heuristic extraction for error codes.
def extract_kb_entries_from_text(text: str, source_url: str) -> List[KnowledgeBaseEntry]:
    """Extract KB entries from raw forum text."""
    entries: List[KnowledgeBaseEntry] = []
    for match in ERROR_CODE_PATTERN.finditer(text):
        error_code = match.group(0)
        title = f"Forum guidance for {error_code}"
        guidance = _extract_context(text, match.start(), match.end())
        entries.append(
            build_kb_entry(
                source="prusa_forum",
                title=title,
                guidance=guidance,
                url=source_url,
                error_code=error_code,
                symptoms=None
            )
        )
    return entries


# PURPOSE: Build KB entries from forum URLs.
# DEPENDENCIES: fetch_forum_page, extract_kb_entries_from_text
# MODIFICATION NOTES: v0.1 - End-to-end ingest helper.
def ingest_forum_urls(urls: Iterable[str]) -> List[KnowledgeBaseEntry]:
    """Fetch and parse forum URLs into KB entries."""
    entries: List[KnowledgeBaseEntry] = []
    for url in urls:
        content = fetch_forum_page(url)
        entries.extend(extract_kb_entries_from_text(content, url))
    return entries


# PURPOSE: Extract nearby context for guidance.
# DEPENDENCIES: None
# MODIFICATION NOTES: v0.1 - Basic context window extraction.
def _extract_context(text: str, start: int, end: int, window: int = 200) -> str:
    """Extract a short context window around a match."""
    left = max(0, start - window)
    right = min(len(text), end + window)
    return text[left:right].strip()
