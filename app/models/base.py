"""Provider contract and common invocation/response schemas."""

from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field


class ModelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input: str | dict[str, Any]
    context: str | list[str] | None = None


class ModelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: str
    provider: str
    model: str
    latency_ms: float = Field(ge=0)
    usage: dict[str, int] | None = None


class ModelProvider(Protocol):
    """Minimal async interface implemented by mock and real model adapters."""

    provider_id: str
    model_id: str

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate one response or raise a classified provider error."""
