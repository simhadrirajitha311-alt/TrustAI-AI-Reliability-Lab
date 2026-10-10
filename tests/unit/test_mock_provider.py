import asyncio

from app.models.base import ModelRequest
from app.models.mock import MockProvider


def test_mock_provider_returns_configured_deterministic_output() -> None:
    provider = MockProvider({"hello": "Hi there"})
    request = ModelRequest(input="hello")

    first = asyncio.run(provider.generate(request))
    second = asyncio.run(provider.generate(request))

    assert first.output == second.output == "Hi there"
    assert first.provider == "mock"
    assert first.model == "mock-v1"


def test_mock_provider_has_stable_fallback_for_structured_input() -> None:
    response = asyncio.run(MockProvider().generate(ModelRequest(input={"question": "2+2?"})))

    assert response.output == 'Mock response: {"question":"2+2?"}'
    assert response.usage is None
