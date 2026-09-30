from pathlib import Path

from freellmpool.industrial import (
    Requirement,
    VendorValue,
    build_matrix,
    build_report,
)


def test_build_matrix_detects_vendor_deviation() -> None:
    matrix = build_matrix()
    deviations = [row for row in matrix if row["status"] == "DEVIATION"]

    assert len(matrix) == 8
    assert len(deviations) == 1
    assert deviations[0]["vendor"] == "Vendor B"
    assert deviations[0]["parameter"] == "Efficiency class"
    assert deviations[0]["offered"] == "IE2"
    assert deviations[0]["required"] == "IE3"
    assert deviations[0]["evidence"] == "Quotation p.2"


def test_missing_fields_are_unverified() -> None:
    requirements = [Requirement("R-01", "Rated voltage", "415 V")]
    vendor_data = [
        VendorValue("Vendor A", "Motor power", "75 kW", "Quotation p.1"),
    ]

    matrix = build_matrix(requirements, vendor_data)
    assert matrix[0]["status"] == "UNVERIFIED"
    assert matrix[0]["claim_status"] == "UNVERIFIED"
    assert matrix[0]["evidence"] == "No matching quotation field"


def test_report_contains_review_actions_and_summary() -> None:
    report = build_report()
    assert report["workflow"] == "rfq-compliance-review"
    assert report["product"] == "industrial-rfq-intelligence"
    summary = report["summary"]
    assert summary["requirements_checked"] == 4
    assert summary["vendors_checked"] == 2
    assert summary["deviations"] == 1
    assert len(report["review_actions"]) == 1


def test_load_rfq_input_from_json(tmp_path) -> None:
    from freellmpool.industrial import load_rfq_input

    path = tmp_path / "rfq.json"
    path.write_text(
        """{
          "requirements": [
            {"tag": "R-01", "parameter": "Rated voltage", "required": "415 V"}
          ],
          "vendor_data": [
            {"vendor": "Vendor X", "parameter": "Rated voltage",
             "value": "400 V", "evidence": "Quotation p.3",
             "claim_status": "VERIFIED"}
          ]
        }""",
        encoding="utf-8",
    )

    requirements, vendor_data, commercial = load_rfq_input(path)
    assert requirements[0].parameter == "Rated voltage"
    assert vendor_data[0].vendor == "Vendor X"
    assert vendor_data[0].claim_status == "VERIFIED"


def test_load_rfq_input_rejects_missing_required_field(tmp_path) -> None:
    from freellmpool.industrial import load_rfq_input

    path = tmp_path / "invalid.json"
    path.write_text(
        '{"requirements": [{"tag": "R-01"}], "vendor_data": [{"vendor": "Vendor X"}]}',
        encoding="utf-8",
    )

    try:
        load_rfq_input(path)
    except ValueError as exc:
        assert "missing field: parameter" in str(exc)
    else:
        raise AssertionError("invalid RFQ input was accepted")


def test_llm_extraction_reuses_strict_validation() -> None:
    from freellmpool.industrial import extract_rfq_with_llm

    class FakeReply:
        text = '{"requirements":[{"tag":"R-01","parameter":"Rated voltage","required":"415 V"}],"vendor_data":[{"vendor":"Vendor X","parameter":"Rated voltage","value":"400 V","evidence":"Vendor X quotation p.1","claim_status":"VERIFIED"}]}'

    class FakePool:
        def ask(self, *args, **kwargs):
            return FakeReply()

    requirements, vendor_data, commercial = extract_rfq_with_llm(
        FakePool(),
        "Supply 415 V motor.",
        [{"vendor": "Vendor X", "text": "400 V motor.", "evidence_prefix": "Vendor X quotation"}],
    )
    assert requirements[0].required == "415 V"
    assert vendor_data[0].value == "400 V"
    assert vendor_data[0].evidence == "Vendor X quotation p.1"
    assert commercial == []


def test_conflicting_vendor_claims_are_unverified() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    matrix = build_matrix(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [
            VendorValue("Vendor X", "Rated voltage", "415 V", "quote p.1", "VERIFIED"),
            VendorValue("Vendor X", "Nominal voltage", "400 V", "quote p.4", "VERIFIED"),
        ],
    )
    assert matrix[0]["status"] == "UNVERIFIED"
    assert matrix[0]["claim_status"] == "CONTRADICTED"
    assert matrix[0]["offered"] == "CONFLICTING"
    assert "quote p.1: 415 V" in matrix[0]["evidence"]
    assert "quote p.4: 400 V" in matrix[0]["evidence"]


def test_missing_evidence_forces_unverified(tmp_path) -> None:
    import json
    from freellmpool.industrial import load_rfq_input

    path = tmp_path / "rfq.json"
    path.write_text(
        json.dumps({
            "requirements": [{"tag": "R-01", "parameter": "Rated voltage", "required": "415 V"}],
            "vendor_data": [{
                "vendor": "Vendor X",
                "parameter": "Rated voltage",
                "value": "415 V",
                "claim_status": "VERIFIED",
            }],
            "commercial_data": [{
                "vendor": "Vendor X",
                "price": "10000",
                "currency": "USD",
                "lead_time": "8 weeks",
                "warranty": "12 months",
                "payment_terms": "30% advance",
                "claim_status": "VERIFIED",
            }],
        }),
        encoding="utf-8",
    )
    _, vendor_data, commercial = load_rfq_input(path)
    assert vendor_data[0].evidence == ""
    assert vendor_data[0].claim_status == "UNVERIFIED"
    assert commercial[0].evidence == ""
    assert commercial[0].claim_status == "UNVERIFIED"


def test_claim_status_defaults_to_unverified(tmp_path) -> None:
    import json
    from freellmpool.industrial import load_rfq_input

    path = tmp_path / "rfq.json"
    path.write_text(
        json.dumps({
            "requirements": [{"tag": "R-01", "parameter": "Rated voltage", "required": "415 V"}],
            "vendor_data": [{
                "vendor": "Vendor X",
                "parameter": "Rated voltage",
                "value": "415 V",
                "evidence": "quote p.1",
            }],
        }),
        encoding="utf-8",
    )
    _, vendor_data, commercial = load_rfq_input(path)
    assert vendor_data[0].claim_status == "UNVERIFIED"
    assert commercial == []


def test_load_rfq_input_includes_commercial_data(tmp_path) -> None:
    import json
    from freellmpool.industrial import load_rfq_input

    payload = {
        "requirements": [{"tag": "R-01", "parameter": "Rated voltage", "required": "415 V"}],
        "vendor_data": [{"vendor": "Vendor A", "parameter": "Rated voltage", "value": "415 V", "evidence": "p.1"}],
        "commercial_data": [{
            "vendor": "Vendor A", "price": "10000", "currency": "USD",
            "lead_time": "8 weeks", "warranty": "24 months",
            "payment_terms": "30% advance", "evidence": "p.3"
        }],
    }
    path = tmp_path / "rfq.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    requirements, vendor_data, commercial = load_rfq_input(path)
    assert requirements[0].required == "415 V"
    assert vendor_data[0].value == "415 V"
    assert commercial[0].price == "10000"
    assert commercial[0].warranty == "24 months"


def test_parameter_alias_and_unit_normalization() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    requirements = [
        Requirement("R-01", "Rated voltage", "0.415 kV"),
        Requirement("R-02", "Motor power", "75 kW"),
    ]
    vendor_data = [
        VendorValue("Vendor X", "Nominal voltage", "415 V", "quotation p.1"),
        VendorValue("Vendor X", "Rated power", "75000 W", "quotation p.1"),
    ]
    matrix = build_matrix(requirements, vendor_data)
    assert [row["status"] for row in matrix] == ["COMPLIANT", "COMPLIANT"]
    assert matrix[0]["offered_parameter"] == "Nominal voltage"


def test_broader_engineering_unit_normalization() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    cases = [
        ("Current", "1 kA", "1000 A"),
        ("Frequency", "50 Hz", "0.05 kHz"),
        ("Speed", "1500 rpm", "1500 rpm"),
        ("Torque", "1 kNm", "1000 Nm"),
        ("Temperature", "40 °C", "40 C"),
        ("Pressure", "1 MPa", "10 bar"),
        ("Length", "1 m", "1000 mm"),
        ("Mass", "1 t", "1000 kg"),
    ]

    for parameter, required, offered in cases:
        matrix = build_matrix(
            [Requirement("R-01", parameter, required)],
            [VendorValue("Vendor X", parameter, offered, "quote p.1", "VERIFIED")],
        )
        assert matrix[0]["status"] == "COMPLIANT"


def test_broader_engineering_unit_mismatch_is_deviation() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    matrix = build_matrix(
        [Requirement("R-01", "Pressure", "1 MPa")],
        [VendorValue("Vendor X", "Pressure", "9 bar", "quote p.1", "VERIFIED")],
    )
    assert matrix[0]["status"] == "DEVIATION"


def test_engineering_operators_ranges_and_tolerance() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    cases = [
        (Requirement("R-01", "Motor power", ">= 75 kW"), "75 kW"),
        (Requirement("R-02", "Rated voltage", "<= 415 V"), "415 V"),
        (Requirement("R-03", "Rated voltage", "> 400 V"), "415 V"),
        (Requirement("R-04", "Motor power", "70 to 80 kW"), "75 kW"),
        (Requirement("R-05", "Rated voltage", "400-450 V"), "450 V"),
        (Requirement("R-06", "Rated voltage", "415 V ±5%"), "415 V"),
        (Requirement("R-07", "Rated voltage", "415 V +/-5%"), "435 V"),
    ]

    for requirement, offered in cases:
        matrix = build_matrix(
            [requirement],
            [VendorValue("Vendor X", requirement.parameter, offered, "quote p.1", "VERIFIED")],
        )
        assert matrix[0]["status"] == "COMPLIANT"


def test_engineering_operator_deviation_is_detected() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    matrix = build_matrix(
        [Requirement("R-01", "Motor power", ">= 75 kW")],
        [VendorValue("Vendor X", "Motor power", "72 kW", "quote p.1", "VERIFIED")],
    )
    assert matrix[0]["status"] == "DEVIATION"


def test_unit_mismatch_remains_deviation() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    matrix = build_matrix(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Voltage", "400 V", "quotation p.1")],
    )
    assert matrix[0]["status"] == "DEVIATION"


def test_report_contains_evidence_register_and_review_flags() -> None:
    from freellmpool.industrial import CommercialValue, VendorValue, build_report
    report = build_report(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Voltage", "415 V", "quote p.1", "PARTIALLY VERIFIED")],
        [CommercialValue("Vendor X", "10000", "USD", "8 weeks", "12 months", "30% advance", "quote p.3", "VERIFIED")],
    )
    assert report["summary"]["evidence_records"] == 2
    assert report["summary"]["claims_requiring_review"] == 1
    assert report["evidence_register"][0]["review_required"] == "YES"
    assert report["evidence_register"][1]["review_required"] == "NO"


def test_document_ingestion_preserves_source_and_page(tmp_path) -> None:
    from freellmpool.industrial import document_text, extract_document_pages

    path = tmp_path / "vendor_quote.txt"
    path.write_text("Rated voltage: 415 V\nMotor power: 75 kW", encoding="utf-8")
    pages = extract_document_pages(path)
    assert pages[0].source.endswith("vendor_quote.txt")
    assert pages[0].page == 1
    assert "Rated voltage: 415 V" in document_text(pages)


def test_document_ingestion_rejects_unsupported_type(tmp_path) -> None:
    from freellmpool.industrial import extract_document_pages

    path = tmp_path / "quote.docx"
    path.write_bytes(b"not supported")
    try:
        extract_document_pages(path)
    except ValueError as exc:
        assert "unsupported document type" in str(exc)
    else:
        raise AssertionError("unsupported document type was accepted")


def test_document_rfq_extraction_passes_provenance_to_llm() -> None:
    from freellmpool.industrial import extract_rfq_documents_with_llm

    class FakeReply:
        text = '{"requirements":[{"tag":"R-01","parameter":"Rated voltage","required":"415 V"}],"vendor_data":[{"vendor":"Vendor X","parameter":"Rated voltage","value":"415 V","evidence":"vendor_quote.txt | PAGE: 1","claim_status":"VERIFIED"}],"commercial_data":[]}'

    class FakePool:
        def __init__(self):
            self.prompt = None

        def ask(self, prompt, **kwargs):
            self.prompt = prompt
            return FakeReply()

    rfq = tmp_path = __import__("pathlib").Path("tests") / "_rfq_m7_temp.txt"
    quote = __import__("pathlib").Path("tests") / "_quote_m7_temp.txt"
    try:
        rfq.write_text("Required rated voltage: 415 V", encoding="utf-8")
        quote.write_text("Rated voltage: 415 V", encoding="utf-8")
        pool = FakePool()
        requirements, vendor_data, commercial = extract_rfq_documents_with_llm(
            pool,
            rfq,
            [{"vendor": "Vendor X", "path": quote}],
        )
        assert "[SOURCE:" in pool.prompt
        assert "PAGE: 1" in pool.prompt
        assert requirements[0].required == "415 V"
        assert vendor_data[0].evidence == "vendor_quote.txt | PAGE: 1"
        assert commercial == []
    finally:
        rfq.unlink(missing_ok=True)
        quote.unlink(missing_ok=True)
def test_sample_rfq_is_reproducible_and_report_matches_fixture() -> None:
    from freellmpool.industrial import build_report, load_rfq_input
    from freellmpool.industrial_report import render_engineering_report

    root = Path(__file__).resolve().parents[1]
    input_path = root / "examples" / "industrial_rfq" / "sample_input.json"
    report_path = root / "examples" / "industrial_rfq" / "sample_report.md"

    requirements, vendor_data, commercial = load_rfq_input(input_path)
    report = build_report(requirements, vendor_data, commercial)
    rendered = render_engineering_report(report) + "\n"

    assert report["summary"] == {
        "requirements_checked": 4,
        "vendors_checked": 2,
        "matrix_rows": 8,
        "deviations": 1,
        "unverified_fields": 0,
        "commercial_records": 2,
        "evidence_records": 10,
        "claims_requiring_review": 0,
    }
    assert rendered == report_path.read_text(encoding="utf-8")
    assert report["matrix"][6]["status"] == "DEVIATION"
    assert report["matrix"][6]["vendor"] == "Vendor B"
    assert report["matrix"][6]["parameter"] == "Efficiency class"

def test_invalid_claim_status_is_rejected(tmp_path) -> None:
    import json
    from freellmpool.industrial import load_rfq_input

    path = tmp_path / "invalid-status.json"
    path.write_text(
        json.dumps({
            "requirements": [{"tag": "R-01", "parameter": "Rated voltage", "required": "415 V"}],
            "vendor_data": [{
                "vendor": "Vendor X",
                "parameter": "Rated voltage",
                "value": "415 V",
                "evidence": "quote p.1",
                "claim_status": "GUESS",
            }],
        }),
        encoding="utf-8",
    )
    try:
        load_rfq_input(path)
    except ValueError as exc:
        assert "invalid claim_status" in str(exc)
    else:
        raise AssertionError("invalid claim_status was accepted")


def test_malformed_json_is_rejected(tmp_path) -> None:
    from freellmpool.industrial import load_rfq_input

    path = tmp_path / "broken.json"
    path.write_text("{not valid json", encoding="utf-8")
    try:
        load_rfq_input(path)
    except ValueError as exc:
        assert "invalid RFQ JSON" in str(exc)
    else:
        raise AssertionError("malformed JSON was accepted")


def test_empty_requirements_and_vendor_data_are_rejected(tmp_path) -> None:
    import json
    from freellmpool.industrial import load_rfq_input

    cases = [
        {"requirements": [], "vendor_data": [{"vendor": "Vendor X", "parameter": "Voltage", "value": "415 V"}]},
        {"requirements": [{"tag": "R-01", "parameter": "Voltage", "required": "415 V"}], "vendor_data": []},
    ]
    for index, payload in enumerate(cases):
        path = tmp_path / f"invalid-{index}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        try:
            load_rfq_input(path)
        except ValueError as exc:
            assert "non-empty" in str(exc)
        else:
            raise AssertionError("empty RFQ collection was accepted")


def test_unsupported_numeric_units_do_not_silently_pass() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_matrix

    matrix = build_matrix(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Rated voltage", "415 psi", "quote p.1", "VERIFIED")],
    )
    assert matrix[0]["status"] == "DEVIATION"


def test_unverified_claim_remains_reviewable_even_with_matching_value() -> None:
    from freellmpool.industrial import Requirement, VendorValue, build_report

    report = build_report(
        [Requirement("R-01", "Rated voltage", "415 V")],
        [VendorValue("Vendor X", "Rated voltage", "415 V", "quote p.1", "UNVERIFIED")],
    )
    assert report["matrix"][0]["status"] == "COMPLIANT"
    assert report["matrix"][0]["claim_status"] == "UNVERIFIED"
    assert report["summary"]["claims_requiring_review"] == 1
