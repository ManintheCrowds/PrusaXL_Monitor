# PURPOSE: SQLAlchemy models for troubleshooting lookups.
# DEPENDENCIES: sqlalchemy
# MODIFICATION NOTES: v0.1 - Minimal error event models.

"""Troubleshooting data models."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PrusaXLErrorEventRecord(Base):
    """Error event record used for troubleshooting lookup."""

    __tablename__ = "prusa_xl_error_events"

    id = Column(String(36), primary_key=True)
    printer_id = Column(String(64), nullable=False)
    error_code = Column(String(64), nullable=False)
    error_message = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False)
    subsystem = Column(String(64))
    event_time = Column(DateTime(timezone=True))
