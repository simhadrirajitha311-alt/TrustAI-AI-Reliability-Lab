"""Small, explicit environment-based settings for local and deployed use."""

import os
from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.core.errors import ConfigurationError


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    max_dataset_bytes: int = Field(default=5 * 1024 * 1024, gt=0, le=50 * 1024 * 1024)
    max_dataset_cases: int = Field(default=10_000, gt=0, le=100_000)
    provider_timeout_seconds: float = Field(default=30, gt=0, le=300)

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "Settings":
        """Read only the documented TrustAI settings, without loading secrets."""
        values = os.environ if environ is None else environ
        try:
            return cls(
                environment=values.get("TRUSTAI_ENV", "development"),
                log_level=values.get("TRUSTAI_LOG_LEVEL", "INFO").upper(),
                max_dataset_bytes=values.get("TRUSTAI_MAX_DATASET_BYTES", 5 * 1024 * 1024),
                max_dataset_cases=values.get("TRUSTAI_MAX_DATASET_CASES", 10_000),
                provider_timeout_seconds=values.get("TRUSTAI_PROVIDER_TIMEOUT_SECONDS", 30),
            )
        except ValidationError as exc:
            raise ConfigurationError(f"Invalid TrustAI environment configuration: {exc}") from exc
