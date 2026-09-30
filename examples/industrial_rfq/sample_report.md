# Industrial RFQ Engineering Review

## Executive summary

- Requirements checked: **4**
- Vendors checked: **2**
- Deviations: **1**
- Unverified fields: **0**
- Claims requiring review: **0**

This report is an evidence-aware engineering review. It does not select a supplier or make an autonomous procurement decision.

## Technical compliance matrix

| Requirement | Vendor | Parameter | Required | Offered | Status | Evidence |
|---|---|---|---|---|---|---|
| R-01 | Vendor A | Rated voltage | 415 V | 0.415 kV | COMPLIANT | Quotation p.1 |
| R-02 | Vendor A | Motor power | 75 kW | 75 kW | COMPLIANT | Quotation p.1 |
| R-03 | Vendor A | Efficiency class | IE3 | IE3 | COMPLIANT | Quotation p.2 |
| R-04 | Vendor A | Ingress protection | IP55 | IP55 | COMPLIANT | Quotation p.2 |
| R-01 | Vendor B | Rated voltage | 415 V | 415 V | COMPLIANT | Quotation p.1 |
| R-02 | Vendor B | Motor power | 75 kW | 75 kW | COMPLIANT | Quotation p.1 |
| R-03 | Vendor B | Efficiency class | IE3 | IE2 | DEVIATION | Quotation p.2 |
| R-04 | Vendor B | Ingress protection | IP55 | IP55 | COMPLIANT | Quotation p.2 |

## Commercial information

| Vendor | Price | Currency | Lead time | Warranty | Payment terms | Claim status | Evidence |
|---|---:|---|---|---|---|---|---|
| Vendor A | 10000 | USD | 8 weeks | 24 months | 30% advance, 70% before shipment | VERIFIED | Quotation p.3 |
| Vendor B | 9200 | USD | 12 weeks | 12 months | 50% advance, 50% before shipment | VERIFIED | Quotation p.3 |

## Engineer review actions

- **Vendor B / Efficiency class**: offered `IE2`, required `IE3`. Verify against source evidence: Quotation p.2.

## Controls

- LLM output is extraction assistance only.
- Compliance status is calculated by the deterministic comparison engine.
- Missing or unsupported claims remain reviewable.
- Commercial data is presented for review; no automatic supplier winner is selected.
