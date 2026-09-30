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
        '{"requirements": [{"tag": "R-01"}], "vendor_data": []}',
        encoding="utf-8",
    )

    try:
        load_rfq_input(path)
    except ValueError as exc:
        assert "non-empty 'vendor_data' array" in str(exc)
    else:
        raise AssertionError("invalid RFQ input was accepted")
