# PURPOSE: Validate OctoPrint client header behavior.
# DEPENDENCIES: services.octoprint.client
# MODIFICATION NOTES: v0.1 - Initial client test stub.

"""Tests for OctoPrint client."""

import pytest

from services.octoprint.config import OctoPrintConfig


# PURPOSE: Ensure missing API key raises validation error.
# DEPENDENCIES: OctoPrintConfig
# MODIFICATION NOTES: v0.1 - API key validation test.
def test_octoprint_config_requires_api_key() -> None:
    with pytest.raises(ValueError):
        OctoPrintConfig(api_key="")
