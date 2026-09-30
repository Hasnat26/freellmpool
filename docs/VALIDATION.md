# Validation Status

## P3-M6 validation scope

The repository CI configuration now covers the industrial RFQ workflow with:

- Ruff linting;
- mypy type checking including `industrial.py` and `industrial_report.py`;
- the full pytest suite with coverage;
- package/wheel smoke testing;
- product-native CLI version smoke;
- industrial RFQ JSON CLI smoke;
- industrial RFQ Markdown CLI smoke.

The obsolete MCP manifest validation job was removed because the repository no longer contains the legacy `server.json` manifest.

## Current verification status

P3-M7 verification refresh: CI is expected to run on pushes to `main` and pull requests targeting `main`.

The validation commands are configured in GitHub Actions, but this environment has not independently executed the repository test suite.

The GitHub Actions API currently reports no workflow runs for the repository. Therefore this milestone does **not** claim that pytest, Ruff, mypy, or the CLI smoke tests have passed on GitHub.

Once Actions produces a run for the current `main` revision, the run should be checked for:

1. all Python-version test jobs passing;
2. Ruff passing;
3. mypy passing;
4. full pytest and coverage checks passing;
5. industrial CLI smoke passing;
6. wheel smoke passing.

This distinction is intentional: repository configuration is not treated as evidence of successful execution.

## Local execution limitation

The current working environment cannot reliably clone/fetch the repository through the local network path to GitHub, so local execution of the complete repository test suite is not represented as completed evidence.

## Validation principle

**Configured is not passed. A green execution result is required before claiming a test or CI check passed.**
