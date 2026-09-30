# Industrial RFQ input schema

Current schema version: `1.0`.

`schema_version` is optional for backward compatibility. When omitted, the loader interprets the document as version `1.0`. If supplied, it must equal `1.0`; unsupported versions fail closed.

## Contract

The root must be a JSON object.

- `requirements`: required, non-empty array. Every item requires non-empty string `tag`, `parameter`, and `required`. Requirement tags must be unique.
- `vendor_data`: required, non-empty array. Every item requires non-empty string `vendor`, `parameter`, and `value`. `evidence` is optional but must be a string when supplied. Missing/empty evidence forces the claim to `UNVERIFIED`.
- `commercial_data`: optional array. Each item requires non-empty string `vendor`, `price`, `currency`, `lead_time`, `warranty`, and `payment_terms`. Evidence follows the same rule as technical claims.
- `claim_status`: optional. It defaults to `UNVERIFIED` and must be one of the evidence-policy statuses accepted by the loader.

Duplicate vendor/parameter claims are intentionally permitted because the deterministic engine uses them to detect contradictory quotation claims rather than discarding evidence.

Malformed JSON, wrong collection types, empty required collections, missing fields, wrong field types, duplicate requirement tags, invalid claim statuses, and unsupported schema versions are rejected with `ValueError`.

## Compatibility

Version `1.0` preserves pre-versioned Industrial RFQ JSON inputs by treating a missing `schema_version` as `1.0`. A future incompatible contract must use a new schema version rather than silently changing version `1.0` semantics.
