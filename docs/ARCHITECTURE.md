# Architecture

## Product architecture

Industrial RFQ Intelligence separates interpretation from engineering judgment:

```text
RFQ / specification / quotations
            |
            v
Document ingestion + provenance
            |
            v
LLM-assisted extraction
            |
            v
Structured claims + evidence
            |
            v
Normalization
            |
            v
Deterministic engineering/commercial comparison
            |
            v
Evidence register + review actions
            |
            v
Engineering report
```

### Layer 1 — ingestion

PDF, TXT, and Markdown sources are converted into structured document content while preserving available source/page provenance.

### Layer 2 — extraction

The LLM may identify candidate parameters, values, commercial terms, and evidence references. Extraction output is treated as a claim, not as engineering truth.

### Layer 3 — deterministic comparison

Normalized values are evaluated against explicit RFQ requirements using deterministic rules. Supported engineering comparisons include equality, relational operators, inclusive ranges, and percentage tolerances where compatible units permit safe comparison.

### Layer 4 — evidence

Each claim carries a status such as VERIFIED, PARTIALLY VERIFIED, UNVERIFIED, INFERENCE, ASSUMPTION, or CONTRADICTED. Missing evidence and materially conflicting claims fail closed to UNVERIFIED.

### Layer 5 — reporting

The report exposes technical compliance, commercial comparison, evidence references, and review actions. Engineers remain the decision makers.

## Compatibility boundary

The repository retains the `freellmpool` Python package namespace because the original implementation contains a broad internal API surface. This is an implementation compatibility boundary, not the public product identity.

New Industrial RFQ functionality should be added under the industrial modules and should not introduce new dependencies on legacy gateway behavior unless technically necessary.
