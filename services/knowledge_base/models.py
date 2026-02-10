# PURPOSE: SQLAlchemy models for troubleshooting knowledge base.
# DEPENDENCIES: sqlalchemy
# MODIFICATION NOTES: v0.1 - Initial KB models.

"""Knowledge base data models."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class KnowledgeBaseEntry(Base):
    """Knowledge base entry linked to error codes or symptoms."""

    __tablename__ = "kb_entries"

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)  # prusa_forum, internal, other
    title = Column(String(255), nullable=False)
    url = Column(String(512), nullable=True)
    error_code = Column(String(64), nullable=True)
    symptoms = Column(String(255), nullable=True)
    guidance = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
