# PURPOSE: PrusaLink REST API client.
# DEPENDENCIES: httpx, services.prusalink.config
# MODIFICATION NOTES: v0.1 - Initial PrusaLink client per OpenAPI spec.

"""PrusaLink API client."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from services.prusalink.config import PrusaLinkConfig

logger = logging.getLogger(__name__)


class PrusaLinkClient:
    """Client for PrusaLink REST API (Prusa-Link-Web)."""

    def __init__(self, config: Optional[PrusaLinkConfig] = None) -> None:
        self.config = config or PrusaLinkConfig()

    async def get_status(self) -> Dict[str, Any]:
        """Fetch /api/v1/status (printer, job, transfer, storage, camera)."""
        return await self._get_json("/api/v1/status")

    async def get_job(self) -> Dict[str, Any]:
        """Fetch /api/v1/job (current job info)."""
        return await self._get_json("/api/v1/job")

    async def get_info(self) -> Dict[str, Any]:
        """Fetch /api/v1/info (printer information)."""
        return await self._get_json("/api/v1/info")

    async def _get_json(self, path: str) -> Dict[str, Any]:
        """GET helper with DigestAuth."""
        auth = httpx.DigestAuth(self.config.username or "", self.config.password or "")
        async with httpx.AsyncClient(
            base_url=self.config.base_url.rstrip("/"),
            timeout=self.config.timeout_seconds,
            auth=auth
        ) as client:
            response = await client.get(path)
            if response.status_code >= 400:
                error_body = self._parse_error_body(response)
                raise PrusaLinkError(
                    status_code=response.status_code,
                    message=error_body.get("title") or error_body.get("text") or response.reason_phrase,
                    code=error_body.get("code"),
                    url=error_body.get("url")
                )
            return response.json()

    def _parse_error_body(self, response: httpx.Response) -> Dict[str, Any]:
        """Parse PrusaLink Error schema from response body."""
        try:
            data = response.json()
            if isinstance(data, dict):
                return {
                    "code": data.get("code"),
                    "title": data.get("title"),
                    "text": data.get("text"),
                    "url": data.get("url")
                }
        except Exception:
            pass
        return {}


class PrusaLinkError(Exception):
    """PrusaLink API error with optional help URL."""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: Optional[str] = None,
        url: Optional[str] = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.code = code
        self.url = url
