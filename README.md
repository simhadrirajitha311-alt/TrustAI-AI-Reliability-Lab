# TrustAI - AI Reliability Lab

TrustAI is an incremental, reproducible toolkit for evaluating AI systems. The repository is at **Phase 1: Python foundation**; it currently provides validated evaluation-case schemas, bounded JSON/JSONL dataset loading, a deterministic offline model provider, environment configuration, and privacy-conscious structured logging. It does not yet run or persist evaluations and makes no claims about model quality.

## Quick start

Requires Python 3.12 or newer. The current development environment uses Python 3.14.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

To use the loader from Python:

```python
from app.datasets.loader import load_dataset

dataset = load_dataset(
	b'{"cases":[{"case_id":"greeting-1","input":"Say hello"}]}',
	filename="greetings.json",
)
print(dataset.dataset_id, dataset.version, len(dataset.cases))
```

The loader accepts JSON arrays or JSON objects containing a `cases` array, and JSONL with one case object per non-empty line. Dataset versions are SHA-256 hashes of the original bytes, so changing whitespace also creates a different version. Upload size and case counts are bounded; parsing never opens a path supplied by a caller.

## Development status

- Implemented: Phase 1 schemas, configuration, error types, structured logging, dataset loader, mock provider, and unit tests.
- Not implemented yet: metric engine, evaluation execution or persistence, API, real provider, UI, regression checks, reports, and deployment.

The mock provider is for deterministic local development only. Its output is not a benchmark result. Follow-up phases will add testable capabilities without presenting unmeasured or invented scores as results.