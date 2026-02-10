# PURPOSE: Validate Prusa XL collector config behavior.
# DEPENDENCIES: pytest, services.collector.config
# MODIFICATION NOTES: v0.1 - Initial config validation tests.

"""Tests for Prusa XL collector configuration."""

import pytest
from services.collector.config import PrusaXLCollectorConfig


# PURPOSE: Ensure network source requires endpoint configuration.
# DEPENDENCIES: PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Network validation test.
def test_network_api_requires_endpoint_or_payload_url() -> None:
    with pytest.raises(ValueError):
        PrusaXLCollectorConfig(source_type="network_api")


# PURPOSE: Allow network API with direct payload URL.
# DEPENDENCIES: PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Direct URL validation test.
def test_network_api_allows_payload_url() -> None:
    config = PrusaXLCollectorConfig(
        source_type="network_api",
        payload_url="https://printer.example/api/diagnostics"
    )
    assert config.payload_url


# PURPOSE: Require base_url when endpoint paths are used.
# DEPENDENCIES: PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Endpoint path validation test.
def test_network_api_requires_base_url_with_endpoints() -> None:
    with pytest.raises(ValueError):
        PrusaXLCollectorConfig(source_type="network_api", status_endpoint="/api/status")


# PURPOSE: Require username/password for basic auth.
# DEPENDENCIES: PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Basic auth validation test.
def test_network_api_requires_basic_auth_credentials() -> None:
    with pytest.raises(ValueError):
        PrusaXLCollectorConfig(
            source_type="network_api",
            payload_url="https://printer.example/api/diagnostics",
            auth_type="basic"
        )


# PURPOSE: Require username/password for digest auth.
# DEPENDENCIES: PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Digest auth validation test.
def test_network_api_requires_digest_auth_credentials() -> None:
    with pytest.raises(ValueError):
        PrusaXLCollectorConfig(
            source_type="network_api",
            payload_url="https://printer.example/api/diagnostics",
            auth_type="digest"
        )


# PURPOSE: Require bearer token for bearer auth.
# DEPENDENCIES: PrusaXLCollectorConfig
# MODIFICATION NOTES: v0.1 - Bearer auth validation test.
def test_network_api_requires_bearer_token() -> None:
    with pytest.raises(ValueError):
        PrusaXLCollectorConfig(
            source_type="network_api",
            payload_url="https://printer.example/api/diagnostics",
            auth_type="bearer"
        )
