"""Domain exceptions with stable meanings for callers and API mapping."""


class TrustAIError(Exception):
    """Base class for expected TrustAI failures."""


class DatasetFormatError(TrustAIError):
    """The supplied dataset bytes are unsupported or malformed."""


class DatasetValidationError(TrustAIError):
    """A dataset case is invalid or violates dataset-level constraints."""


class ProviderError(TrustAIError):
    """A model provider could not produce a valid response."""


class ConfigurationError(TrustAIError):
    """Environment configuration is invalid."""
