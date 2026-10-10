import hashlib

import pytest

from app.core.errors import DatasetFormatError, DatasetValidationError
from app.datasets.loader import load_dataset


def test_loads_json_dataset_and_hashes_exact_source_bytes() -> None:
    content = b'{"cases":[{"case_id":"a","input":"hello"}]}'

    dataset = load_dataset(content, "sample.json")

    assert dataset.version == f"sha256:{hashlib.sha256(content).hexdigest()}"
    assert dataset.cases[0].case_id == "a"
    assert dataset.cases[0].reference_answer is None


def test_loads_jsonl_and_skips_blank_lines() -> None:
    dataset = load_dataset(b'{"case_id":"a","input":"hello"}\n\n', "sample.jsonl")

    assert len(dataset.cases) == 1


@pytest.mark.parametrize(
    ("content", "filename", "error"),
    [
        (b"{bad", "cases.json", DatasetFormatError),
        (b"[]", "cases.json", DatasetValidationError),
        (b'[{"case_id":"a"}]', "cases.json", DatasetValidationError),
        (
            b'[{"case_id":"a","input":"x"},{"case_id":"a","input":"y"}]',
            "cases.json",
            DatasetValidationError,
        ),
        (b"{}", "cases.csv", DatasetFormatError),
    ],
)
def test_rejects_malformed_or_unsupported_dataset(
    content: bytes, filename: str, error: type[Exception]
) -> None:
    with pytest.raises(error):
        load_dataset(content, filename)


def test_enforces_upload_size_limit() -> None:
    with pytest.raises(DatasetFormatError, match="upload limit"):
        load_dataset(b'[{"case_id":"a","input":"x"}]', "cases.json", max_bytes=1)


def test_rejects_invalid_jsonl_with_source_line() -> None:
    with pytest.raises(DatasetFormatError, match="line 2"):
        load_dataset(b'{"case_id":"a","input":"ok"}\nnot json', "cases.jsonl")
