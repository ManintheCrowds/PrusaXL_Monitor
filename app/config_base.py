# PURPOSE: Base configuration with shared validation helpers.
# DEPENDENCIES: pydantic
# MODIFICATION NOTES: v0.1 - Initial base config for Prusa XL services.

"""Base service configuration with validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class BaseServiceConfig(BaseModel):
    """Base configuration with shared validation helpers."""

    class Config:
        extra = "ignore"

    @staticmethod
    def validate_positive_int(value: int, field_name: str) -> int:
        """Ensure integer is positive."""
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"{field_name} must be a positive integer")
        return value

    @staticmethod
    def validate_non_empty_string(value: Optional[str], field_name: str) -> Optional[str]:
        """Ensure string is non-empty if provided."""
        if value is None:
            return value
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
        return value.strip()

    @staticmethod
    def validate_path(
        value: str,
        must_exist: bool = False,
        must_be_creatable: bool = False
    ) -> Path:
        """Validate path format and optionally existence."""
        path = Path(value)
        if must_exist and not path.exists():
            raise ValueError(f"Path does not exist: {value}")
        if must_be_creatable and path.exists() and not path.is_dir():
            raise ValueError(f"Path is not a directory: {value}")
        return path
