# Reviewer Workflow

P3-M23 defines a local/API-neutral reviewer workflow:

**UPLOAD → EXTRACTION → REVIEW → REPORT**

The workflow is intentionally a state contract rather than a server framework. A UI or HTTP adapter can implement it without changing the engineering decision logic.

## State contract

| State | Purpose | Allowed next state |
|---|---|---|
| UPLOAD | Identify the RFQ/specification and quotation inputs | EXTRACTION |
| EXTRACTION | Run grounded document extraction | REVIEW |
| REVIEW | Engineer inspects claims, evidence, deviations and risk flags | REVIEW or REPORT |
| REPORT | Produce the reviewed report artifact | terminal |

The REVIEW → REPORT transition requires an explicit human approval flag. There is no implicit approval from successful extraction or deterministic compliance.

## Local/API mapping

An adapter can expose these operations:

- POST /sessions — create a review session.
- POST /sessions/{id}/input — attach an input reference.
- POST /sessions/{id}/extract — invoke the existing document/LLM extraction boundary.
- GET /sessions/{id} — return state and references.
- POST /sessions/{id}/approve — explicit human approval.
- POST /sessions/{id}/report — render the report after approval.

These are interface contracts only; P3-M23 does not add a web-server dependency.

## Security and control boundary

The reviewer workflow accepts document/input references and report references only. It does not accept:

- production credentials;
- PLC/DCS credentials;
- purchase-order execution commands;
- autonomous supplier-selection commands;
- unattended approval tokens.

Extraction remains an extraction operation. Deterministic comparison remains the compliance operation. Human approval is a separate state transition.

## Failure behavior

Invalid transitions fail closed with ValueError. In particular:

- extraction cannot start without an uploaded input reference;
- review cannot start without an extraction reference;
- report generation cannot occur without explicit human approval;
- a report state is terminal.

This state machine is deliberately independent of supplier ranking or procurement selection.