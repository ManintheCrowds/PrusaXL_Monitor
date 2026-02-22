# PURPOSE: Prusa Connect cloud API client (optional/placeholder).
# DEPENDENCIES: httpx, services.prusaconnect.config
# MODIFICATION NOTES: v0.1 - Placeholder; Connect API docs incomplete. Expand when docs available.

"""Prusa Connect API client. Placeholder for future cloud monitoring."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx

from services.prusaconnect.config import PrusaConnectConfig

logger = logging.getLogger(__name__)


class PrusaConnectClient:
    """Client for Prusa Connect cloud API. Placeholder until API docs are available."""

    def __init__(self, config: Optional[PrusaConnectConfig] = None) -> None:
        self.config = config or PrusaConnectConfig()

    async def get_printers(self) -> Dict[str, Any]:
        """Fetch printer list from Connect. Placeholder - returns empty when not configured."""
        if not self.config.is_configured:
            return {"printers": [], "error": "PRUSACONNECT_API_KEY not set"}
        try:
            async with httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
                headers={"Authorization": f"Bearer {self.config.api_key}"}
            ) as client:
                response = await client.get("/app/printers")
                if response.status_code >= 400:
                    return {"printers": [], "error": f"HTTP {response.status_code}"}
                return response.json()
        except Exception as e:
            logger.warning("Prusa Connect API error: %s", e)
            return {"printers": [], "error": str(e)}
