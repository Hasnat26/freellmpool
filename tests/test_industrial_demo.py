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

    requirements, vendor_data = load_rfq_input(path)
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
        [CommercialValue("Vendor X", "10000", "USD", "8 weeks", "12 months", "30% advance", "quote p.3")],
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
