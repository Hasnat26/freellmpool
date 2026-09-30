"""Deterministic portfolio demo for an industrial engineering workflow.

This demo intentionally uses sample data and performs no external API calls.
It validates the product shape before provider/model integration is added.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Status = Literal[
    "VERIFIED",
    "PARTIALLY VERIFIED",
    "UNVERIFIED",
    "INFERENCE",
    "ASSUMPTION",
    "CONTRADICTED",
]


@dataclass(frozen=True)
class Requirement:
    tag: str
    parameter: str
    required: str


@dataclass(frozen=True)
class VendorValue:
    vendor: str
    parameter: str
    value: str
    evidence: str
    status: Status


REQUIREMENTS = [
    Requirement("R-01", "Rated voltage", "415 V"),
    Requirement("R-02", "Motor power", "75 kW"),
    Requirement("R-03", "Efficiency class", "IE3"),
    Requirement("R-04", "Ingress protection", "IP55"),
]

VENDOR_DATA = [
    VendorValue("Vendor A", "Rated voltage", "415 V", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor A", "Motor power", "75 kW", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor A", "Efficiency class", "IE3", "Quotation p.2", "VERIFIED"),
    VendorValue("Vendor A", "Ingress protection", "IP55", "Quotation p.2", "VERIFIED"),
    VendorValue("Vendor B", "Rated voltage", "415 V", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor B", "Motor power", "75 kW", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor B", "Efficiency class", "IE2", "Quotation p.2", "VERIFIED"),
    VendorValue("Vendor B", "Ingress protection", "IP55", "Quotation p.2", "VERIFIED"),
]


def build_matrix() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for req in REQUIREMENTS:
        for vendor in ("Vendor A", "Vendor B"):
            item = next(
                (
                    x
                    for x in VENDOR_DATA
                    if x.vendor == vendor and x.parameter == req.parameter
                ),
                None,
            )
            if item is None:
                rows.append(
                    {
                        "requirement": req.tag,
                        "vendor": vendor,
                        "parameter": req.parameter,
                        "required": req.required,
                        "offered": "MISSING",
                        "status": "UNVERIFIED",
                        "evidence": "No matching quotation field",
                    }
                )
                continue

            status = "COMPLIANT" if item.value == req.required else "DEVIATION"
            rows.append(
                {
                    "requirement": req.tag,
                    "vendor": vendor,
                    "parameter": req.parameter,
                    "required": req.required,
                    "offered": item.value,
                    "status": status,
                    "evidence": item.evidence,
                }
            )
    return rows


def main() -> None:
    matrix = build_matrix()
    print("Industrial Engineering AI Gateway — deterministic demo")
    print("=" * 58)
    print("Workflow: RFQ → requirement extraction → compliance review")
    print()

    for row in matrix:
        print(
            f"{row['requirement']} | {row['vendor']:8} | "
            f"{row['parameter']:18} | required={row['required']:5} | "
            f"offered={row['offered']:5} | {row['status']:10} | {row['evidence']}"
        )

    deviations = [x for x in matrix if x["status"] == "DEVIATION"]
    print()
    print(f"Verified deviations requiring engineer review: {len(deviations)}")
    for item in deviations:
        print(
            f"- {item['vendor']}: {item['parameter']} = "
            f"{item['offered']} (required {item['required']})"
        )


if __name__ == "__main__":
    main()
