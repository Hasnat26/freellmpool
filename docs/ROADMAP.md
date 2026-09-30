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
