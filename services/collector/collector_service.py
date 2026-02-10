# PURPOSE: Orchestrate Prusa XL data collection from API and logs.
# DEPENDENCIES: services.collector.network_client, services.collector.log_reader
# MODIFICATION NOTES: v0.1 - Initial collector orchestration.

"""Collector service for Prusa XL data sources."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from services.collector.config import PrusaXLCollectorConfig
from services.collector.log_reader import list_log_files, parse_log_files
from services.collector.network_client import PrusaXLNetworkCollector
from services.collector.prusa_xl_adapter import PrusaXLAdapter, PrusaXLErrorEvent
from services.octoprint.client import OctoPrintClient
from services.octoprint.adapter import OctoPrintAdapter


class PrusaXLCollectorService:
    """Collector service to fetch and normalize Prusa XL data."""

    # PURPOSE: Initialize collector service with config.
    # DEPENDENCIES: PrusaXLCollectorConfig
    # MODIFICATION NOTES: v0.1 - Setup adapters for API and logs.
    def __init__(self, config: Optional[PrusaXLCollectorConfig] = None) -> None:
        self.config = config or PrusaXLCollectorConfig()
        self.network = PrusaXLNetworkCollector(self.config)
        self.adapter = PrusaXLAdapter(self.config)
        self.octoprint = OctoPrintClient()
        self.octo_adapter = OctoPrintAdapter()

    # PURPOSE: Collect and normalize API payload.
    # DEPENDENCIES: PrusaXLNetworkCollector, PrusaXLAdapter
    # MODIFICATION NOTES: v0.1 - API-only normalization.
    async def collect_api_payload(self) -> Dict[str, Any]:
        """Collect and normalize API payload into adapter schema."""
        payload = await self.network.fetch_payload()
        normalized = self.adapter.normalize_payload(payload, source="network_api")
        return normalized.model_dump()

    # PURPOSE: Collect and normalize OctoPrint payload.
    # DEPENDENCIES: OctoPrintClient, OctoPrintAdapter
    # MODIFICATION NOTES: v0.1 - OctoPrint data normalization.
    async def collect_octoprint_payload(self) -> Dict[str, Any]:
        """Collect and normalize OctoPrint payload."""
        printer = await self.octoprint.get_printer()
        job = await self.octoprint.get_job()
        logs = await self.octoprint.get_logs()
        normalized = self.octo_adapter.normalize_payload(
            printer=printer,
            job=job,
            logs=logs
        )
        return normalized

    # PURPOSE: Collect and normalize log-derived error events.
    # DEPENDENCIES: log_reader, PrusaXLAdapter
    # MODIFICATION NOTES: v0.1 - Log-derived error normalization.
    def collect_log_errors(self) -> List[Dict[str, Any]]:
        """Collect error events from logs and convert to row dicts."""
        if not self.config.log_path:
            return []
        log_files = list_log_files(self.config.log_path)
        events = parse_log_files(log_files)
        return [self.adapter.build_error_row(event) for event in events]

    # PURPOSE: Normalize log events without DB conversion.
    # DEPENDENCIES: log_reader
    # MODIFICATION NOTES: v0.1 - Provide structured error events.
    def collect_log_events(self) -> List[PrusaXLErrorEvent]:
        """Collect raw error events from logs."""
        if not self.config.log_path:
            return []
        log_files = list_log_files(self.config.log_path)
        return parse_log_files(log_files)
