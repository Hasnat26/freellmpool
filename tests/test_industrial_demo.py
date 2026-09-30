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
