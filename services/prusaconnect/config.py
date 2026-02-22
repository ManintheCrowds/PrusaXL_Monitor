# PURPOSE: Configuration for Prusa Connect API (optional).
# DEPENDENCIES: pydantic, app.config_base
# MODIFICATION NOTES: v0.1 - Placeholder config for Connect cloud API.

"""Prusa Connect configuration."""

from typing import Optional

from app.config_base import BaseServiceConfig


class PrusaConnectConfig(BaseServiceConfig):
    """Configuration for Prusa Connect cloud API. Optional; only active when api_key set."""

    base_url: str = "https://connect.prusa3d.com"
    api_key: str = ""
    timeout_seconds: int = 10

    class Config:
        env_prefix = "PRUSACONNECT_"
        case_sensitive = False

    @property
    def is_configured(self) -> bool:
        """True if Connect API is configured (feature-flag)."""
        return bool(self.api_key and self.api_key.strip())
