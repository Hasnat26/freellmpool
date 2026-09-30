"""Industrial engineering workflows for freellmpool.

The first vertical slice is a deterministic RFQ compliance reviewer.  It is
deliberately dependency-free and can be used as a stable foundation for a
future LLM-assisted extraction layer.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Sequence, cast

ClaimStatus = Literal[
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
    claim_status: ClaimStatus = "VERIFIED"


DEFAULT_REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement("R-01", "Rated voltage", "415 V"),
    Requirement("R-02", "Motor power", "75 kW"),
    Requirement("R-03", "Efficiency class", "IE3"),
    Requirement("R-04", "Ingress protection", "IP55"),
)

DEFAULT_VENDOR_DATA: tuple[VendorValue, ...] = (
    VendorValue("Vendor A", "Rated voltage", "415 V", "Quotation p.1"),
    VendorValue("Vendor A", "Motor power", "75 kW", "Quotation p.1"),
    VendorValue("Vendor A", "Efficiency class", "IE3", "Quotation p.2"),
    VendorValue("Vendor A", "Ingress protection", "IP55", "Quotation p.2"),
    VendorValue("Vendor B", "Rated voltage", "415 V", "Quotation p.1"),
    VendorValue("Vendor B", "Motor power", "75 kW", "Quotation p.1"),
    VendorValue("Vendor B", "Efficiency class", "IE2", "Quotation p.2"),
    VendorValue("Vendor B", "Ingress protection", "IP55", "Quotation p.2"),
)


def _normalise_requirements(
    requirements: Sequence[Requirement] | None,
) -> tuple[Requirement, ...]:
    return tuple(requirements or DEFAULT_REQUIREMENTS)


def _normalise_vendor_data(
    vendor_data: Sequence[VendorValue] | None,
) -> tuple[VendorValue, ...]:
    return tuple(vendor_data or DEFAULT_VENDOR_DATA)


def load_rfq_input(path: str | Path) -> tuple[list[Requirement], list[VendorValue]]:
    """Load and strictly validate a structured RFQ JSON input file."""
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read RFQ input '${input_path}': ${exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid RFQ JSON in '${input_path}': ${exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValueError("RFQ input must be a JSON object")

    raw_requirements = payload.get("requirements")
    raw_vendor_data = payload.get("vendor_data")
    if not isinstance(raw_requirements, list) or not raw_requirements:
        raise ValueError("RFQ input requires a non-empty 'requirements' array")
    if not isinstance(raw_vendor_data, list) or not raw_vendor_data:
        raise ValueError("RFQ input requires a non-empty 'vendor_data' array")

    requirements: list[Requirement] = []
    for index, item in enumerate(raw_requirements):
        if not isinstance(item, dict):
            raise ValueError(f"requirements[${index}] must be an object")
        missing = next((field for field in ("tag", "parameter", "required") if field not in item), None)
        if missing:
            raise ValueError(f"requirements[${index}] missing field: ${missing}")
        tag = str(item["tag"]).strip()
        parameter = str(item["parameter"]).strip()
        required = str(item["required"]).strip()
        if not tag or not parameter or not required:
            raise ValueError(f"requirements[${index}] fields must not be empty")
        requirements.append(Requirement(tag, parameter, required))

    allowed_statuses = {"VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "INFERENCE", "ASSUMPTION", "CONTRADICTED"}
    vendor_data: list[VendorValue] = []
    for index, item in enumerate(raw_vendor_data):
        if not isinstance(item, dict):
            raise ValueError(f"vendor_data[${index}] must be an object")
        missing = next((field for field in ("vendor", "parameter", "value", "evidence") if field not in item), None)
        if missing:
            raise ValueError(f"vendor_data[${index}] missing field: ${missing}")
        vendor = str(item["vendor"]).strip()
        parameter = str(item["parameter"]).strip()
        value = str(item["value"]).strip()
        evidence = str(item["evidence"]).strip()
        claim_status = str(item.get("claim_status", "VERIFIED")).strip().upper()
        if not vendor or not parameter or not value or not evidence:
            raise ValueError(f"vendor_data[${index}] required fields must not be empty")
        if claim_status not in allowed_statuses:
            raise ValueError(f"vendor_data[${index}] invalid claim_status: ${claim_status!r}")
        vendor_data.append(VendorValue(vendor, parameter, value, evidence, cast(ClaimStatus, claim_status)))

    return requirements, vendor_data


def build_matrix(
    requirements: Sequence[Requirement] | None = None,
    vendor_data: Sequence[VendorValue] | None = None,
) -> list[dict[str, str]]:
    """Build a requirement-by-vendor compliance matrix.

    A missing quotation field is never treated as compliant.  It is explicitly
    labelled UNVERIFIED so downstream review cannot mistake absence of evidence
    for compliance.
    """

    reqs = _normalise_requirements(requirements)
    values = _normalise_vendor_data(vendor_data)
    vendors = tuple(dict.fromkeys(item.vendor for item in values))
    rows: list[dict[str, str]] = []

    for req in reqs:
        for vendor in vendors:
            item = next(
                (
                    value
                    for value in values
                    if value.vendor == vendor and value.parameter == req.parameter
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
                        "claim_status": "UNVERIFIED",
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
                    "claim_status": item.claim_status,
                }
            )

    return rows


def build_report(
    requirements: Sequence[Requirement] | None = None,
    vendor_data: Sequence[VendorValue] | None = None,
) -> dict[str, object]:
    """Return a machine-readable RFQ review report."""

    reqs = _normalise_requirements(requirements)
    values = _normalise_vendor_data(vendor_data)
    matrix = build_matrix(reqs, values)
    deviations = [row for row in matrix if row["status"] == "DEVIATION"]
    unverified = [row for row in matrix if row["status"] == "UNVERIFIED"]
    vendors = tuple(dict.fromkeys(item.vendor for item in values))

    return {
        "product": "freellmpool industrial engineering",
        "workflow": "rfq-compliance-review",
        "evidence_policy": (
            "Only explicit supporting quotation evidence may be marked VERIFIED; "
            "missing or unsupported claims remain UNVERIFIED."
        ),
        "summary": {
            "requirements_checked": len(reqs),
            "vendors_checked": len(vendors),
            "matrix_rows": len(matrix),
            "deviations": len(deviations),
            "unverified_fields": len(unverified),
        },
        "matrix": matrix,
        "review_actions": [
            {
                "vendor": row["vendor"],
                "parameter": row["parameter"],
                "offered": row["offered"],
                "required": row["required"],
                "action": "Engineer review required",
                "evidence": row["evidence"],
            }
            for row in deviations
        ],
    }


def render_report(report: dict[str, object]) -> str:
    """Render a concise human-readable RFQ review."""

    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        "Industrial Engineering AI Gateway — RFQ compliance review",
        "=" * 62,
        "Workflow: RFQ → requirement extraction → compliance review",
        "",
    ]
    matrix = report["matrix"]
    assert isinstance(matrix, list)
    for row in matrix:
        lines.append(
            f"{row['requirement']} | {row['vendor']:8} | "
            f"{row['parameter']:18} | required={row['required']:5} | "
            f"offered={row['offered']:7} | {row['status']:10} | "
            f"{row['evidence']}"
        )
    lines.extend(
        [
            "",
            f"Requirements checked: {summary['requirements_checked']}",
            f"Vendors checked: {summary['vendors_checked']}",
            f"Deviations requiring engineer review: {summary['deviations']}",
            f"Unverified fields: {summary['unverified_fields']}",
        ]
    )
    return "\n".join(lines)


def write_report(report: dict[str, object], output: str | Path) -> None:
    """Write a JSON report to disk, creating the parent directory if needed."""

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


__all__ = [
    "ClaimStatus",
    "DEFAULT_REQUIREMENTS",
    "DEFAULT_VENDOR_DATA",
    "Requirement",
    "VendorValue",
    "build_matrix",
    "build_report",
    "load_rfq_input",
    "render_report",
    "write_report",
]
