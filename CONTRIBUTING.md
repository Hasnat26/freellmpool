# Contributing to Industrial RFQ Intelligence

Industrial RFQ Intelligence is an evidence-aware engineering decision-support prototype for technical and commercial review of industrial RFQs and vendor quotations.

## Development setup

```bash
git clone https://github.com/Hasnat26/industrial-rfq-intelligence
cd industrial-rfq-intelligence
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
ruff check .
pytest
```

The primary product implementation is under `src/freellmpool/industrial.py` and `src/freellmpool/industrial_report.py`. The `freellmpool` package namespace is retained as an internal compatibility namespace; it is not the product identity.

## Product contribution rules

- Keep engineering compliance decisions deterministic and testable.
- LLM-assisted extraction must remain separate from compliance judgment.
- Missing or conflicting evidence must fail closed rather than silently pass.
- Preserve source/provenance information whenever extracted claims enter the comparison layer.
- Do not add autonomous procurement decisions, plant/control-system actions, or production credentials.
- Add regression tests for new comparison, normalization, evidence, or report behavior.

## Focused validation

```bash
ruff check .
pytest
python -m mypy --follow-imports=skip src/freellmpool/industrial.py src/freellmpool/industrial_report.py
industrial-rfq-intelligence industrial-rfq --input examples/industrial_rfq/sample_input.json --json
industrial-rfq-intelligence industrial-rfq --input examples/industrial_rfq/sample_input.json --markdown
```

Actual CI execution status is reported separately in `docs/VALIDATION.md`. Do not describe a configured workflow as a passed workflow without execution evidence.
