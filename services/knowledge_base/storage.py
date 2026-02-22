# PURPOSE: Store and query KB entries from the database.
# DEPENDENCIES: sqlalchemy, services.knowledge_base.models
# MODIFICATION NOTES: v0.1 - Initial KB storage helpers.

"""Knowledge base storage helpers."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from services.knowledge_base.models import KnowledgeBaseEntry


# PURPOSE: Persist a knowledge base entry.
# DEPENDENCIES: sqlalchemy.orm.Session
# MODIFICATION NOTES: v0.1 - Simple insert helper.
def save_kb_entry(session: Session, entry: KnowledgeBaseEntry) -> KnowledgeBaseEntry:
    """Save a KB entry to the database."""
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


# PURPOSE: Lookup KB entries by error code.
# DEPENDENCIES: sqlalchemy.orm.Session
# MODIFICATION NOTES: v0.1 - Filter by error_code.
def find_kb_by_error_code(session: Session, error_code: str) -> List[KnowledgeBaseEntry]:
    """Return KB entries for an error code."""
    return (
        session.query(KnowledgeBaseEntry)
        .filter(KnowledgeBaseEntry.error_code == error_code)
        .order_by(KnowledgeBaseEntry.created_at.desc())
        .all()
    )


# PURPOSE: Lookup KB entries by symptom keyword.
# DEPENDENCIES: sqlalchemy.orm.Session
# MODIFICATION NOTES: v0.1 - Simple symptom substring search.
def find_kb_by_symptom(session: Session, symptom: str) -> List[KnowledgeBaseEntry]:
    """Return KB entries containing a symptom substring."""
    return (
        session.query(KnowledgeBaseEntry)
        .filter(KnowledgeBaseEntry.symptoms.ilike(f"%{symptom}%"))
        .order_by(KnowledgeBaseEntry.created_at.desc())
        .all()
    )


# PURPOSE: Delete KB entries by source.
# DEPENDENCIES: sqlalchemy.orm.Session
# MODIFICATION NOTES: v0.1 - For idempotent seed operations.
def delete_kb_by_source(session: Session, source: str) -> int:
    """Delete all KB entries with given source. Returns count deleted."""
    deleted = session.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.source == source).delete()
    session.commit()
    return deleted


# PURPOSE: Get most recent KB entries.
# DEPENDENCIES: sqlalchemy.orm.Session
# MODIFICATION NOTES: v0.1 - Limit recent results.
def list_recent_entries(session: Session, limit: int = 20) -> List[KnowledgeBaseEntry]:
    """List recent KB entries."""
    return (
        session.query(KnowledgeBaseEntry)
        .order_by(KnowledgeBaseEntry.created_at.desc())
        .limit(limit)
        .all()
    )


# PURPOSE: Safely build a KnowledgeBaseEntry object.
# DEPENDENCIES: KnowledgeBaseEntry
# MODIFICATION NOTES: v0.1 - Normalize fields for KB ingestion.
def build_kb_entry(
    source: str,
    title: str,
    guidance: str,
    url: Optional[str] = None,
    error_code: Optional[str] = None,
    symptoms: Optional[str] = None
) -> KnowledgeBaseEntry:
    """Build a KnowledgeBaseEntry object."""
    return KnowledgeBaseEntry(
        source=source,
        title=title,
        url=url,
        error_code=error_code,
        symptoms=symptoms,
        guidance=guidance
    )
