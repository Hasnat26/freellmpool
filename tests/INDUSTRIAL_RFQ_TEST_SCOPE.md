# Industrial RFQ test scope

The repository contains historical tests from the original gateway implementation. They are retained as source history/reference material but are not part of the active Industrial RFQ product validation boundary.

## Active product tests

The default pytest configuration intentionally runs only:

- `tests/test_industrial_demo.py`
- `tests/test_industrial_report.py`

These tests cover the current Industrial RFQ workflow, including:

- RFQ/vendor input validation;
- claim-status defaults;
- missing evidence;
- contradiction handling;
- engineering unit normalization;
- relational operators, ranges, and tolerances;
- deterministic compliance results;
- commercial data;
- evidence registers;
- report rendering;
- LLM extraction boundary behavior.

The CI workflow also performs native CLI JSON/Markdown smoke tests, focused mypy checks for the Industrial RFQ modules, and wheel installation/smoke validation.

## Historical compatibility tests

The remaining files under `tests/` cover legacy provider-routing, proxy, MCP, OpenCode, catalog, plugin, gateway, and release infrastructure. They are not used by the default product test suite because those surfaces are no longer the public product scope.

This boundary is deliberate. It prevents legacy gateway behavior from becoming an implicit acceptance criterion for Industrial RFQ Intelligence.

## Validation rule

A green Industrial RFQ test run means the current product boundary passed the configured tests. It does not mean every retained historical compatibility module is fully validated.

The repository does not claim CI success until an actual GitHub Actions run provides execution evidence.
