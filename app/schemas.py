"""Validated data contracts shared by the TrustAI foundation."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvaluationCase(BaseModel):
    """One user-provided test case; reference data is optional by design."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    case_id: str = Field(min_length=1, max_length=128)
    input: str | dict[str, Any]
    reference_answer: str | None = None
    context: str | list[str] | None = None
    expected_output_schema: dict[str, Any] | None = None
    expected_behavior: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LoadedDataset(BaseModel):
    """An immutable dataset snapshot identified by the hash of its source bytes."""

    model_config = ConfigDict(frozen=True)

    dataset_id: str
    version: str
    cases: tuple[EvaluationCase, ...]
