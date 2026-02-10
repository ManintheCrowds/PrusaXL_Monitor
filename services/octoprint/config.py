# PURPOSE: Configuration for OctoPrint integration.
# DEPENDENCIES: pydantic, app.config_base.BaseServiceConfig
# MODIFICATION NOTES: v0.1 - Initial OctoPrint config.

"""OctoPrint configuration."""

from typing import Optional
from pydantic import field_validator

from app.config_base import BaseServiceConfig


class OctoPrintConfig(BaseServiceConfig):
    """Configuration for OctoPrint API access."""

    base_url: str = "http://octoprint:5000"
    api_key: str = ""
    timeout_seconds: int = 10

    class Config:
        env_prefix = "OCTOPRINT_"
        case_sensitive = False

    # PURPOSE: Validate API key presence.
    # DEPENDENCIES: pydantic.field_validator
    # MODIFICATION NOTES: v0.1 - Ensure API key is non-empty.
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        """Ensure API key is provided."""
        return cls.validate_non_empty_string(value, field_name="api_key") or ""

    # PURPOSE: Validate timeout.
    # DEPENDENCIES: BaseServiceConfig.validate_positive_int
    # MODIFICATION NOTES: v0.1 - Ensure timeout is positive.
    @field_validator("timeout_seconds")
    @classmethod
    def validate_timeout(cls, value: int) -> int:
        """Ensure timeout is positive."""
        return cls.validate_positive_int(value, field_name="timeout_seconds")
