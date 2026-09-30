# CI / release workflow policy

The repository intentionally keeps only product-relevant automation:

- `.github/workflows/ci.yml` — Python validation, tests, type checking, packaging, and Industrial RFQ CLI smoke tests.
- `.github/workflows/codeql.yml` — static security analysis.
- `.github/workflows/security.yml` — dependency/security validation.

Legacy gateway-specific publication and deployment workflows were removed during repository identity cleanup.

The project is currently a portfolio engineering prototype rather than a published MCP/plugin/container distribution. Release automation for those legacy surfaces is deliberately out of scope.

Product CI should validate the current repository as **Industrial RFQ Intelligence**, while the internal `freellmpool` Python namespace remains only as a compatibility implementation detail.
