"""Deterministic, offline provider for development and automated tests."""

from time import perf_counter
from typing import Any

from app.models.base import ModelRequest, ModelResponse


class MockProvider:
    """Return configured responses by input, or a stable echo-style response."""

    provider_id = "mock"

    def __init__(self, responses: dict[str, str] | None = None) -> None:
        self.model_id = "mock-v1"
        self._responses = dict(responses or {})

    async def generate(self, request: ModelRequest) -> ModelResponse:
        started = perf_counter()
        key = _input_key(request.input)
        output = self._responses.get(key, f"Mock response: {key}")
        return ModelResponse(
            output=output,
            provider=self.provider_id,
            model=self.model_id,
            latency_ms=(perf_counter() - started) * 1000,
        )


def _input_key(value: str | dict[str, Any]) -> str:
    if isinstance(value, str):
        return value
    import json

    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
