# Roadmap

Industrial RFQ Intelligence is an evidence-aware AI-assisted engineering decision-support system for industrial RFQs and vendor quotations.

## Product north star

**AI reads and structures. Deterministic logic compares. Evidence explains. Engineers decide.**

The system is designed around a concrete workflow:

RFQ/specification + vendor quotations → document ingestion → structured extraction → normalization → deterministic technical/commercial comparison → evidence register → engineering review report.

## Current scope

Implemented:

- structured Industrial RFQ input;
- vendor technical-value comparison;
- deterministic compliance operators, ranges, and percentage tolerances;
- engineering-unit normalization;
- missing-evidence fail-closed handling;
- conflicting-claim detection;
- commercial comparison;
- evidence register and review actions;
- PDF/TXT/Markdown document ingestion with provenance;
- LLM-assisted grounded extraction;
- Markdown/JSON engineering reports;
- native `industrial-rfq-intelligence` CLI.

## Next product work

1. Higher-quality table/document extraction.
2. OCR for scanned RFQs and quotations.
3. More engineering domains and parameter semantics.
4. Stronger provenance at page/table/cell level.
5. Structured commercial-risk and exception reporting.
6. Reviewer-oriented web/API workflow.
7. Benchmark datasets for evidence-aware RFQ extraction and comparison.

## Explicit non-goals

The product will not become:

- an autonomous purchasing agent;
- a PLC/DCS programming agent;
- a plant-control execution system;
- an unattended vendor-selection system;
- a system that presents inferred claims as verified evidence.

The legacy `freellmpool` runtime modules remain in the repository only where needed for implementation compatibility. They are not the product roadmap.

## Master milestone: P3-M14 → P3-M28 — Production Readiness

The next phase is tracked as one master milestone with sequential sub-milestones. Each sub-milestone should be completed and reported before starting the next.

### P3-M14 — CI execution evidence
- [ ] Determine why GitHub Actions reports zero workflow runs.
- [ ] Confirm workflow execution on push/PR.
- [ ] Capture the first real green run before claiming CI success.

### P3-M15 — CI/test configuration reconciliation
- [ ] Audit stale tests asserting deleted legacy workflows.
- [ ] Remove, rewrite, or quarantine obsolete assertions.
- [ ] Ensure active product validation cannot be masked by stale tests.

### P3-M16 — Industrial core API cleanup
- [ ] Audit legacy `freellmpool` identity leakage from product-facing output/API.
- [ ] Replace misleading legacy product strings where safe.
- [ ] Preserve the compatibility namespace only where required and documented.

### P3-M17 — Input/schema contract hardening
- [ ] Define a versioned Industrial RFQ input schema.
- [ ] Harden type/required-field validation.
- [ ] Add duplicate, malformed-value, and compatibility cases.
- [ ] Document schema compatibility expectations.

### P3-M18 — Evidence/provenance hardening
- [ ] Standardize source/page/section/table/cell provenance.
- [ ] Require explicit evidence for VERIFIED claims.
- [ ] Add provenance fixtures and regression tests.
- [ ] Preserve contradiction/review states end-to-end.

### P3-M19 — Engineering comparison expansion — DONE
- [x] Add parameter-specific engineering semantics.
- [x] Expand industrial unit coverage deliberately.
- [x] Add boundary, range, tolerance, and incompatible-dimension tests.
- [x] Keep unsupported semantics fail-closed.

### P3-M20 — Commercial/risk review layer — DONE
- [x] Normalize commercial fields.
- [x] Add delivery/warranty/payment exception flags.
- [x] Add evidence-aware commercial risk reporting.
- [x] Do not introduce supplier ranking or winner selection.

### P3-M21 — Document intelligence benchmark — DONE
- [x] Build a representative RFQ/quotation benchmark.
- [x] Include text, PDF, table-heavy, ambiguous, and contradictory cases.
- [x] Define extraction, provenance, and compliance metrics.
- [x] Separate LLM extraction quality from deterministic comparison quality.

### P3-M22 — Report quality and auditability — DONE
- [x] Add deterministic commercial-risk review to the human-readable report.
- [x] Preserve commercial provenance in the evidence register.
- [x] Add report auditability regression coverage.
- [x] Refresh the checked-in Markdown report fixture.

### P3-M23 — Reviewer workflow interface
- [ ] Design upload → extraction → review → report states.
- [ ] Define a local/API reviewer workflow.
- [ ] Keep human approval explicit.
- [ ] Exclude production credentials and unattended procurement actions.

### P3-M24 — Repository/public-surface cleanup
- [ ] Audit remaining legacy gateway docs, HTML, issue templates, scripts and assets.
- [ ] Remove/archive obsolete public material where safe.
- [ ] Resolve stale binary social-preview/docs assets.
- [ ] Recheck README, metadata, links and navigation.

### P3-M25 — Security/dependency gate
- [ ] Verify Bandit, pip-audit and zizmor/security workflows.
- [ ] Review dependency and supply-chain controls.
- [ ] Add security regression cases for document ingestion and LLM boundaries.

### P3-M26 — Packaging/release readiness
- [ ] Verify wheel/sdist contents and native CLI installation.
- [ ] Remove misleading legacy release claims.
- [ ] Define an Industrial RFQ release checklist.
- [ ] Only publish claims backed by executable evidence.

### P3-M27 — Portfolio/recruiter evidence pack
- [ ] Create a concise architecture/evidence page.
- [ ] Add one reproducible end-to-end demo path.
- [ ] Document engineering problem, deterministic controls, evidence policy and limitations.
- [ ] Keep all portfolio claims measurable and defensible.

### P3-M28 — Final acceptance gate
- [ ] Real CI green-run evidence.
- [ ] Benchmark acceptance evidence.
- [ ] Security gate evidence.
- [ ] Package/CLI smoke evidence.
- [ ] Sample report consistency.
- [ ] Public documentation audit.
- [ ] Final release/portfolio readiness review.

### Phase non-goals

This phase will not add:
- autonomous purchasing;
- vendor winner/ranking automation;
- PLC/DCS control execution;
- inferred claims presented as VERIFIED;
- production deployment or production credentials.

Current status: P3-M1 through P3-M13 and P3-M15 through P3-M22 complete. P3-M14 remains pending because real GitHub Actions execution evidence has not yet been captured. Next execution target: P3-M23.

