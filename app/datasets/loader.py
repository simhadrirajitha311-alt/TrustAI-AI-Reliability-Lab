"""Bounded JSON and JSONL dataset ingestion from caller-supplied bytes."""

import hashlib
import json
from pathlib import PurePath
from typing import Any

from pydantic import ValidationError

from app.core.errors import DatasetFormatError, DatasetValidationError
from app.schemas import EvaluationCase, LoadedDataset

DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_MAX_CASES = 10_000
SUPPORTED_SUFFIXES = {".json", ".jsonl"}


def load_dataset(
    content: bytes,
    filename: str,
    *,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_cases: int = DEFAULT_MAX_CASES,
) -> LoadedDataset:
    """Parse and validate dataset bytes; filename is used only to select a format."""
    suffix = PurePath(filename).suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise DatasetFormatError("Dataset filename must end in .json or .jsonl")
    if len(content) > max_bytes:
        raise DatasetFormatError(f"Dataset exceeds the {max_bytes}-byte upload limit")

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DatasetFormatError("Dataset must be UTF-8 encoded") from exc

    rows = _parse_jsonl(text) if suffix == ".jsonl" else _parse_json(text)
    if not rows:
        raise DatasetValidationError("Dataset must contain at least one case")
    if len(rows) > max_cases:
        raise DatasetFormatError(f"Dataset exceeds the {max_cases}-case limit")

    cases = tuple(_validate_case(row, index, suffix) for index, row in enumerate(rows, start=1))
    case_ids = [case.case_id for case in cases]
    if len(set(case_ids)) != len(case_ids):
        raise DatasetValidationError("Dataset contains duplicate case_id values")

    version = f"sha256:{hashlib.sha256(content).hexdigest()}"
    dataset_id = f"dataset-{hashlib.sha256(content).hexdigest()[:12]}"
    return LoadedDataset(dataset_id=dataset_id, version=version, cases=cases)


def _parse_json(text: str) -> list[Any]:
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DatasetFormatError(f"Invalid JSON at line {exc.lineno}, column {exc.colno}") from exc
    if isinstance(document, list):
        return document
    if isinstance(document, dict) and isinstance(document.get("cases"), list):
        return document["cases"]
    raise DatasetFormatError("JSON dataset must be an array or an object with a cases array")


def _parse_jsonl(text: str) -> list[Any]:
    rows = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            message = f"Invalid JSONL at line {line_number}, column {exc.colno}"
            raise DatasetFormatError(message) from exc
    return rows


def _validate_case(row: Any, index: int, suffix: str) -> EvaluationCase:
    location = f"line {index}" if suffix == ".jsonl" else f"case {index}"
    if not isinstance(row, dict):
        raise DatasetValidationError(f"{location} must be a JSON object")
    try:
        return EvaluationCase.model_validate(row)
    except ValidationError as exc:
        details = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors(include_url=False)
        )
        raise DatasetValidationError(f"Invalid {location}: {details}") from exc
