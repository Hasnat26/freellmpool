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
    claim_status: ClaimStatus = "UNVERIFIED"


@dataclass(frozen=True)
class CommercialValue:
    vendor: str
    price: str
    currency: str
    lead_time: str
    warranty: str
    payment_terms: str
    evidence: str
    claim_status: ClaimStatus = "UNVERIFIED"


DEFAULT_REQUIREMENTS: tuple[Requirement, ...] = (
    Requirement("R-01", "Rated voltage", "415 V"),
    Requirement("R-02", "Motor power", "75 kW"),
    Requirement("R-03", "Efficiency class", "IE3"),
    Requirement("R-04", "Ingress protection", "IP55"),
)

DEFAULT_VENDOR_DATA: tuple[VendorValue, ...] = (
    VendorValue("Vendor A", "Rated voltage", "415 V", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor A", "Motor power", "75 kW", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor A", "Efficiency class", "IE3", "Quotation p.2", "VERIFIED"),
    VendorValue("Vendor A", "Ingress protection", "IP55", "Quotation p.2", "VERIFIED"),
    VendorValue("Vendor B", "Rated voltage", "415 V", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor B", "Motor power", "75 kW", "Quotation p.1", "VERIFIED"),
    VendorValue("Vendor B", "Efficiency class", "IE2", "Quotation p.2", "VERIFIED"),
    VendorValue("Vendor B", "Ingress protection", "IP55", "Quotation p.2", "VERIFIED"),
)


def _normalise_requirements(
    requirements: Sequence[Requirement] | None,
) -> tuple[Requirement, ...]:
    return tuple(requirements or DEFAULT_REQUIREMENTS)


def _normalise_vendor_data(
    vendor_data: Sequence[VendorValue] | None,
) -> tuple[VendorValue, ...]:
    return tuple(vendor_data or DEFAULT_VENDOR_DATA)


def load_rfq_input(path: str | Path) -> tuple[list[Requirement], list[VendorValue], list[CommercialValue]]:
    """Load and strictly validate a structured RFQ JSON input file."""
    input_path = Path(path)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read RFQ input '{input_path}': {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid RFQ JSON in '{input_path}': {exc.msg}") from exc

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
            raise ValueError(f"requirements[{index}] must be an object")
        missing = next((field for field in ("tag", "parameter", "required") if field not in item), None)
        if missing:
            raise ValueError(f"requirements[{index}] missing field: {missing}")
        tag = str(item["tag"]).strip()
        parameter = str(item["parameter"]).strip()
        required = str(item["required"]).strip()
        if not tag or not parameter or not required:
            raise ValueError(f"requirements[{index}] fields must not be empty")
        requirements.append(Requirement(tag, parameter, required))

    allowed_statuses = {"VERIFIED", "PARTIALLY VERIFIED", "UNVERIFIED", "INFERENCE", "ASSUMPTION", "CONTRADICTED"}
    vendor_data: list[VendorValue] = []
    for index, item in enumerate(raw_vendor_data):
        if not isinstance(item, dict):
            raise ValueError(f"vendor_data[{index}] must be an object")
        missing = next((field for field in ("vendor", "parameter", "value", "evidence") if field not in item), None)
        if missing:
            raise ValueError(f"vendor_data[{index}] missing field: {missing}")
        vendor = str(item["vendor"]).strip()
        parameter = str(item["parameter"]).strip()
        value = str(item["value"]).strip()
        evidence = str(item["evidence"]).strip()
        claim_status = str(item.get("claim_status", "UNVERIFIED")).strip().upper()
        if not vendor or not parameter or not value or not evidence:
            raise ValueError(f"vendor_data[{index}] required fields must not be empty")
        if claim_status not in allowed_statuses:
            raise ValueError(f"vendor_data[{index}] invalid claim_status: {claim_status!r}")
        vendor_data.append(VendorValue(vendor, parameter, value, evidence, cast(ClaimStatus, claim_status)))

    raw_commercial = payload.get("commercial_data", [])
    if not isinstance(raw_commercial, list):
        raise ValueError("RFQ input 'commercial_data' must be an array when provided")
    commercial_data: list[CommercialValue] = []
    commercial_fields = ("vendor", "price", "currency", "lead_time", "warranty", "payment_terms", "evidence")
    for index, item in enumerate(raw_commercial):
        if not isinstance(item, dict):
            raise ValueError(f"commercial_data[{index}] must be an object")
        missing = next((field for field in commercial_fields if field not in item), None)
        if missing:
            raise ValueError(f"commercial_data[{index}] missing field: {missing}")
        values = {field: str(item[field]).strip() for field in commercial_fields}
        claim_status = str(item.get("claim_status", "UNVERIFIED")).strip().upper()
        if any(not values[field] for field in commercial_fields):
            raise ValueError(f"commercial_data[{index}] required fields must not be empty")
        if claim_status not in allowed_statuses:
            raise ValueError(f"commercial_data[{index}] invalid claim_status: {claim_status!r}")
        commercial_data.append(CommercialValue(**values, claim_status=cast(ClaimStatus, claim_status)))

    return requirements, vendor_data, commercial_data


@dataclass(frozen=True)
class DocumentPage:
    source: str
    page: int
    text: str


def extract_document_pages(path: str | Path) -> list[DocumentPage]:
    """Extract text while preserving source and page provenance."""
    document = Path(path)
    if not document.is_file():
        raise ValueError(f"document not found: {document}")
    suffix = document.suffix.casefold()
    if suffix in {".txt", ".md"}:
        text = document.read_text(encoding="utf-8")
        return [DocumentPage(str(document), 1, text)]
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF ingestion requires the pypdf dependency") from exc
        try:
            reader = PdfReader(str(document))
        except Exception as exc:
            raise ValueError(f"cannot read PDF: {document}") from exc
        pages: list[DocumentPage] = []
        for number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(DocumentPage(str(document), number, text))
        if not pages:
            raise ValueError(f"PDF contains no pages: {document}")
        return pages
    raise ValueError("unsupported document type; expected .txt, .md, or .pdf")


def document_text(pages: Sequence[DocumentPage]) -> str:
    """Build LLM-ready text with explicit source/page markers."""
    return "\n\n".join(
        f"[SOURCE: {page.source} | PAGE: {page.page}]\n{page.text.strip()}"
        for page in pages
        if page.text.strip()
    )


_PARAMETER_ALIASES = {
    "rated voltage": "rated voltage",
    "voltage": "rated voltage",
    "nominal voltage": "rated voltage",
    "motor voltage": "rated voltage",
    "motor power": "motor power",
    "rated power": "motor power",
    "power": "motor power",
    "efficiency class": "efficiency class",
    "efficiency": "efficiency class",
    "energy efficiency": "efficiency class",
    "ingress protection": "ingress protection",
    "ip rating": "ingress protection",
    "protection": "ingress protection",
}

def _normalise_parameter(parameter: str) -> str:
    key = " ".join(parameter.casefold().replace("_", " ").replace("-", " ").split())
    return _PARAMETER_ALIASES.get(key, key)

def _normalise_value(value: str) -> str:
    return " ".join(value.casefold().replace(",", "").split())

def _numeric_unit(value: str) -> tuple[float, str] | None:
    import re
    match = re.fullmatch(r"([-+]?\d+(?:\.\d+)?)\s*([a-zA-Z%]+)", value.strip())
    if not match:
        return None
    number = float(match.group(1))
    unit = match.group(2).casefold()
    conversions = {
        "v": ("v", 1.0), "kv": ("v", 1000.0),
        "w": ("w", 1.0), "kw": ("w", 1000.0), "mw": ("w", 1_000_000.0),
    }
    if unit not in conversions:
        return None
    canonical, multiplier = conversions[unit]
    return number * multiplier, canonical

def _values_match(required: str, offered: str) -> bool:
    left = _numeric_unit(required)
    right = _numeric_unit(offered)
    if left is not None and right is not None and left[1] == right[1]:
        return left[0] == right[0]
    return _normalise_value(required) == _normalise_value(offered)


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
                    if value.vendor == vendor
                    and _normalise_parameter(value.parameter) == _normalise_parameter(req.parameter)
                ),
                None,
            )
            if item is None:
                rows.append(
                    {
                        "requirement": req.tag,
                        "vendor": vendor,
                        "parameter": req.parameter,
                        "offered_parameter": "MISSING",
                        "required": req.required,
                        "offered": "MISSING",
                        "status": "UNVERIFIED",
                        "evidence": "No matching quotation field",
                        "claim_status": "UNVERIFIED",
                    }
                )
                continue

            status = "COMPLIANT" if _values_match(item.value, req.required) else "DEVIATION"
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



def build_evidence_register(requirements: Sequence[Requirement], vendor_data: Sequence[VendorValue], commercial_data: Sequence[CommercialValue] = ()) -> list[dict[str, str]]:
    """Return a traceable evidence register for every supplied claim."""
    rows: list[dict[str, str]] = []
    for item in vendor_data:
        rows.append({"source_type": "technical_quotation", "vendor": item.vendor, "field": item.parameter, "value": item.value, "evidence": item.evidence, "claim_status": item.claim_status, "review_required": "YES" if item.claim_status != "VERIFIED" else "NO"})
    for item in commercial_data:
        rows.append({"source_type": "commercial_quotation", "vendor": item.vendor, "field": "price / lead_time / warranty / payment_terms", "value": f"{item.price} {item.currency}; {item.lead_time}; {item.warranty}; {item.payment_terms}", "evidence": item.evidence, "claim_status": item.claim_status, "review_required": "YES" if item.claim_status != "VERIFIED" else "NO"})
    return rows

def build_report(
    requirements: Sequence[Requirement] | None = None,
    vendor_data: Sequence[VendorValue] | None = None,
    commercial_data: Sequence[CommercialValue] | None = None,
) -> dict[str, object]:
    """Return a machine-readable RFQ review report."""

    reqs = _normalise_requirements(requirements)
    values = _normalise_vendor_data(vendor_data)
    commercial = tuple(commercial_data or ())
    matrix = build_matrix(reqs, values)
    evidence_register = build_evidence_register(reqs, values, commercial)
    review_claims = [row for row in evidence_register if row["review_required"] == "YES"]
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
            "commercial_records": len(commercial),
            "evidence_records": len(evidence_register),
            "claims_requiring_review": len(review_claims),
        },
        "matrix": matrix,
        "commercial_comparison": [asdict(item) for item in commercial],
        "evidence_register": evidence_register,
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
    "CommercialValue",
    "DocumentPage",
    "extract_document_pages",
    "document_text",
    "build_matrix",
    "build_evidence_register",
    "build_report",
    "load_rfq_input",
    "extract_rfq_with_llm",
    "extract_rfq_documents_with_llm",
    "render_report",
    "write_report",
]


def extract_rfq_documents_with_llm(
    pool: object,
    rfq_document: str | Path,
    quotation_documents: Sequence[dict[str, str | Path]],
) -> tuple[list[Requirement], list[VendorValue], list[CommercialValue]]:
    """Extract an RFQ and vendor quotations directly from local documents."""
    rfq_pages = extract_document_pages(rfq_document)
    rfq_text = document_text(rfq_pages)
    quotations: list[dict[str, str]] = []
    for index, item in enumerate(quotation_documents):
        vendor = str(item.get("vendor", "")).strip()
        path = item.get("path")
        if not vendor or path is None:
            raise ValueError(f"quotation_documents[{index}] requires vendor and path")
        pages = extract_document_pages(path)
        text = document_text(pages)
        if not text.strip():
            raise ValueError(f"quotation document is empty: {path}")
        quotations.append({
            "vendor": vendor,
            "text": text,
            "evidence_prefix": f"{Path(path).name}",
        })
    return extract_rfq_with_llm(pool, rfq_text, quotations)

def extract_rfq_with_llm(pool: object, rfq_text: str, quotations: Sequence[dict[str, str]]) -> tuple[list[Requirement], list[VendorValue], list[CommercialValue]]:
    """Extract structured RFQ data with the gateway, then validate it locally.

    The model is an extractor only. Compliance status is calculated later by
    build_matrix from the extracted values and their evidence.
    """
    if not rfq_text.strip():
        raise ValueError("RFQ text must not be empty")
    if not quotations:
        raise ValueError("at least one quotation is required")

    quote_payload = []
    for index, quote in enumerate(quotations):
        vendor = str(quote.get("vendor", "")).strip()
        text = str(quote.get("text", "")).strip()
        evidence_prefix = str(quote.get("evidence_prefix", f"{vendor} quotation")).strip()
        if not vendor or not text:
            raise ValueError(f"quotations[{index}] requires vendor and text")
        quote_payload.append({"vendor": vendor, "text": text, "evidence_prefix": evidence_prefix})

    schema = {
        "requirements": [{"tag": "R-01", "parameter": "Rated voltage", "required": "415 V"}],
        "vendor_data": [{"vendor": "Vendor A", "parameter": "Rated voltage",
                         "value": "415 V", "evidence": "Vendor A quotation, section 2",
                         "claim_status": "VERIFIED"}],
        "commercial_data": [{"vendor": "Vendor A", "price": "10000", "currency": "USD", "lead_time": "8 weeks", "warranty": "12 months", "payment_terms": "30% advance", "evidence": "Vendor A quotation, commercial section", "claim_status": "VERIFIED"}],
    }
    system = (
        "You are an engineering document extraction component. Extract only facts explicitly stated "
        "in the supplied RFQ and quotations. Never infer missing values. Every vendor value must include "
        "a concise source/evidence reference. Return exactly one JSON object matching this schema: "
        + json.dumps(schema, ensure_ascii=False)
        + ". Use claim_status VERIFIED only when the supplied quotation explicitly supports the value; "
        "otherwise use UNVERIFIED. Do not calculate compliance."
    )
    prompt = json.dumps({"rfq": rfq_text, "quotations": quote_payload}, ensure_ascii=False)
    try:
        reply = pool.ask(prompt, system=system, max_tokens=3000, temperature=0.0, timeout=90.0, task="grounded-reading")
    except Exception as exc:
        raise ValueError(f"LLM RFQ extraction failed: {exc}") from exc

    raw = reply.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        if raw.endswith("```"):
            raw = raw[:-3].rstrip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM returned invalid extraction JSON: {exc.msg}") from exc

    import tempfile
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=False)
            temp_path = Path(handle.name)
        return load_rfq_input(temp_path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

