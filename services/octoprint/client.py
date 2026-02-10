# PURPOSE: OctoPrint API client for printer/job/log data.
# DEPENDENCIES: httpx, services.octoprint.config
# MODIFICATION NOTES: v0.1 - Initial OctoPrint client.

"""OctoPrint API client."""

from __future__ import annotations

from typing import Dict, Any, Optional

import httpx

from services.octoprint.config import OctoPrintConfig


class OctoPrintClient:
    """Client for OctoPrint REST API."""

    # PURPOSE: Initialize client with config.
    # DEPENDENCIES: OctoPrintConfig
    # MODIFICATION NOTES: v0.1 - Store config and headers.
    def __init__(self, config: Optional[OctoPrintConfig] = None) -> None:
        self.config = config or OctoPrintConfig()

    # PURPOSE: Fetch printer state and temperatures.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - GET /api/printer.
    async def get_printer(self) -> Dict[str, Any]:
        """Return printer state and temperatures."""
        return await self._get_json("/api/printer")

    # PURPOSE: Fetch current job state.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - GET /api/job.
    async def get_job(self) -> Dict[str, Any]:
        """Return job and progress details."""
        return await self._get_json("/api/job")

    # PURPOSE: Fetch server logs.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - GET /api/logs.
    async def get_logs(self) -> Dict[str, Any]:
        """Return OctoPrint log entries."""
        return await self._get_json("/api/logs")

    # PURPOSE: Execute GET requests with auth.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - Centralized GET handling.
    async def _get_json(self, path: str) -> Dict[str, Any]:
        """GET helper for OctoPrint endpoints."""
        timeout = self.config.timeout_seconds
        headers = {"X-Api-Key": self.config.api_key}
        async with httpx.AsyncClient(base_url=self.config.base_url, timeout=timeout, headers=headers) as client:
            response = await client.get(path)
            response.raise_for_status()
            return response.json()
