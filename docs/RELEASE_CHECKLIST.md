# Industrial RFQ Intelligence — Release Checklist

This checklist defines the minimum evidence required before publishing a release or making a package-installation claim.

## 1. Repository state

- [ ] Working tree changes are committed.
- [ ] README describes the Industrial RFQ product, not a generic LLM gateway.
- [ ] No release documentation claims unsupported provider capacity, gateway functionality, MCP listings, or production deployment.
- [ ] Version in `pyproject.toml` is the intended release version.
- [ ] Release notes, if published, contain only verified changes.

## 2. Source and security gates

- [ ] Ruff passes.
- [ ] Industrial RFQ mypy check passes.
- [ ] Full pytest suite passes.
- [ ] Security workflow passes Bandit, pip-audit and zizmor gates.
- [ ] Container security audit passes when the Docker image is built.
- [ ] No active security exception is used to hide a finding.

## 3. Package artifacts

Run:

```bash
python -m build
python -m twine check dist/*.whl dist/*.tar.gz
```

Verify:

- exactly one intended wheel is present;
- exactly one intended sdist is present;
- wheel contains the `freellmpool` runtime package required by the current compatibility namespace;
- sdist contains `pyproject.toml` and source files;
- no obsolete gateway/provider/MCP release assets are packaged.

## 4. Native CLI installation

Test both artifacts in a clean virtual environment:

```bash
python -m venv /tmp/industrial-rfq-release-smoke
/tmp/industrial-rfq-release-smoke/bin/python -m pip install dist/*.whl
/tmp/industrial-rfq-release-smoke/bin/industrial-rfq-intelligence --version
/tmp/industrial-rfq-release-smoke/bin/industrial-rfq-intelligence industrial-rfq \
  --input examples/industrial_rfq/sample_input.json --markdown
```

Then repeat after replacing the wheel with the sdist.

The CLI smoke must produce a non-empty report.

## 5. Product boundary

A release must preserve these boundaries:

- LLM output is extraction assistance, not final compliance authority.
- Deterministic Python logic performs compliance classification.
- Evidence and claim status remain visible.
- Missing or unsupported evidence fails closed.
- The system does not autonomously select a vendor.
- The system does not modify PLC/DCS logic or operate plant equipment.
- No production credentials are required for the sample workflow.

## 6. CI evidence rule

Repository configuration is not evidence of execution.

Do not state that a release is CI-verified until a real GitHub Actions run for the relevant commit has completed successfully. P3-M14 tracks that execution evidence separately.

## 7. Release claim rule

Only publish claims supported by one of:

1. executable CI output;
2. reproducible local execution;
3. checked-in test/fixture evidence;
4. directly inspectable source/configuration evidence.

Do not convert planned functionality into an implemented-feature claim.
