# Evidence and provenance policy

Industrial RFQ Intelligence treats evidence and provenance as separate but linked concepts.

Evidence is the human-readable citation retained with every extracted claim. Structured provenance is the normalized source location:

- `source`: source document or quotation identifier
- `page`: 1-based page number when applicable
- `section`: document section when known
- `table`: table identifier or label when known
- `cell`: table cell reference when known

Claims with missing evidence remain `UNVERIFIED`. Legacy evidence strings remain supported for backward compatibility; structured provenance is preserved whenever supplied.

For `VERIFIED` claims, the evidence must be explicit. The deterministic compliance engine does not infer missing provenance or upgrade an unverified claim.

Conflicting claims remain traceable through their individual evidence/provenance records and are handled as contradictions rather than silently selecting one source.

The LLM extraction boundary is expected to return evidence and structured provenance. Compliance status is still calculated by the deterministic comparison engine.
