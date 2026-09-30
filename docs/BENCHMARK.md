# Industrial RFQ Intelligence Benchmark

P3-M21 defines a small, versioned benchmark for measuring the two reliability boundaries separately:

1. **LLM/document extraction quality** — whether requirements, vendor fields, evidence, and provenance are extracted correctly.
2. **Deterministic engineering comparison quality** — whether already-structured facts produce the expected compliance and claim-status results.

## Dataset

`examples/industrial_rfq/benchmark.json` contains five representative scenarios:

| Case | Source/scenario | Coverage |
|---|---|---|
| TXT-01 | Plain text | baseline extraction and technical deviation |
| PDF-02 | Page-aware PDF text fixture | source/page provenance and unit normalization |
| TABLE-03 | Table-heavy quotation | table/cell provenance and engineering units |
| AMB-04 | Ambiguous text | unsupported/non-computable wording remains reviewable |
| CON-05 | Contradictory quotation | conflicting claims become UNVERIFIED/CONTRADICTED |

The PDF case is represented at the **post-text-extraction fixture boundary**. It does not claim that OCR or binary PDF ingestion is benchmarked; scanned-document OCR remains outside the current product scope.

## Metrics

Extraction metrics are calculated independently:

- requirement precision/recall;
- vendor-field precision/recall;
- evidence coverage;
- structured provenance coverage.

Deterministic metrics are calculated against gold structured inputs:

- compliance status accuracy;
- claim-status accuracy for cases that define expected claim status.

This separation prevents a strong deterministic engine from masking extraction errors.

## Acceptance principle

Benchmark scores are evidence about the supplied fixture set, not proof of general engineering accuracy. Expansion of the dataset is required before making broader performance claims.

The benchmark does not rank suppliers, select a winner, or make a procurement recommendation.