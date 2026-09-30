# Security Policy

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for security-sensitive issues. Do not include credentials, provider keys, prompts, customer data, or other sensitive information in a public issue.

For a product security issue, include the affected version or commit, a minimal reproduction, impact, and suggested mitigation where available.

## Product security boundaries

Industrial RFQ Intelligence is a decision-support prototype. It is not an autonomous control-system, procurement, or production-execution system.

The product must not:

- modify PLC/DCS logic or plant control parameters;
- execute unattended procurement decisions;
- require production credentials;
- treat an LLM-generated statement as verified engineering evidence;
- silently convert missing, ambiguous, or conflicting evidence into compliance.

The deterministic engineering layer is responsible for compliance status. The evidence layer records provenance and review requirements.

The internal `freellmpool` namespace remains for implementation compatibility and should not be treated as the public product identity.

## Validation

Repository automation currently focuses on:

- Ruff linting;
- focused mypy validation;
- pytest and coverage;
- package/wheel smoke tests;
- Industrial RFQ JSON and Markdown CLI smoke tests; and
- CodeQL/dependency security workflows.

See `docs/VALIDATION.md` and `docs/CI_POLICY.md` for the current validation policy. Configured checks are not represented as passed until an actual workflow execution provides evidence.
