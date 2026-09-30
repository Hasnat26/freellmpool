# Industrial Engineering AI Gateway — Product Specification

## Product goal

Turn the existing freellmpool gateway into a practical, evidence-aware AI gateway for engineering, EPC and industrial automation workflows.

## v1 user journey

1. Start the local gateway.
2. Select an engineering task.
3. Route the task to an available model/provider.
4. Collect the response and execution metadata.
5. Attach evidence/status labels to important claims.
6. Produce a structured engineering report.

## v1 workflows

### RFQ / quotation comparison

Input:
- RFQ/specification
- 2–5 vendor quotations

Output:
- requirement extraction
- vendor-by-vendor compliance matrix
- technical deviations
- commercial comparison fields
- missing-information list
- evidence references
- review status

### Engineering document Q&A

Input:
- manuals
- specifications
- FAT/SAT documents
- project correspondence

Output:
- answer
- source reference
- confidence/status
- unresolved ambiguity

### Project risk review

Input:
- risk register
- schedule extract
- procurement status
- issue log

Output:
- risk summary
- schedule/commercial impact fields
- mitigation actions
- evidence/status

## Evidence policy

The application must distinguish:
- VERIFIED
- PARTIALLY VERIFIED
- UNVERIFIED
- INFERENCE
- ASSUMPTION
- CONTRADICTED

No claim may be represented as verified without an explicit supporting source.

## v1 non-goals

- no autonomous plant/control-system operation
- no modification of PLC/DCS logic
- no unattended procurement decisions
- no production credentials stored in the repository
- no claim of engineering certification or professional approval

## Acceptance criteria

The v1 release is considered complete when a clean user can:

1. install the package;
2. start the local gateway;
3. run an example engineering workflow with sample data;
4. receive a structured result;
5. see evidence/status fields;
6. run the automated test suite successfully;
7. reproduce the demo from README instructions.

## Portfolio positioning

This project demonstrates practical application of AI orchestration to engineering and EPC decision-support workflows rather than generic chatbot functionality.
