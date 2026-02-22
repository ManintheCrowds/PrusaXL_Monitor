# PURPOSE: Configuration for PrusaLink API access.
# DEPENDENCIES: pydantic, app.config_base.BaseServiceConfig
# MODIFICATION NOTES: v0.1 - Initial PrusaLink config.

"""PrusaLink configuration."""

from typing import Optional
from pydantic import field_validator

from app.config_base import BaseServiceConfig


class PrusaLinkConfig(BaseServiceConfig):
    """Configuration for PrusaLink API (Prusa-Link-Web)."""

    base_url: str = ""
    username: str = ""
    password: str = ""
    printer_id: str = "prusa-xl-1"
    timeout_seconds: int = 10

    class Config:
        env_prefix = "PRUSALINK_"
        case_sensitive = False

    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, value: int) -> int:
        """Ensure timeout is positive."""
        return cls.validate_positive_int(value, field_name="timeout_seconds")

    @field_validator("printer_id")
    @classmethod
    def validate_printer_id(cls, value: Optional[str]) -> str:
        """Ensure printer_id is non-empty."""
        return cls.validate_non_empty_string(value or "prusa-xl-1", field_name="printer_id") or "prusa-xl-1"
