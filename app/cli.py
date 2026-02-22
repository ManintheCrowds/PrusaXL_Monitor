# PURPOSE: Flask CLI commands for KB and maintenance.
# DEPENDENCIES: flask.cli, app.db, services.knowledge_base
# MODIFICATION NOTES: v0.1 - Initial CLI with kb seed-error-codes.

"""Flask CLI commands."""

from __future__ import annotations

import click

from app.db import SessionLocal
from services.knowledge_base.error_codes_ingest import SOURCE, ingest_error_codes
from services.knowledge_base.storage import delete_kb_by_source, save_kb_entry


def register_cli(app):
    """Register CLI commands on the Flask app."""

    @app.cli.group()
    def kb():
        """Knowledge base management commands."""

    @kb.command("seed-error-codes")
    @click.option("--xl-only/--all", default=True, help="Filter to XL errors only")
    @click.option("--dry-run", is_flag=True, help="Fetch and parse only, do not persist")
    def seed_error_codes(xl_only: bool, dry_run: bool) -> None:
        """Seed KB from Prusa-Error-Codes YAML (XL filter)."""
        click.echo("Fetching Prusa-Error-Codes YAML...")
        entries = ingest_error_codes(xl_only=xl_only)
        click.echo(f"Parsed {len(entries)} error code entries")
        if dry_run:
            for e in entries[:5]:
                click.echo(f"  {e.error_code}: {e.title}")
            if len(entries) > 5:
                click.echo(f"  ... and {len(entries) - 5} more")
            return
        session = SessionLocal()
        try:
            removed = delete_kb_by_source(session, SOURCE)
            if removed:
                click.echo(f"Removed {removed} existing {SOURCE} entries")
            saved = 0
            for entry in entries:
                save_kb_entry(session, entry)
                saved += 1
            click.echo(f"Saved {saved} KB entries")
        finally:
            session.close()
