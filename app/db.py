# PURPOSE: Database session management for PostgreSQL.
# DEPENDENCIES: sqlalchemy
# MODIFICATION NOTES: v0.1 - Initial DB session factory.

"""Database session helpers."""

from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/prusa_xl")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# PURPOSE: Provide a database session generator.
# DEPENDENCIES: SQLAlchemy SessionLocal
# MODIFICATION NOTES: v0.1 - Basic session lifecycle management.
def get_db() -> Generator[Session, None, None]:
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
