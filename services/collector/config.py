# PURPOSE: Configuration for Prusa XL collector adapters.
# DEPENDENCIES: pydantic, app.config_base.BaseServiceConfig
# MODIFICATION NOTES: v0.1 - Initial collector configuration.

"""Configuration for Prusa XL collector adapters."""

from typing import Optional
from pydantic import field_validator, model_validator
from app.config_base import BaseServiceConfig


class PrusaXLCollectorConfig(BaseServiceConfig):
    """Configuration for Prusa XL collector POC."""

    printer_id: str = "prusa-xl-1"
    source_type: str = "unknown"  # usb_serial, network_api, log_files, sd_gcode
    base_url: Optional[str] = None
    payload_url: Optional[str] = None
    status_endpoint: Optional[str] = None
    errors_endpoint: Optional[str] = None
    telemetry_endpoint: Optional[str] = None
    info_endpoint: Optional[str] = None
    storage_endpoint: Optional[str] = None
    auth_type: str = "none"  # none, basic, digest, bearer
    username: Optional[str] = None
    password: Optional[str] = None
    bearer_token: Optional[str] = None
    device_port: Optional[str] = None
    log_path: Optional[str] = None
    poll_interval_seconds: int = 15
    request_timeout_seconds: int = 10
    timezone: str = "UTC"

    class Config:
        env_prefix = "PRUSA_XL_"
        case_sensitive = False

    # PURPOSE: Validate collector poll interval.
    # DEPENDENCIES: BaseServiceConfig.validate_positive_int
    # MODIFICATION NOTES: v0.1 - Ensure poll interval is positive.
    @field_validator("poll_interval_seconds")
    @classmethod
    def validate_poll_interval(cls, value: int) -> int:
        """Ensure polling interval is a positive integer."""
        return cls.validate_positive_int(value, field_name="poll_interval_seconds")

    # PURPOSE: Validate auth type.
    # DEPENDENCIES: pydantic.field_validator
    # MODIFICATION NOTES: v0.1 - Allow only supported auth types.
    @field_validator("auth_type")
    @classmethod
    def validate_auth_type(cls, value: str) -> str:
        """Validate auth type values."""
        allowed = {"none", "basic", "digest", "bearer"}
        normalized = (value or "none").strip().lower()
        if normalized not in allowed:
            raise ValueError(f"auth_type must be one of {sorted(allowed)}")
        return normalized

    # PURPOSE: Validate request timeout.
    # DEPENDENCIES: BaseServiceConfig.validate_positive_int
    # MODIFICATION NOTES: v0.1 - Ensure request timeout is positive.
    @field_validator("request_timeout_seconds")
    @classmethod
    def validate_request_timeout(cls, value: int) -> int:
        """Ensure request timeout is a positive integer."""
        return cls.validate_positive_int(value, field_name="request_timeout_seconds")

    # PURPOSE: Validate printer identifier string.
    # DEPENDENCIES: BaseServiceConfig.validate_non_empty_string
    # MODIFICATION NOTES: v0.1 - Prevent empty printer IDs.
    @field_validator("printer_id")
    @classmethod
    def validate_printer_id(cls, value: str) -> str:
        """Ensure printer_id is non-empty."""
        return cls.validate_non_empty_string(value, field_name="printer_id") or ""

    # PURPOSE: Validate optional log path format.
    # DEPENDENCIES: BaseServiceConfig.validate_path
    # MODIFICATION NOTES: v0.1 - Allow optional log path validation.
    @field_validator("log_path")
    @classmethod
    def validate_log_path(cls, value: Optional[str]) -> Optional[str]:
        """Validate log path if provided."""
        if value is None:
            return value
        path = cls.validate_path(value, must_exist=False, must_be_creatable=False)
        return str(path)

    # PURPOSE: Ensure required network settings are present.
    # DEPENDENCIES: pydantic.model_validator
    # MODIFICATION NOTES: v0.1 - Require endpoint info for network source.
    @model_validator(mode="after")
    def validate_network_settings(self) -> "PrusaXLCollectorConfig":
        """Validate network settings when source_type is network_api."""
        if self.source_type != "network_api":
            return self

        has_direct_url = bool(self.payload_url)
        has_endpoints = bool(
            self.status_endpoint
            or self.errors_endpoint
            or self.telemetry_endpoint
            or self.info_endpoint
            or self.storage_endpoint
        )
        if not has_direct_url and not has_endpoints:
            raise ValueError("network_api requires payload_url or endpoint paths")
        if has_endpoints and not self.base_url:
            raise ValueError("network_api endpoint paths require base_url")
        if self.auth_type in {"basic", "digest"} and (not self.username or not self.password):
            raise ValueError("basic auth requires username and password")
        if self.auth_type == "bearer" and not self.bearer_token:
            raise ValueError("bearer auth requires bearer_token")
        return self
