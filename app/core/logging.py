"""JSON logging that excludes prompt and credential fields by default."""

import json
import logging
import re
from datetime import UTC, datetime
from typing import Any

_SAFE_FIELDS = (
    "event",
    "trace_id",
    "run_id",
    "case_id",
    "provider",
    "model",
    "status",
    "duration_ms",
)
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|secret|password)(\s*[=:]\s*)(['\"]?)([^'\"\s,;]+)"
)
_BEARER_TOKEN = re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/-]+=*")
_COMMON_API_KEY = re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")


class JsonFormatter(logging.Formatter):
    """Emit a compact JSON object with an allowlist of structured attributes."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": _redact(record.getMessage()),
        }
        for field in _SAFE_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        return json.dumps(payload, ensure_ascii=True, separators=(",", ":"))


def _redact(message: str) -> str:
    message = _SECRET_ASSIGNMENT.sub(r"\1\2[REDACTED]", message)
    message = _BEARER_TOKEN.sub(r"\1[REDACTED]", message)
    return _COMMON_API_KEY.sub("[REDACTED]", message)


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger once with structured output."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
