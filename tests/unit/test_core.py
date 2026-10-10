import json
import logging

import pytest

from app.core.config import Settings
from app.core.errors import ConfigurationError
from app.core.logging import JsonFormatter


def test_settings_load_from_environment_mapping() -> None:
    settings = Settings.from_env(
        {
            "TRUSTAI_ENV": "test",
            "TRUSTAI_LOG_LEVEL": "debug",
            "TRUSTAI_MAX_DATASET_CASES": "25",
        }
    )

    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.max_dataset_cases == 25


def test_settings_reject_invalid_limits() -> None:
    with pytest.raises(ConfigurationError, match="Invalid TrustAI"):
        Settings.from_env({"TRUSTAI_MAX_DATASET_BYTES": "0"})


def test_json_formatter_redacts_credentials_and_omits_unapproved_fields() -> None:
    record = logging.LogRecord(
        "trustai.test",
        logging.INFO,
        "",
        0,
        "request api_key=%s Authorization: Bearer %s",
        ("top-secret", "token-value"),
        None,
    )
    record.input = "private prompt"

    formatted = JsonFormatter().format(record)
    payload = json.loads(formatted)

    assert "top-secret" not in formatted
    assert "token-value" not in formatted
    assert "private prompt" not in formatted
    assert "[REDACTED]" in payload["message"]
    assert "input" not in payload
