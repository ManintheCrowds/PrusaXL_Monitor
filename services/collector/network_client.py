# PURPOSE: Fetch Prusa XL payloads over network interfaces.
# DEPENDENCIES: httpx, services.collector.config.PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Initial network collector implementation.

"""Network collector for Prusa XL payloads."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from services.collector.config import PrusaXLCollectorConfig

logger = logging.getLogger(__name__)


class PrusaXLNetworkCollector:
    """Network collector for Prusa XL payloads."""

    # PURPOSE: Initialize network collector with config.
    # DEPENDENCIES: PrusaXLCollectorConfig
    # MODIFICATION NOTES: v0.1 - Config-based initialization.
    def __init__(self, config: Optional[PrusaXLCollectorConfig] = None) -> None:
        self.config = config or PrusaXLCollectorConfig()

    # PURPOSE: Fetch a unified payload from configured endpoints.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - Support direct payload URL or endpoint paths.
    async def fetch_payload(self) -> Dict[str, Any]:
        """Fetch a normalized raw payload container from the network source."""
        if self.config.payload_url:
            return await self._fetch_direct_payload(self.config.payload_url)
        return await self._fetch_composed_payload()

    # PURPOSE: Fetch a payload from a single URL.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - Direct URL retrieval.
    async def _fetch_direct_payload(self, url: str) -> Dict[str, Any]:
        """Fetch payload from a single URL."""
        timeout = self.config.request_timeout_seconds
        async with httpx.AsyncClient(timeout=timeout, **self._client_kwargs()) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    # PURPOSE: Fetch payload from multiple endpoint paths.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - Compose payload sections by endpoint.
    async def _fetch_composed_payload(self) -> Dict[str, Any]:
        """Fetch payload from status/errors/telemetry endpoints."""
        timeout = self.config.request_timeout_seconds
        base_url = self.config.base_url or ""
        payload: Dict[str, Any] = {}

        async with httpx.AsyncClient(base_url=base_url, timeout=timeout, **self._client_kwargs()) as client:
            if self.config.status_endpoint:
                payload["status"] = await self._fetch_endpoint(client, self.config.status_endpoint)
            if self.config.errors_endpoint:
                payload["errors"] = await self._fetch_endpoint(client, self.config.errors_endpoint)
            if self.config.telemetry_endpoint:
                payload["telemetry"] = await self._fetch_endpoint(client, self.config.telemetry_endpoint)
            if self.config.info_endpoint:
                payload["info"] = await self._fetch_endpoint(client, self.config.info_endpoint)
            if self.config.storage_endpoint:
                payload["storage"] = await self._fetch_endpoint(client, self.config.storage_endpoint)

        return payload

    # PURPOSE: Fetch JSON from a single endpoint path.
    # DEPENDENCIES: httpx.AsyncClient
    # MODIFICATION NOTES: v0.1 - Centralize endpoint fetch error handling.
    async def _fetch_endpoint(self, client: httpx.AsyncClient, path: str) -> Dict[str, Any]:
        """Fetch JSON payload from an endpoint path."""
        try:
            response = await client.get(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch endpoint %s: %s", path, exc)
            return {}

    # PURPOSE: Build httpx client kwargs for auth.
    # DEPENDENCIES: httpx.BasicAuth
    # MODIFICATION NOTES: v0.1 - Support basic and bearer auth.
    def _client_kwargs(self) -> Dict[str, Any]:
        """Build AsyncClient kwargs based on auth config."""
        auth_type = self.config.auth_type
        if auth_type == "basic":
            return {"auth": httpx.BasicAuth(self.config.username or "", self.config.password or "")}
        if auth_type == "digest":
            return {"auth": httpx.DigestAuth(self.config.username or "", self.config.password or "")}
        if auth_type == "bearer":
            return {"headers": {"Authorization": f"Bearer {self.config.bearer_token}"}}
        return {}
