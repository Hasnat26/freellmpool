# End-to-End Portfolio Demo

Run the checked-in sample from the repository root:

```bash
python -m pip install -e ".[dev]"
industrial-rfq-intelligence industrial-rfq --input examples/industrial_rfq/sample_input.json --markdown > /tmp/industrial-rfq-report.md
industrial-rfq-intelligence industrial-rfq --input examples/industrial_rfq/sample_input.json --json > /tmp/industrial-rfq-report.json
```

The sample demonstrates requirements, vendor comparison, engineering deviation detection, commercial fields, evidence/provenance, and human review boundaries.

Vendor A uses an equivalent 0.415 kV representation for the 415 V requirement. Vendor B intentionally contains an IE2 efficiency-class deviation against the IE3 requirement. The workflow reports the difference but does not choose a supplier.

For a supported document, use:

```bash
industrial-rfq-intelligence industrial-document specification.pdf
```

The current implementation supports PDF/TXT/Markdown ingestion and page-aware PDF provenance. OCR for scanned/image-only documents is outside the current scope.

The portfolio boundary is: LLM-assisted extraction -> deterministic comparison -> evidence register -> human engineering review.
