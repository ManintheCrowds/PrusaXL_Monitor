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
from services.prusalink.client import PrusaLinkClient
from services.prusalink.adapter import PrusaLinkAdapter
from services.prusalink.config import PrusaLinkConfig


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
        self.prusalink_config = PrusaLinkConfig()
        self.prusalink = PrusaLinkClient(self.prusalink_config)
        self.prusalink_adapter = PrusaLinkAdapter(self.prusalink_config)

    # PURPOSE: Collect and normalize API payload.
    # DEPENDENCIES: PrusaXLNetworkCollector, PrusaXLAdapter
    # MODIFICATION NOTES: v0.1 - API-only normalization.
    async def collect_api_payload(self) -> Dict[str, Any]:
        """Collect and normalize API payload into adapter schema."""
        payload = await self.network.fetch_payload()
        normalized = self.adapter.normalize_payload(payload, source="network_api")
        return normalized.model_dump()

    # PURPOSE: Collect and normalize PrusaLink payload.
    # DEPENDENCIES: PrusaLinkClient, PrusaLinkAdapter
    # MODIFICATION NOTES: v0.1 - PrusaLink native API support.
    async def collect_prusalink_payload(self) -> Dict[str, Any]:
        """Collect and normalize PrusaLink payload from /api/v1/status, /api/v1/job, /api/v1/info."""
        if not self.prusalink_config.base_url:
            return {"source": "prusalink", "error": "PRUSALINK_BASE_URL not configured", "telemetry": None, "errors": []}
        try:
            status = await self.prusalink.get_status()
            job = status.get("job")
            info = None
            try:
                info = await self.prusalink.get_info()
            except Exception:
                pass
            normalized = self.prusalink_adapter.normalize_payload(status=status, job=job, info=info)
            return normalized.model_dump()
        except Exception as e:
            from services.prusalink.client import PrusaLinkError
            http_error = {}
            if isinstance(e, PrusaLinkError):
                http_error = {"code": e.code, "title": e.message, "url": e.url}
            else:
                http_error = {"code": "unknown", "title": str(e), "url": None}
            normalized = self.prusalink_adapter.normalize_payload(
                status={}, job={}, http_error=http_error
            )
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
