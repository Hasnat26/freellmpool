# Portfolio Evidence — Industrial RFQ Intelligence

## 1. Engineering problem
Industrial RFQs and vendor quotations often arrive as semi-structured PDFs, tables, spreadsheets, and text. An engineer must reconcile specification requirements with vendor claims, normalize units and terminology, identify deviations, retain source evidence, and decide what still needs human review.

This project demonstrates a bounded decision-support workflow for a concrete portfolio case: **415 V induction motors and VFD supply**.

The prototype accepts structured RFQ/quotation data and can also ingest PDF, TXT, and Markdown text before extraction. It produces a technical-commercial review rather than an autonomous purchasing decision.

## 2. Architecture
```text
RFQ / vendor documents
        |
        v
Document ingestion + provenance
        |
        v
LLM-assisted grounded extraction
        |
        v
Schema validation + normalization
        |
        v
Deterministic engineering comparison
        +----> COMPLIANT
        +----> DEVIATION
        +----> UNVERIFIED
        |
        v
Evidence / claim-status register
        |
        v
Human engineering review report
```

The design separates probabilistic extraction from deterministic engineering comparison.

**AI reads and structures. Deterministic logic compares. Evidence explains. Engineers decide.**

## 3. Reproducible end-to-end demo
Install the project and run the checked-in sample:

```bash
python -m pip install -e ".[dev]"

industrial-rfq-intelligence industrial-rfq \
  --input examples/industrial_rfq/sample_input.json \
  --markdown > /tmp/industrial-rfq-report.md
```

The same input can be rendered as JSON:

```bash
industrial-rfq-intelligence industrial-rfq \
  --input examples/industrial_rfq/sample_input.json \
  --json > /tmp/industrial-rfq-report.json
```

The repository contains the input fixture and generated Markdown report fixture under examples/industrial_rfq/. The sample intentionally contains both a compliant-style technical offer and a technical deviation so the comparison path is visible without external vendor data.

For document ingestion, a supported PDF/TXT/Markdown source can be passed through the document command:

```bash
industrial-rfq-intelligence industrial-document specification.pdf
```

Scanned/image-only OCR is outside the current implementation scope.

## 4. Deterministic controls
- Requirement/vendor values are schema-validated.
- Supported engineering units are normalized before comparison.
- Supported semantics include equality, >=, <=, >, <, inclusive ranges, and percentage tolerances.
- Incompatible dimensions are rejected rather than guessed.
- Unsupported expressions fall back to normalized exact matching.
- Missing evidence forces the affected claim to UNVERIFIED.
- Conflicting claims for the same vendor/parameter force review and are not treated as compliant.
- Commercial fields are normalized and surfaced as review risks.
- The system does not rank vendors or select a winner.

These controls make the prototype suitable as an engineering-review demonstration, not as an autonomous procurement engine.

## 5. Evidence policy
Every material vendor/commercial claim has an explicit claim status:

- VERIFIED
- PARTIALLY VERIFIED
- UNVERIFIED
- INFERENCE
- ASSUMPTION
- CONTRADICTED

A claim is not considered verified merely because a value was extracted. The structured input must explicitly identify a claim as VERIFIED and provide evidence/provenance. Missing evidence forces UNVERIFIED.

For document-derived values, source/page provenance is preserved. The model is not permitted to convert an inferred or unsupported statement into verified engineering evidence.

## 6. Human-review boundary
The prototype intentionally stops before high-consequence autonomous action.

It does not:
- approve or purchase equipment;
- select a supplier;
- modify PLC/DCS logic;
- operate a plant;
- use production credentials;
- certify engineering compliance;
- replace qualified engineering review.

The reviewer workflow models UPLOAD → EXTRACTION → REVIEW → REPORT, with explicit human approval required before the report state.

## 7. What is measurable
The portfolio claims are tied to repository artifacts rather than marketing language:

| Capability | Inspectable evidence |
|---|---|
| RFQ schema validation | src/freellmpool/industrial.py + tests |
| Deterministic compliance | engineering comparison implementation + tests |
| Unit/parameter normalization | engineering normalization tests |
| Evidence/provenance | provenance models, validation, and fixtures |
| Contradiction handling | conflict validation and regression tests |
| Commercial-risk review | commercial normalization/review implementation |
| PDF/TXT/Markdown ingestion | document ingestion implementation + security tests |
| Reviewer boundary | src/freellmpool/reviewer_workflow.py + tests |
| Report generation | src/freellmpool/industrial_report.py + sample report |
| Package/CLI path | pyproject.toml + CLI smoke configuration |
| Security/dependency controls | .github/workflows/security.yml, Dependabot, security tests |
| Release discipline | docs/RELEASE_CHECKLIST.md |

Repository configuration is not the same as execution evidence. The project currently has no verified GitHub Actions green-run evidence for P3-M14. Portfolio material must not describe CI as successfully executed until a real workflow run is captured.

## 8. Recruiter-facing positioning
This repository is best described as an industrial engineering AI decision-support prototype demonstrating:
1. a concrete EPC/procurement workflow;
2. AI-assisted document understanding;
3. deterministic engineering controls;
4. evidence and provenance handling;
5. human-in-the-loop review;
6. security and release-boundary thinking.

The engineering value is not a generic chatbot. The portfolio signal is the separation of extraction, deterministic comparison, evidence, and human approval in a workflow familiar to industrial automation/EPC environments.

## 9. Current limitations
The current prototype does not claim production readiness. Known limitations include:
- OCR for scanned documents is not implemented;
- table extraction is limited compared with a production document-intelligence stack;
- the engineering parameter vocabulary is intentionally bounded;
- commercial risk thresholds are review heuristics, not procurement selection rules;
- real CI execution evidence remains pending under P3-M14;
- the Python implementation namespace remains freellmpool for compatibility and is not the intended product identity.

## 10. Portfolio evidence rule
Any future portfolio statement should be backed by one of:
- reproducible local execution;
- an actual GitHub Actions result;
- checked-in tests/fixtures;
- directly inspectable source/configuration.

Do not convert planned, configured, or inferred capabilities into claims of successful execution.

## 11. One-line project summary
**Industrial RFQ Intelligence turns RFQ and vendor-quotation data into evidence-aware engineering review outputs using LLM-assisted extraction and deterministic compliance logic, while keeping final decisions with engineers.**