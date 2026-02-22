# PURPOSE: Pytest fixtures for PrusaXL_Monitor tests.
# DEPENDENCIES: pytest, flask
# MODIFICATION NOTES: v0.1 - Test config, client fixture, DB setup for E2E.

"""Pytest configuration and fixtures."""

# Set test config before any app imports
import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["TESTING"] = "1"

import pytest

from app import create_app
from app.db import SessionLocal, engine
from services.knowledge_base.models import Base as KBBase
from services.troubleshoot.models import Base as TroubleshootBase


@pytest.fixture(scope="session")
def _create_tables():
    """Create all tables in test DB (session-scoped)."""
    TroubleshootBase.metadata.create_all(engine)
    KBBase.metadata.create_all(engine)


@pytest.fixture
def app(_create_tables):
    """Flask app in test mode."""
    return create_app()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()
