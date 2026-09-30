# Release Checklist

This checklist is for the current Industrial RFQ Intelligence distribution.

## Verify

```bash
python3 -m pip install -e ".[dev]"
ruff check .
python3 -m mypy --follow-imports=skip src/freellmpool/industrial.py src/freellmpool/industrial_report.py
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m pytest --cov=freellmpool --cov-branch --cov-report=term-missing --cov-report=json:.coverage.json
python3 scripts/check_coverage.py .coverage.json
python3 -m build
python3 -m twine check dist/*.whl dist/*.tar.gz
industrial-rfq-intelligence --version
industrial-rfq-intelligence industrial-rfq --input examples/industrial_rfq/sample_input.json --json
industrial-rfq-intelligence industrial-rfq --input examples/industrial_rfq/sample_input.json --markdown
```

## Release identity

- Distribution name: `industrial-rfq-intelligence`
- Native executable: `industrial-rfq-intelligence`
- Product: Industrial RFQ Intelligence
- Internal compatibility namespace: `freellmpool`

Do not describe the compatibility namespace as the public product identity.

## Evidence requirements

Before publishing a release, confirm:

1. tests and packaging checks actually executed;
2. the Industrial RFQ CLI smoke tests completed successfully;
3. product documentation matches the implemented behavior;
4. no release artifact claims unsupported MCP/plugin/gateway publication;
5. no inferred engineering claim is presented as verified evidence.

CI configuration alone is not evidence of a successful release check. Record the actual workflow run when available.
